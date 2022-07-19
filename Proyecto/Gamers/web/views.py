from django.http import JsonResponse
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
from django.views.decorators.csrf import csrf_exempt

from .forms import GameshipUpdateForm, UserRegisterForm, UserLoginForm, UserUpdateForm, SetPasswordForm, PasswordResetForm, GamerUpdateForm
from .models import Game, Gamer, Gameship, User, Friendship, Clan
from .decorators import user_not_authenticated
from .tokens import account_activation_token

def activate(request, uidb64, token):
    user = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('index')

def activateEmail(request, user, to_email):
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

def index(request):
    """
    Función vista para la página de inicio del sitio.
    """
    num_gamers = Gamer.objects.all().count()
    num_clans = Clan.objects.all().count()

    return render(
        request,
        'index.html',
        context= {'num_gamers': num_gamers, 'num_clans':num_clans},
    )

@user_not_authenticated
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active=False
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('index')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = UserRegisterForm()

    return render(
        request = request,
        template_name = "registration/register.html",
        context={"form":form}
        )

@login_required
def custom_logout(request):
    useri = request.user
    useri.last_online = timezone.now()
    useri.is_online = False
    useri.save(update_fields=['last_online','is_online'])
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("index")

@user_not_authenticated
def custom_login(request):
    if request.method == "POST":
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                useri = request.user
                messages.success(request, f"Hello <b>{user.username}</b>! You have been logged in")
                if Gamer.objects.filter(user=useri).exists() == False:
                    dct = {
                        'user':useri
                    }
                    Gamer.objects.create(**dct)

                return redirect("index")

        else:
            for error in list(form.errors.values()):
                messages.error(request, error) 

    form = UserLoginForm()

    return render(
        request=request,
        template_name="registration/login.html",
        context={"form": form}
        )

def profile(request, username):
    if request.method == "POST" and 'btnform1' in request.POST:
        user = request.user
        gamer = Gamer.objects.filter(user=user).first()
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        form2 = GamerUpdateForm(request.POST, request.FILES, instance=gamer)
        if form.is_valid() and form2.is_valid():
            form2.save()
            user_form = form.save()
            messages.success(request, f'{user_form.username}, Your profile has been updated!')
            return redirect("profile", user_form.username)

        for error in list(form.errors.values()):
            messages.error(request, error)
            return redirect("profile", user.username)

    if request.method == "POST" and 'btnform2' in request.POST:
        user = request.user
        form3 = GameshipUpdateForm(request.POST, request.FILES)
        if form3.is_valid():
            form3.save()
            messages.success(request, f'{user.username}, Your games has been updated!')
            return redirect("profile", user.username)

        for error in list(form3.errors.values()):
            messages.error(request, error)
            return redirect("profile", user.username)

    if request.method == 'POST' and 'btndelete' in request.POST:
        user = get_user_model().objects.filter(username=username).first()
        gamer = Gamer.objects.filter(user=user).first()
        game = Game.objects.filter(game_name=request.POST['gamename']).first()
        Gameship.objects.filter(game=game,gamer=gamer).delete()
        return redirect("profile", request.user.username)

    if request.method == 'POST' and request.POST['action']:
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_ranks':
                game = Game.objects.filter(id=request.POST['game']).first()
                if game.competitive == True:
                    data = dict(Game.GAMES_RANKS)[game.game_name]
                else:
                    data = ''
            else:
                data['error'] = 'Error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)
        
    user = get_user_model().objects.filter(username=username).first()
    gamer = Gamer.objects.filter(user=user).first()
    gameships = Gameship.objects.filter(gamer=gamer).select_related('game')
    games = Game.objects.all()
    if user:
        form = UserUpdateForm(instance=user)
        form2 = GamerUpdateForm(instance=gamer)
        form3 = GameshipUpdateForm()
        return render(
            request = request, 
            template_name='profile.html', 
            context={
                'form': form,
                'form2': form2,
                'form3': form3,
                'gameships': gameships,
                'games': games
            }
            )      

    return redirect("index")

@login_required
def password_change(request):
    user = request.user
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed")
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = SetPasswordForm(user)
    return render(request, 'password_reset_confirm.html', {'form': form})

@user_not_authenticated
def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
            if associated_user:
                subject = "Password Reset request"
                message = render_to_string("template_reset_password.html", {
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

    form = PasswordResetForm()
    return render(
        request=request, 
        template_name="password_reset.html", 
        context={"form": form}
        )

def passwordResetConfirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may go ahead and <b>log in </b> now.")
                return redirect('index')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = SetPasswordForm(user)
        return render(request, 'password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "Link is expired")

    messages.error(request, 'Something went wrong, redirecting back to Homepage')
    return redirect("index")