from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from chat.models import Thread


@login_required
def messages_page(request):
    threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
    context = {
        'Threads': threads
    }
    return render(request, 'chatbox.html', context)
