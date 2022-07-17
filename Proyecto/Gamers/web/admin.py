from django.contrib import admin
from .models import ConnectionHistory, Game, Gamer, Gameship, Friendship, Clan, User
from django.contrib.auth.admin import UserAdmin

class UserAdmin(admin.ModelAdmin):
    fields = [
        'is_superuser',
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_active',
        'date_joined',
        'last_login',
        'birth_date',
        'language',
        'profile_pic',
    ]

admin.site.register(ConnectionHistory)
admin.site.register(User, UserAdmin)
admin.site.register(Game)
admin.site.register(Gamer)
admin.site.register(Gameship)
admin.site.register(Clan)
admin.site.register(Friendship)