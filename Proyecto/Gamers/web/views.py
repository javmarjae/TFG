from itertools import count
from django.shortcuts import render
from .models import Game, Gamer, Gameship, User, Friendship, Clan

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