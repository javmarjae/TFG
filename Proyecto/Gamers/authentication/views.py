from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_http_methods
import web.forms as forms
import web.models as models
from .decorators import user_not_authenticated
from .tokens import account_activation_token

@require_http_methods(["GET", "POST"])
def activate(request, uidb64, token):
    user = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = models.User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,ObjectDoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('index')

def activate_email(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("template_activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear <b>{user}</b>, please go to you email <b>{to_email}</b> inbox and click on \
                received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.')
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')

@require_http_methods(["GET", "POST"])
@user_not_authenticated
def register(request):
    if request.method == 'POST':
        form = forms.UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active=False
            user.save()
            models.Gamer.objects.create(user=user)
            activate_email(request, user, form.cleaned_data.get('email'))
            return redirect('index')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = forms.UserRegisterForm()

    return render(
        request = request,
        template_name = "register.html",
        context={"form":form}
        )

@require_http_methods(["GET", "POST"])
@login_required
def custom_logout(request):
    useri = request.user
    useri.last_online = timezone.now()
    useri.is_online = False
    useri.save(update_fields=['last_online','is_online'])
    request.session['is_logout'] = True
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("index")

@require_http_methods(["GET", "POST"])
@user_not_authenticated
def custom_login(request):
    if request.method == "POST":
        form = forms.UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                useri = request.user
                messages.success(request, f"Hello <b>{user.username}</b>! You have been logged in")
                if models.Gamer.objects.filter(user=useri).exists() == False:
                    dct = {
                        'user':useri
                    }
                    models.Gamer.objects.create(**dct)

                return redirect("index")

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = forms.UserLoginForm()

    return render(
        request=request,
        template_name="login.html",
        context={"form": form}
        )

@require_http_methods(["GET", "POST"])
@login_required
def password_change(request):
    user = request.user
    if request.method == 'POST':
        form = forms.SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed")
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = forms.SetPasswordForm(user)
    return render(request, 'password_reset_confirm.html', {'form': form})

@require_http_methods(["GET", "POST"])
@user_not_authenticated
def password_reset_request(request):
    if request.method == 'POST':
        form = forms.PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
            if associated_user:
                subject = "Password Reset request"
                message = render_to_string("template_password_reset.html", {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, to=[associated_user.email])
                if email.send():
                    messages.success(request,
                        """
                        <h2>Password reset sent</h2><hr>
                        <p>
                            We've emailed you instructions for setting your password, if an account exists with the email you entered.
                            You should receive them shortly.<br>If you don't receive an email, please make sure you've entered the address
                            you registered with, and check your spam folder.
                        </p>
                        """
                    )
                else:
                    messages.error(request, "Problem sending reset password email, <b>SERVER PROBLEM</b>")

            return redirect('index')

    form = forms.PasswordResetForm()
    return render(
        request,
        template_name="password_reset.html",
        context={"form": form}
        )

@require_http_methods(["GET", "POST"])
def password_reset_confirm(request, uidb64, token):
    user = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = user.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,ObjectDoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = forms.SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may go ahead and <b>log in </b> now.")
                return redirect('index')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = forms.SetPasswordForm(user)
        return render(request, 'password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "Link is expired")

    messages.error(request, 'Something went wrong, redirecting back to Homepage')
    return redirect("index")
