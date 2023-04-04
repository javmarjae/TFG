import numpy as np
from django.db.models import Q
from .models import User, Gameship, Friendship, Gamer, UserMatrix
from sklearn.metrics.pairwise import cosine_similarity
from numpy.linalg import norm

def create_user_matrix():
    language_index = {'EN': 0, 'SP': 1, 'FR': 2, 'GE': 3, 'CH': 4}

    for user in User.objects.all():
        # Obtener los juegos, rangos y amigos del usuario
        gamer = Gamer.objects.filter(user=user).first()
        games = set(Gameship.objects.filter(gamer=gamer).values_list('game', flat=True))
        ranks = set(Gameship.objects.filter(gamer=gamer, game__in=games).values_list('rank', flat=True))
        friends = Friendship.objects.filter(Q(sender=gamer, status='ac') | Q(receiver=gamer, status='ac')).values_list('sender', 'receiver')
        num_friends = len(set([f for f in friends]))

        # Crear los datos de la matriz
        birth_year = user.birth_date.year
        language = language_index[user.language]
        games_and_ranks_count = len(games) + len(ranks)

        # Crear la instancia de UserMatrix y guardarla en la base de datos
        matrix_data = {
            'birth_year': birth_year,
            'language': language,
            'games_and_ranks_count': games_and_ranks_count,
            'num_friends': num_friends
        }
        user_matrix = UserMatrix(user=user, birth_year=matrix_data['birth_year'], language=matrix_data['language'], games_and_ranks_count=matrix_data['games_and_ranks_count'], num_friends=matrix_data['num_friends'], similarity_vector='')
        user_matrix.save()

def recommended_users(user):
    top_users = []
    gamer = Gamer.objects.filter(user=user).first()
    users = UserMatrix.objects.exclude(user=user)
    friends = Friendship.objects.filter(Q(sender=gamer, status='ac') | Q(receiver=gamer, status='ac')).values_list('sender__user_id', 'receiver__user_id')
    users = [idx for idx in users if users[idx].user.id not in [user_id for user_id in friends]]

    for u in users:
        top_users = dice_coefficient(u,user)