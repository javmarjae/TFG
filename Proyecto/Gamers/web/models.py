import uuid, os
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import naturaltime


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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30, help_text="Clan name", unique=True)
    description = models.TextField(max_length=300, help_text="Clan description")
    leader = models.CharField(max_length=20, help_text="Clan leader", null=True, blank=True)

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

    discord = models.CharField(max_length=30, help_text="Discord user name", blank=True)
    steam = models.CharField(max_length=30, help_text="Steam user name", blank=True)
    epic_games = models.CharField(max_length=30, help_text="EpicGames user name", blank=True)
    riot_games = models.CharField(max_length=30, help_text="Riot Games user name", blank=True)

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
        unique_together = ('sender','receiver')

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

    GAMES_RANKS = [
        ('un','Unranked'),
        ('CSG', (
        ('s1','Silver I'),
        ('s2','Silver II'),
        ('s3','Silver III'),
        ('s4','Silver IV'),
        ('se','Silver Elite'),
        ('sm','Silver Elite Master'),
        ('g1','Gold Nova I'),
        ('g2','Gold Nova II'),
        ('g3','Gold Nova III'),
        ('gm','Gold Nova Master'),
        ('m1','Master Guardian I'),
        ('m2','Master Guardian II'),
        ('me','Master Guardian Elite'),
        ('dm','Distinguished Master Guardian'),
        ('le','Legendary Eagle'),
        ('lm','Legendary Eagle Master'),
        ('sf','Supreme Master First Class'),
        ('ge','The Global Elite'),
            )
        ),
        ('LOL', (
        ('ir','Iron'),
        ('br','Bronze'),
        ('si','Silver'),
        ('go','Gold'),
        ('pl','Platinum'),
        ('di','Diamond IV'),
        ('ma','Master IV'),
        ('gm','Grand Master'),
        ('ch','Challenger'),
            )
        ),
        ('RLE', (
        ('b1','Bronze I'),
        ('b2','Bronze II'),
        ('b3','Bronze III'),
        ('s1','Silver I'),
        ('s2','Silver II'),
        ('s3','Silver III'),
        ('g1','Gold I'),
        ('g2','Gold II'),
        ('g3','Gold III'),
        ('p1','Platinum I'),
        ('p2','Platinum II'),
        ('p3','Platinum III'),
        ('d1','Diamond I'),
        ('d2','Diamond II'),
        ('d3','Diamond III'),
        ('c1','Champion I'),
        ('c2','Champion II'),
        ('c3','Champion III'),
        ('h1','Grand Champion I'),
        ('h2','Grand Champion II'),
        ('h3','Grand Champion III'),
        ('sl','Supersonic Legend'),
            )
        ),
        ('VAL', (
        ('i1','Iron I'),
        ('i2','Iron II'),
        ('i3','Iron III'),
        ('b1','Bronze I'),
        ('b2','Bronze II'),
        ('b3','Bronze III'),
        ('s1','Silver I'),
        ('s2','Silver II'),
        ('s3','Silver III'),
        ('g1','Gold I'),
        ('g2','Gold II'),
        ('g3','Gold III'),
        ('p1','Platinum I'),
        ('p2','Platinum II'),
        ('p3','Platinum III'),
        ('d1','Diamond I'),
        ('d2','Diamond II'),
        ('d3','Diamond III'),
        ('a1','Ascendent I'),
        ('a2','Ascendent II'),
        ('a3','Ascendent III'),
        ('h1','Inmortal I'),
        ('h2','Inmortal II'),
        ('h3','Inmortal III'),
        ('ra','Radiant'),
            )
        ),
    ]

    rank = models.CharField(max_length=20, choices=GAMES_RANKS, default='un', help_text="Gamer rank in a Game")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, help_text="Game selected")
    gamer = models.ForeignKey(Gamer, on_delete=models.CASCADE, help_text="Gamer that selects a Game")

    def __str__(self) -> str:
        return '%s-%s' % (self.gamer,self.game)
    
    class Meta:
        unique_together = ('game','gamer')
        