from itertools import count
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from web.forms import UserRegisterForm, UserLoginForm
from .models import Game, Gamer, Gameship, User, Friendship, Clan
from .decorators import user_not_authenticated

def index(request):
    """
    Función vista para la página de inicio del sitio.
    """
    num_gamers = Gamer.objects.all().count()
    num_clans = Clan.objects.all().count()
    
    num_gamers_online = Gamer.objects.filter(status__exact = 'on').count()
    num_gamers_playing = Gamer.objects.filter(status__exact = 'pl').count()

    return render(
        request,
        'index.html',
        context= {'num_gamers': num_gamers, 'num_clans':num_clans, 'num_gamers_online':num_gamers_online, 'num_gamers_playing':num_gamers_playing},
    )

@user_not_authenticated
def register(request):
    # Logged in user can't register a new account
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else:
            for error in list(form.errors.values()):
                print(request, error)

    else:
        form = UserRegisterForm()

    return render(
        request = request,
        template_name = "registration/register.html",
        context={"form":form}
        )

@login_required
def custom_logout(request):
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
                messages.success(request, f"Hello <b>{user.username}</b>! You have been logged in")
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