from django.contrib import admin

from .models import User, Game, Gamer, Gameship, Friendship, Clan

admin.site.register(User)
admin.site.register(Game)
admin.site.register(Gamer)
admin.site.register(Gameship)
admin.site.register(Clan)
admin.site.register(Friendship)