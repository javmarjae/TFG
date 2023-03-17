from datetime import datetime
from django.contrib.auth import get_user_model
from Gamers.settings import MEDIA_ROOT
from faker import Faker
from random import randint
from web.models import Clan, Gamer, Friendship, Game, Gameship, User
from django.conf import settings
from django.core.management import call_command
from django.core.files import File
import random, django, os

django.setup()

call_command('flush', '--noinput')

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'root123')

User = get_user_model()
fake = Faker()

fotos_path = os.path.join(MEDIA_ROOT, 'defaultimages')
fotos = os.listdir(fotos_path)

clan_names = ['KOI LOL', 'Pokemon', 'League of Legends', 'World of Warcraft', 'Rocket League', 'Sevillanos', 'Salchicha Team', 'Fortnite', 'Escuadra suicida']
for name in clan_names:
    foto_nombre = random.choice(fotos)
    foto_ruta = os.path.join(fotos_path, foto_nombre)
    clan = Clan.objects.create(
        name=name,
        description=fake.text(max_nb_chars=300),
        leader=fake.name(),
        join_date=fake.date_this_year(before_today=True)
    )
    with open(foto_ruta, 'rb') as f:
        clan.profile_pic.save(foto_nombre, File(f))

clans = Clan.objects.all()

for i in range(20):
    foto_nombre = random.choice(fotos)
    foto_ruta = os.path.join(fotos_path, foto_nombre)
    user = User.objects.create(
        username=fake.user_name(),
        email=fake.email(),
        password='password',
        language=random.choice(User.LANGUAGES)[0],
        birth_date=fake.date_between_dates(date_start=datetime(1990,1,1), date_end=datetime(2005,12,31)),
        is_online=random.choice([True,False])
    )
    with open(foto_ruta, 'rb') as f:
        user.profile_pic.save(foto_nombre, File(f))
    gamer = Gamer.objects.create(
        user=user,
        discord=fake.user_name(),
        steam=fake.user_name(),
        epic_games=fake.user_name(),
        riot_games=fake.user_name(),
        clan=clans[randint(0, clans.count()-1)] if clans.exists() else None
    )

gamers = Gamer.objects.all()

for clan in Clan.objects.all():
    members = Gamer.objects.filter(clan=clan)
    if members.exists():
        leader = random.choice(members)
        clan.leader = leader.user.username
    else:
        other_clans = Clan.objects.exclude(id=clan.id)
        if other_clans.exists():
            other_members = Gamer.objects.filter(clan__in=other_clans)
            if other_members.exists():
                leader = random.choice(other_members)
                clan.leader = leader.user.username
        else:
            clan.leader = None
    clan.save()

for gamer in gamers:
    for i in range(random.randint(2, 5)):
        friend = random.choice(gamers)
        while friend == gamer or Friendship.objects.filter(sender=gamer, receiver=friend).exists() or Friendship.objects.filter(sender=friend, receiver=gamer).exists():
            friend = random.choice(gamers)
        if Friendship.FRIENSHIP_STATUS:
            stat = random.choice(Friendship.FRIENSHIP_STATUS)[0]
        else:
            stat = None
        Friendship.objects.create(sender=gamer, receiver=friend, status=stat)

for gamename in Game.GAMES:
    is_competitive = False
    ranks = [tupla for tupla in Game.GAMES_RANKS if tupla[0] == gamename[0]]
    if ranks: is_competitive = True
    Game.objects.create(game_name=gamename[0],competitive=is_competitive)

for gamer in gamers:
    num_games = random.randint(1, len(Game.objects.all())) # Número aleatorio de juegos a asignar
    unassigned_games = list(Game.objects.exclude(gameship__gamer=gamer)) # Juegos que aún no se han asignado a este jugador
    if len(unassigned_games) < num_games:
        raise Exception('No hay suficientes juegos disponibles para asignar al jugador')
    games = random.sample(unassigned_games, num_games) # Juegos aleatorios que se asignarán
    for game in games:
        if game.competitive:
            for gameranks in Game.GAMES_RANKS:
                if gameranks[0] == game.game_name:
                    ranks = gameranks[1]
            rank = random.choice(ranks)[0]
            print(rank)
        else:
            rank = None
        Gameship.objects.create(game=game, gamer=gamer, rank=rank)

