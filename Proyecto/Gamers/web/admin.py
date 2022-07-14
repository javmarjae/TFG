from django.contrib import admin
from .models import Game, Gamer, Gameship, Friendship, Clan, User
from django.contrib.auth.admin import UserAdmin

admin.site.register(User, UserAdmin)
admin.site.register(Game)
admin.site.register(Gamer)
admin.site.register(Gameship)
admin.site.register(Clan)
admin.site.register(Friendship)