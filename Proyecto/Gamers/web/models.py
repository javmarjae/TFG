import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Modelo que representa cada usuario.
    """

    LANGUAGES = (
        ('EN','English'),
        ('SP','Spanish'),
        ('FR','French'),
        ('GE','German'),
        ('CH','Chinese')
    )

    language = models.CharField(max_length=2, choices=LANGUAGES, default='SP', help_text="Language")
    profile_pic = models.ImageField(upload_to='img/profile', default = 'img/profile/default.png', null=True, blank=True, help_text="Profile pic")
    birth_date = models.DateField(null=True, blank=True, help_text="Birth date")

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
        ('i4','Iron IV'),
        ('i3','Iron III'),
        ('i2','Iron II'),
        ('i1','Iron I'),
        ('b4','Bronze IV'),
        ('b3','Bronze III'),
        ('b2','Bronze II'),
        ('b1','Bronze I'),
        ('s4','Silver IV'),
        ('s3','Silver III'),
        ('s2','Silver II'),
        ('s1','Silver I'),
        ('g4','Gold IV'),
        ('g3','Gold III'),
        ('g2','Gold II'),
        ('g1','Gold I'),
        ('p4','Platinum IV'),
        ('p3','Platinum III'),
        ('p2','Platinum II'),
        ('p1','Platinum I'),
        ('d4','Diamond IV'),
        ('d3','Diamond III'),
        ('d2','Diamond II'),
        ('d1','Diamond I'),
        ('m4','Master IV'),
        ('m3','Master III'),
        ('m2','Master II'),
        ('m1','Master I'),
        ('h4','Grand Master IV'),
        ('h3','Grand Master III'),
        ('h2','Grand Master II'),
        ('h1','Grand Master I'),
        ('ch','Challenger'),
            )
        ),
        ('Rocket League', (
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
        ('Valorant', (
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
        ('c1','Ascendent I'),
        ('c2','Ascendent II'),
        ('c3','Ascendent III'),
        ('h1','Inmortal I'),
        ('h2','Inmortal II'),
        ('h3','Inmortal III'),
        ('rl','Radiant'),
            )
        ),
    )

    rank = models.CharField(max_length=20, choices=GAMES_RANKS, default='un', help_text="Gamer rank in a Game")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, help_text="Game selected")
    gamer = models.ForeignKey(Gamer, on_delete=models.CASCADE, help_text="Gamer that selects a Game")

    def __str__(self) -> str:
        return '%s-%s' % (self.gamer,self.game)
    
    class Meta:
        unique_together = ('game','gamer')
        