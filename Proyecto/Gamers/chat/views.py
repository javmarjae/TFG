from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from chat.models import Thread


@login_required(login_url='login')
def messages_page(request):

    campo_texto = request.GET.get('busqueda')

    threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')

    if campo_texto:
        threads = threads.filter(Q(first_person__username__icontains=campo_texto) | Q(second_person__username__icontains=campo_texto))

    context = {
        'Threads': threads
    }
    return render(request, 'chatbox.html', context)
