from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import User, Friendship, Gameship, Gamer, Clan
import Levenshtein

User = get_user_model()

def jaccard_similarity(user):

    user_gamer = Gamer.objects.filter(user=user).first()

    similarity_dict = {}

    friends = set([friendship.receiver.user if friendship.sender == user_gamer else friendship.sender.user for friendship 
                   in Friendship.objects.filter(Q(sender=user_gamer)|Q(receiver=user_gamer),status='ac')])

    all_users = User.objects.exclude(Q(id=user.id) | Q(is_active=False)).exclude(id__in = [friend.id for friend in friends])

    user_gameships = Gameship.objects.filter(gamer=user_gamer)

    user_games = set(user_gameships.values_list('game__game_name', flat=True))

    user_rank = {game: rank for game, rank in user_gameships.values_list('game', 'rank')}

    user_clan = user_gamer.clan

    for other_user in all_users:
        u_gamer = Gamer.objects.filter(user=other_user).first()
        u_friends = set([friendship.receiver.user if friendship.sender == u_gamer else friendship.sender.user for friendship 
                   in Friendship.objects.filter(Q(sender=u_gamer)|Q(receiver=u_gamer),status='ac')])
        
        if user.language == other_user.language:
            lang_similarity = 1
        else:
            lang_similarity = 0
        
        common_friends = friends.intersection(u_friends)

        if not friends or not u_friends:
            friend_similarity = 1
        else:
            friend_similarity = len(common_friends) / (len(friends) + len(u_friends) - len(common_friends))

        u_gameships = Gameship.objects.filter(gamer=u_gamer)

        u_games = u_gameships.values_list('game__game_name', flat=True).distinct()

        if not user_games or not u_games:
            game_similarity = 1
        else:
            game_similarity = len(user_games.intersection(u_games)) / len(user_games.union(u_games))
            
        u_rank = {game: rank for game, rank in u_gameships.values_list('game', 'rank')}

        if not user_rank or not u_rank:
            rank_similarity = 1
        else:
            rank_diffs = [Levenshtein.distance(user_rank.get(game, ''), u_rank.get(game, '')) for game in user_games.union(u_games)]
            rank_similarity = 1 - sum(rank_diffs) / (len(user_games.union(u_games)) * 4)

        if user.birth_date and other_user.birth_date:
            age_diff = abs((user.birth_date - other_user.birth_date).days) / 365
            age_similarity = 1 - min(age_diff / 10, 1)
        else:
            age_similarity = 1

        u_clan = u_gamer.clan

        if not user_clan or not u_clan:
            clan_similarity = 0
        else:
            if user_clan == u_clan:
                clan_similarity = 1
            else:
                clan_diff = Levenshtein.distance(user_clan.name, u_clan.name)
                clan_similarity = 1 - clan_diff

        similarity = (lang_similarity * 5 + friend_similarity * 1 + game_similarity * 2.5 + rank_similarity * 4 + age_similarity * 3 + clan_similarity * 0.5) / 6

        similarity_dict[other_user] = similarity

    sorted_users = sorted(similarity_dict.items(), key=lambda x: x[1], reverse=True)

    return sorted_users   
