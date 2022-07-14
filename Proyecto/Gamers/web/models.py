from tkinter import CASCADE
import uuid
from xmlrpc.client import TRANSPORT_ERROR
from django.db import models
from django.dispatch import receiver


class User(models.Model):
    """
    Modelo que representa cada usuario.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, help_text="Name")
    last_name = models.CharField(max_length=40, help_text="Last name")
    user_name = models.CharField(max_length=20, help_text="User name", unique=True)
    email = models.EmailField(max_length=30 ,help_text="Email", unique=True)
    password = models.CharField(max_length=30, help_text="Password")

    LANGUAGES = (
        ('EN','English'),
        ('SP','Spanish'),
        ('FR','French'),
        ('GE','German'),
        ('CH','Chinese')
    )

    language = models.CharField(max_length=2, choices=LANGUAGES, default='SP', help_text="Language")
    profile_pic = models.ImageField(upload_to='img/profile', help_text="Profile pic")
    birth_date = models.DateField(help_text="Birth date")

    ROLES = (
        ('ad','Admin'),
        ('us','User')
    )

    role = models.CharField(max_length=2, choices=ROLES, default='us', help_text="Role privileges")

    def __str__(self) -> str:
        """
        String para representar el objeto del modelo
        """
        return '%s' % self.user_name

class Clan(models.Model):
    """
    Modelo que representa cada Clan.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30, help_text="Clan name", unique=True)
    description = models.TextField(max_length=300, help_text="Clan description")
    num_members = models.IntegerField(help_text="Number of members")

    def __str__(self) -> str:
        return '%s' % self.name

class Gamer(models.Model):
    """
    Modelo que representa cada Gamer asociado a un User.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )

    discord = models.CharField(max_length=30, help_text="Discord user name", blank=True)
    steam = models.CharField(max_length=30, help_text="Steam user name", blank=True)
    epic_games = models.CharField(max_length=30, help_text="EpicGames user name", blank=True)
    riot_games = models.CharField(max_length=30, help_text="Riot Games user name", blank=True)

    GAMER_STATUS = (
        ('on','Online'),
        ('of','Offline'),
        ('pl','Playing')
    )

    status = models.CharField(max_length=2, choices=GAMER_STATUS, default='of', help_text="Gamer status")
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

    GAMES_RANKS = (
        ('un','Unranked'),
        ('CS:GO', (
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
        ('sm','Supreme Master First Class'),
        ('ge','The Global Elite'),
            )
        ),
        ('League of Legends', (
        ('ir','Iron'),
        ('br','Bronze'),
        ('si','Silver'),
        ('go','Gold'),
        ('pl','Platinum'),
        ('di','Diamond'),
        ('ma','Master'),
        ('gm','Grand Master'),
        ('ch','Challenger'),
            )
        ),
        ('Rocket League', (
        ('br','Bronze'),
        ('si','Silver'),
        ('go','Gold'),
        ('pl','Platinum'),
        ('di','Diamond'),
        ('ch','Champion'),
        ('gc','Grand Champion'),
        ('le','Supersonic Legend'),
            )
        ),
        ('Valorant', (
        ('ir','Iron'),
        ('br','Bronze'),
        ('si','Silver'),
        ('go','Gold'),
        ('pl','Platinum'),
        ('di','Diamond'),
        ('as','Ascendent'),
        ('in','Inmortal'),
        ('ra','Radiant'),
            )
        ),
    )

    rank = models.CharField(max_length=20, choices=GAMES_RANKS, default='un', help_text="Gamer rank in a Game")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, help_text="Game selected")
    gamer = models.ForeignKey(Gamer, on_delete=models.CASCADE, help_text="Gamer that selects a Game")
    
    class Meta:
        unique_together = ('game','gamer')
        