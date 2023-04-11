from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.db.models.functions import Lower
from django.core.paginator import Paginator
from unidecode import unidecode

from .forms import ClanUpdateForm, GamerClanUpdateForm, GameshipUpdateForm, UserUpdateForm, GamerUpdateForm
from .models import Game, Gamer, Gameship, User, Friendship, Clan
from chat.models import Thread

def index(request):
    """
    Función vista para la página de inicio del sitio.
    """
    user = request.user
    users = User.objects.all().exclude(id=user.id)[:10]
    clans = Clan.objects.all()[:10]

    return render(
        request,
        'index.html',
        context= {
            'users': [(u,Gamer.objects.filter(user=u),Gameship.objects.filter(gamer=Gamer.objects.filter(user=u).first()).count()) for u in users],
            'clans':[(c,Gamer.objects.filter(clan=c).count()) for c in clans]
        },
    )

@login_required
def users(request):
    user = request.user
    users = User.objects.all().exclude(id=user.id)

    campo_texto = request.GET.get('busqueda')
    languages = User.LANGUAGES
    selected_languages = request.GET.getlist('languages')
    games = Game.GAMES
    selected_games = request.GET.getlist('games')
    ranks =[
        ('CS:GO', ['Silver I', 'Silver II', 'Silver III', 'Silver IV', 'Silver Elite', 'Silver Elite Master', 'Gold Nova I', 'Gold Nova II','Gold Nova III',
            'Gold Nova Master', 'Master Guardian I', 'Master Guardian II', 'Master Guardian Elite', 'Distinguished Master Guardian', 'Legendary Eagle',
            'Legendary Eagle Master', 'Supreme Master First Class', 'The Global Elite']),
        ('League of Legends', ['Iron IV','Iron III','Iron II','Iron I','Bronze IV','Bronze III','Bronze II','Bronze I','Silver IV','Silver III','Silver II',
            'Silver I','Gold IV','Gold III','Gold II','Gold I','Platinum IV','Platinum III','Platinum II','Platinum I','Diamond IV','Diamond III',
            'Diamond II','Diamond I','Master IV','Master III','Master II','Master I','Grand Master IV','Grand Master III','Grand Master II',
            'Grand Master I','Challenger']),
        ('Rocket League', ['Bronze I','Bronze II','Bronze III','Silver I','Silver II','Silver III','Gold I','Gold II','Gold III','Platinum I','Platinum II',
            'Platinum III','Diamond I','Diamond II','Diamond III','Champion I','Champion II','Champion III','Grand Champion I','Grand Champion II',
            'Grand Champion III','Supersonic Legend']),
        ('Valorant', ['Iron I','Iron II','Iron III','Bronze I','Bronze II','Bronze III','Silver I','Silver II','Silver III','Gold I','Gold II','Gold III',
            'Platinum I','Platinum II','Platinum III','Diamon I','Diamond II','Diamond III','Ascendent I','Ascendent II','Ascendent III','Inmortal I',
            'Inmortal II','Inmortal III','Radiant'])]
    selected_ranks = request.GET.getlist('ranks')

    if selected_games:
        gamer_ids = Gameship.objects.filter(game__game_name__in=selected_games).select_related('gamer').values_list('gamer_id',flat=True).distinct()
        users = users.filter(id__in=gamer_ids)

    if selected_ranks:
        gamer_ids = Gameship.objects.filter(rank__in=selected_ranks).select_related('gamer').values_list('gamer_id',flat=True).distinct()
        users = users.filter(id__in=gamer_ids)

    if selected_languages:
        users = users.filter(language__in=selected_languages)

    if campo_texto:
        users = users.annotate(username_m=Lower('username')).filter(username_m__icontains=unidecode(campo_texto.lower()))

    paginator = Paginator(users,20)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)
    users = page_object.object_list

    if 'restart' in request.GET:
        campo_texto = ''
        selected_languages = []
        selected_games = []
        selected_ranks = []

    return render(
        request,
        'users.html',
        context= {
            'users': [(u,Gamer.objects.filter(user=u),Gameship.objects.filter(gamer=Gamer.objects.filter(user=u).first()).count()) for u in users],
            'page': page_object,
            'languages':languages,
            'selected_languages':selected_languages,
            'busqueda':campo_texto,
            'games':games,
            'selected_games':selected_games,
            'ranks':ranks,
            'selected_ranks':selected_ranks
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
            request,
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

    campo_texto = request.GET.get('busqueda')
    min_miembros = request.GET.get('minimo')
    max_miembros = request.GET.get('maximo')
    orden_fecha = request.GET.get('ordenfecha')
    orden_miembros = request.GET.get('ordenmiembros')

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
        
    clans = clans.annotate(num_members=Count('Clan')) #Clan es el related_name que tiene la clase Gamer en el atributo clan

    menos_miembros = clans.order_by('num_members').first()
    mas_miembros = clans.order_by('-num_members').first()

    if min_miembros:
        clans = clans.exclude(num_members__lte=min_miembros)

    if max_miembros:
        clans = clans.exclude(num_members__gte=max_miembros)

    if orden_fecha:
        if orden_fecha=='fecharec':
            clans = clans.order_by('-join_date')
        elif orden_fecha=='fechaant':
            clans = clans.order_by('join_date')
        else:
            clans = clans.order_by('id')

    if orden_miembros:
        if orden_miembros=='maymiem':
            clans = clans.order_by('-num_members')
        elif orden_miembros=='menmiem':
            clans = clans.order_by('num_members')
        else:
            clans = clans.order_by('id')


    if campo_texto:
        clans = clans.annotate(name_m=Lower('name')).filter(name_m__icontains=unidecode(request.POST.get('busqueda').lower()))

    if 'restart' in request.GET:
        campo_texto = ''
        min_miembros = ''
        max_miembros = ''
        orden_fecha = ''
        orden_miembros = ''
        clans = clans.order_by('id')

    form1 = ClanUpdateForm()
    return render(
        request,
        'clans.html',
        context={
            'clans':[(c,Gamer.objects.filter(clan=c).count()) for c in clans],
            'gamer':gamer,
            'form1':form1,
            'masmiembros':mas_miembros.num_members,
            'menosmiembros':menos_miembros.num_members,
            'busqueda':campo_texto,
            'min_miembros':min_miembros,
            'max_miembros':max_miembros,
            'orden_fecha':orden_fecha,
            'orden_miembros':orden_miembros
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
        
    if 'busqueda' in request.POST:
        members = members.annotate(name_m=Lower('user__username')).filter(name_m__icontains=unidecode(request.POST.get('busqueda').lower()))

    if clan:
        form1 = GamerClanUpdateForm(instance=gamer)
        form2 = ClanUpdateForm(instance=clan)
        return render(
            request,
            'clanprofile.html',
            context={
                'clan':clan,
                'members':[(m,Gameship.objects.filter(gamer=m).count()) for m in members],
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
        if not Thread.objects.filter(Q(first_person=friendship.sender.user) & Q(second_person=friendship.receiver.user) | Q(first_person=friendship.receiver.user) & Q(second_person=friendship.sender.user)):
            Thread.objects.create(first_person=friendship.sender.user,second_person=friendship.receiver.user)
    if request.method == 'POST' and 'decline' in request.POST:
        friendshipid = request.POST['solicitud']
        friendship = Friendship.objects.filter(id=friendshipid).first()
        friendship.status = 'de'
        friendship.save()
    if request.method == 'POST' and 'remove' in request.POST:
        friendshipid = request.POST['solicitud']
        friendship = Friendship.objects.filter(id=friendshipid).first()
        Thread.objects.filter(Q(first_person=friendship.sender.user) & Q(second_person=friendship.receiver.user) | Q(first_person=friendship.receiver.user) & Q(second_person=friendship.sender.user)).first().delete()
        friendship.delete()

    solicitudes = Friendship.objects.filter(receiver=Gamer.objects.filter(user=request.user).first(), status='pe') or None
    amigos = Friendship.objects.filter(receiver=Gamer.objects.filter(user=request.user).first(), status='ac') or Friendship.objects.filter(sender=Gamer.objects.filter(user=request.user).first(), status='ac')
    
    return render(request,'friends.html',context={'solicitudes':solicitudes,'amigos':amigos})