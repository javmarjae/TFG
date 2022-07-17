import json

from .models import ConnectionHistory
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


@database_sync_to_async
def update_user_status(self, user, status):
    return ConnectionHistory.objects.get_or_create(
        user=user,
    ).update(status=status)