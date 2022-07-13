from xmlrpc.client import TRANSPORT_ERROR
from django.db import models
from django.dispatch import receiver


class User(models.Model):
    """
    Modelo que representa cada usuario.
    """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=20, help_text="Name.")
    last_name = models.CharField(max_length=40, help_text="Last name.")
    user_name = models.CharField(max_length=20, help_text="User name.", unique=True)
    email = models.EmailField(max_length=30 ,help_text="Email.", unique=True)
    password = models.CharField(max_length=30, help_text="Password.")

    LANGUAGES = (
        ('EN','English'),
        ('SP','Spanish'),
        ('FR','French'),
        ('GE','German'),
        ('CH','Chinese')
    )

    language = models.CharField(max_length=2, choices=LANGUAGES, default='SP', help_text="Language.")
    profile_pic = models.ImageField(upload_to=None, help_text="Profile pic.")
    birth_date = models.DateField(help_text="Birth date.")

    ROLES = (
        ('ad','Admin'),
        ('us','User')
    )

    role = models.CharField(max_length=2, choices=ROLES, default='us', help_text="Role privileges.")

    def __str__(self):
        """
        String para representar el objeto del modelo
        """
        return '%s' % self.user_name

class Gamer(models.Model):
    """
    Modelo que representa cada Gamer asociado a un User.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )

    discord = models.CharField(max_length=30, help_text="Discord user name.", blank=True)
    steam = models.CharField(max_length=30, help_text="Steam user name.", blank=True)
    epic_games = models.CharField(max_length=30, help_text="EpicGames user name.", blank=True)
    riot_games = models.CharField(max_length=30, help_text="Riot Games user name.", blank=True)

    GAMER_STATUS = (
        ('on','Online'),
        ('of','Offline'),
        ('pl','Playing')
    )

    status = models.CharField(max_length=2, choices=GAMER_STATUS, default='off', help_text="Gamer status.")

    def __str__(self):
        """
        String para representar el objeto del modelo
        """
        return '%s' % self.user

class Friendship(models.Model):
    """
    Modelo que representa cada solicitud de amistad de un Gamer.
    """
    id = models.BigAutoField(primary_key=True)
    sender = models.ForeignKey(Gamer, on_delete=models.CASCADE, related_name="Friend request sender.")
    receiver = models.ForeignKey(Gamer, on_delete=models.CASCADE, related_name="Friend request receiver.")

    FRIENSHIP_STATUS = (
        ('ac','Accepted'),
        ('de','Declined'),
        ('pe','Pending')
    )

    status = models.CharField(max_length=2, choices=FRIENSHIP_STATUS, default='pe', help_text="Friendship request status.")

