from datetime import datetime
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

from .forms import ClanCreateForm, ClanUpdateForm, GamerClanUpdateForm, GameshipUpdateForm, UserRegisterForm, UserLoginForm, UserUpdateForm, SetPasswordForm, PasswordResetForm, GamerUpdateForm
from .models import Game, Gamer, Gameship, User, Friendship, Clan
from chat.models import Thread

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
        context= {
            'users': [(u,Gamer.objects.filter(user=u),Gameship.objects.filter(gamer=Gamer.objects.filter(user=u).first()).count()) for u in users], 
            'clans':[(c,Gamer.objects.filter(clan=c).count()) for c in clans]
        },
    )

@login_required(login_url='login')
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

    if request.method == 'POST' and 'btnfriendrequest' in request.POST:
        usersender = request.user
        sender = Gamer.objects.filter(user=usersender).first()
        user = get_user_model().objects.filter(username=username).first()
        receiver = Gamer.objects.filter(user=user).first()

        friendship = Friendship.objects.filter(sender=sender,receiver=receiver).first() or Friendship.objects.filter(sender=receiver,receiver=sender).first()
        if friendship:
            if friendship.status == 'pe':
                messages.error(request,'Friend request already sent!')
            elif friendship.status == 'ac':
                messages.warning(request,'You are already friends!')
            else:
                friendship.status = 'pe'
                friendship.save()
                messages.success(request,'Friend request sent!')
        else:
            Friendship.objects.create(sender=sender,receiver=receiver)
            messages.success(request,'Friend request sent!')
        return redirect("profile", user.username)

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
    clan = Clan.objects.filter(name=gamer.clan).first() or None
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
                'games': games,
                'gamer': gamer,
                'gamerclan':clan
            }
            )      

    return redirect("index")

@login_required(login_url='login')
def clans(request):
    gamer = Gamer.objects.filter(user=request.user).first()
    clans = Clan.objects.all()
    if request.method == 'POST' and 'btnform2' in request.POST:
        form1 = ClanUpdateForm(request.POST, request.FILES)
        if form1.is_valid():
            clan_form = form1.save()
            gamer.clan = Clan.objects.filter(name=clan_form.name).first()
            gamer.save()
            messages.success(request, f'You have created this clan!')
            return redirect("clan", clan_form.name)

        for error in list(form1.errors.values()):
            messages.error(request, error)
            return redirect("clans")

    form1 = ClanUpdateForm()
    return render(
        request,
        'clans.html',
        context={
            'clans':[(c,Gamer.objects.filter(clan=c).count()) for c in clans],
            'gamer':gamer,
            'form1':form1,
        }
    )

@login_required(login_url='login')
def clanprofile(request, name):
    gamer = Gamer.objects.filter(user=request.user).first()
    clan = Clan.objects.filter(name=name).first()
    members = Gamer.objects.filter(clan=clan).select_related('user')
    if request.method == 'POST' and 'joinclan' in request.POST:
        form1 = GamerClanUpdateForm(request.POST, request.FILES, instance=gamer)
        if form1.is_valid():
            form1.save()
            messages.success(request, f'You have joined this clan!')
            return redirect("clan", name)

        for error in list(form1.errors.values()):
            messages.error(request, error)
            return redirect("clan", name)
    
    if request.method == 'POST' and 'exitclan' in request.POST:
        form1 = GamerClanUpdateForm(request.POST, request.FILES, instance=gamer)
        if form1.is_valid():
            form1.save()
            messages.success(request, f'You have abandoned this clan!')
            members = Gamer.objects.filter(clan=clan).select_related('user')
            if members.count() <= 0:
                clan.delete()
            else:
                if clan.leader == request.user.username:
                    clan.leader = members[1].user.username
            return redirect("clans")

        for error in list(form1.errors.values()):
            messages.error(request, error)
            return redirect("clan", name)

    if request.method == 'POST' and 'btnform2' in request.POST:
        form2 = ClanUpdateForm(request.POST, request.FILES, instance=clan)
        if form2.is_valid():
            clan_form = form2.save()
            messages.success(request, f'You have edited this clan!')
            return redirect("clan", clan_form.name)

        for error in list(form2.errors.values()):
            messages.error(request, error)
            return redirect("clan", name)

    if clan:
        form1 = GamerClanUpdateForm(instance=gamer)
        form2 = ClanUpdateForm(instance=clan)
        return render(
            request,
            'clanprofile.html',
            context={
                'clan':clan, 
                'members':members, 
                'gamer':gamer,
                'form1':form1,
                'form2':form2
            }
            )

    return redirect("index")

@login_required(login_url='login')
def friends(request):
    if request.method == 'POST' and 'accept' in request.POST:
        friendshipid = request.POST['solicitud']
        friendship = Friendship.objects.filter(id=friendshipid).first()
        friendship.status = 'ac'
        friendship.save()
        Thread.objects.create(first_person=friendship.sender.user,second_person=friendship.receiver.user)
    if request.method == 'POST' and 'decline' in request.POST:
        friendshipid = request.POST['solicitud']
        friendship = Friendship.objects.filter(id=friendshipid).first()
        friendship.status = 'de'
        friendship.save()
    if request.method == 'POST' and 'remove' in request.POST:
        friendshipid = request.POST['solicitud']
        friendship = Friendship.objects.filter(id=friendshipid).first().delete()

    solicitudes = Friendship.objects.filter(receiver=Gamer.objects.filter(user=request.user).first(), status='pe') or None
    amigos = Friendship.objects.filter(receiver=Gamer.objects.filter(user=request.user).first(), status='ac') or Friendship.objects.filter(sender=Gamer.objects.filter(user=request.user).first(), status='ac')
    
    return render(request,'friends.html',context={'solicitudes':solicitudes,'amigos':amigos})