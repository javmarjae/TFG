from unicodedata import name
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

def index(request):
    """
    Función vista para la página de inicio del sitio.
    """
    user = request.user
    users = User.objects.exclude(username = user)
    clans = Clan.objects.all()

    return render(
        request,
        'index.html',
        context= {'users': users, 'clans':clans},
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

def clans(request):
    clans = Clan.objects.all()
    return render(request,'clans.html',context={'clans':clans})

def clanprofile(request, name):
    clan = Clan.objects.filter(name=name).first()
    return render(request,'clanprofile.html',context={'clan':clan})