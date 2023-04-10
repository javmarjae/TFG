from datetime import datetime
import uuid, os
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from model_utils import Choices


class User(AbstractUser):
    """
    Modelo que representa cada usuario.
    """

    def image_upload_to(self, instance=None):
        if instance:
            return os.path.join("Users", self.username, instance)
        return None

    LANGUAGES = (
        ('EN','English'),
        ('SP','Spanish'),
        ('FR','French'),
        ('GE','German'),
        ('CH','Chinese')
    )

    language = models.CharField(max_length=2, choices=LANGUAGES, default='SP', help_text="Language")
    profile_pic = models.ImageField(upload_to=image_upload_to, default = 'profile/default.png', null=True, blank=True, help_text="Profile pic")
    birth_date = models.DateField(null=True, blank=True, help_text="Birth date")
    last_online = models.DateTimeField(blank=True, null=True)
    is_online = models.BooleanField(default=False)


class Clan(models.Model):
    """
    Modelo que representa cada Clan.
    """
    def image_upload_to(self, instance=None):
        if instance:
            return os.path.join("Clans", self.name, instance)
        return None

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30, help_text="Clan name", unique=True)
    description = models.TextField(max_length=300, help_text="Clan description")
    leader = models.CharField(max_length=20, help_text="Clan leader", null=True, blank=True)
    profile_pic = models.ImageField(upload_to=image_upload_to, default = 'profile/default.png', null=True, blank=True, help_text="Clan pic")
    join_date = models.DateField(default=datetime.now, blank=False, null=False)

    def __str__(self) -> str:
        return '%s' % self.name

class Gamer(models.Model):
    """
    Modelo que representa cada Gamer asociado a un User.
    """
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="Usuario"
    )

    discord = models.CharField(max_length=30, help_text="Discord user name", blank=True, null=True)
    steam = models.CharField(max_length=30, help_text="Steam user name", blank=True, null=True)
    epic_games = models.CharField(max_length=30, help_text="EpicGames user name", blank=True, null=True)
    riot_games = models.CharField(max_length=30, help_text="Riot Games user name", blank=True, null=True)

    clan = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name="Clan", blank=True, null=True)

    def __str__(self):
        """
        String para representar el objeto del modelo
        """
        return '%s' % self.user

class Friendship(models.Model):
    """
    Modelo que representa cada solicitud de amistad de un Gamer.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(Gamer, on_delete=models.CASCADE, related_name="Sender")
    receiver = models.ForeignKey(Gamer, on_delete=models.CASCADE, related_name="Receiver")

    FRIENSHIP_STATUS = (
        ('ac','Accepted'),
        ('de','Declined'),
        ('pe','Pending')
    )

    status = models.CharField(max_length=2, choices=FRIENSHIP_STATUS, default='pe', help_text="Friendship request status")

    def __str__(self) -> str:
        return '%s-%s' % (self.sender,self.receiver)

    class Meta:
        unique_together = ['sender','receiver']

class Game(models.Model):
    """
    Modelo que representa cada Game.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    GAMES = (
        ('LOL','League of Legends'),
        ('RLE','Rocket League'),
        ('VAL','Valorant'),
        ('CSG','CS:GO'),
        ('FIF','FIFA'),
        ('FOR','Fortnite'),
        ('WOW','World of Warcraft')
    )

    GAMES_RANKS = Choices(
        ('un',['Unranked']),
        ('CSG', ['Silver I', 'Silver II', 'Silver III', 'Silver IV', 'Silver Elite', 'Silver Elite Master', 'Gold Nova I', 'Gold Nova II','Gold Nova III',
            'Gold Nova Master', 'Master Guardian I', 'Master Guardian II', 'Master Guardian Elite', 'Distinguished Master Guardian', 'Legendary Eagle',
            'Legendary Eagle Master', 'Supreme Master First Class', 'The Global Elite']),
        ('LOL', ['Iron IV','Iron III','Iron II','Iron I','Bronze IV','Bronze III','Bronze II','Bronze I','Silver IV','Silver III','Silver II',
            'Silver I','Gold IV','Gold III','Gold II','Gold I','Platinum IV','Platinum III','Platinum II','Platinum I','Diamond IV','Diamond III',
            'Diamond II','Diamond I','Master IV','Master III','Master II','Master I','Grand Master IV','Grand Master III','Grand Master II',
            'Grand Master I','Challenger']),
        ('RLE', ['Bronze I','Bronze II','Bronze III','Silver I','Silver II','Silver III','Gold I','Gold II','Gold III','Platinum I','Platinum II',
            'Platinum III','Diamond I','Diamond II','Diamond III','Champion I','Champion II','Champion III','Grand Champion I','Grand Champion II',
            'Grand Champion III','Supersonic Legend']),
        ('VAL', ['Iron I','Iron II','Iron III','Bronze I','Bronze II','Bronze III','Silver I','Silver II','Silver III','Gold I','Gold II','Gold III',
            'Platinum I','Platinum II','Platinum III','Diamon I','Diamond II','Diamond III','Ascendent I','Ascendent II','Ascendent III','Inmortal I',
            'Inmortal II','Inmortal III','Radiant']),
    )

    game_name = models.CharField(max_length=3, choices=GAMES, help_text="Games to choose")
    competitive = models.BooleanField(default=True, help_text="A game has competitive ranking or not")

    def __str__(self) -> str:
        """
        String para representar el objeto del modelo
        """
        return '%s' % self.game_name

class Gameship(models.Model):
    """
    Modelo que representa cada unión de un Gamer con un Game.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    rank = models.CharField(max_length=100, blank=True, null=True, help_text="Gamer rank in a Game")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, help_text="Game selected")
    gamer = models.ForeignKey(Gamer, on_delete=models.CASCADE, help_text="Gamer that selects a Game")

    def __str__(self) -> str:
        return '%s-%s' % (self.gamer,self.game)

    class Meta:
        unique_together = ('game','gamer')

class UserMatrix(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    birth_year = models.IntegerField()
    language = models.CharField(max_length=2)
    games_and_ranks_count = models.IntegerField()
    num_friends = models.IntegerField()
    similarity_vector = models.TextField()

    def __str__(self):
        """
        String para representar el objeto del modelo
        """
        return '%s' % self.user