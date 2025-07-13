
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .forms import EventForm, InvitationForm
from .models import Event, Invitation, User


def event_list(request):
    user = request.user
    events = Event.objects.filter(
        Q(organizer=user) | Q(invitations__guest=user)
    ).distinct().order_by('-start_time')

    my_organized_events = Event.objects.filter(organizer=user).order_by('-start_time')
    my_invited_events = Event.objects.filter(invitations__guest=user).distinct().order_by('-start_time')

    context = {
        'events': events,
        'my_organized_events': my_organized_events,
        'my_invited_events': my_invited_events,
    }
    return render(request, 'event_list.html', context)


def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, "Подію успішно створено!")
            return redirect('event_planner:event_list')
        else:
            messages.error(request, "Не вдалося створити подію. Будь ласка, перевірте форму.")
    else:
        form = EventForm()
    return render(request, 'event_form.html', {'form': form})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user != event.organizer and not event.invitations.filter(guest=request.user).exists():
        messages.error(request, "У вас немає доступу до цієї події.")
        return redirect('event_planner:event_list')

    invitations = event.invitations.all().order_by('guest__username')
    is_organizer = (request.user == event.organizer)
    is_guest = event.invitations.filter(guest=request.user).exists()

    context = {
        'event': event,
        'invitations': invitations,
        'is_organizer': is_organizer,
        'is_guest': is_guest,
    }
    return render(request, 'event_detail.html', context)


def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)

    # Перевірка дозволу: лише організатор може редагувати
    if request.user != event.organizer:
        messages.error(request, "У вас немає дозволу на редагування цієї події.")
        return redirect('event_planner:event_detail', pk=pk)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Подію успішно оновлено!")
            return redirect('event_planner:event_detail', pk=pk)
        else:
            messages.error(request, "Не вдалося оновити подію. Будь ласка, перевірте форму.")
    else:
        form = EventForm(instance=event)
    return render(request, 'event_form.html', {'form': form, 'event': event})


def event_delete(request, pk):

    event = get_object_or_404(Event, pk=pk)

    if request.user != event.organizer:
        messages.error(request, "У вас немає дозволу на видалення цієї події.")
        return redirect('event_planner:event_detail', pk=pk)

    if request.method == 'POST':
        event.delete()
        messages.success(request, "Подію успішно видалено!")
        return redirect('event_planner:event_list')
    return render(request, 'event_confirm_delete.html', {'event': event})


def event_invite(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.user != event.organizer:
        messages.error(request, "У вас немає дозволу на запрошення гостей на цю подію.")
        return redirect('event_planner:event_detail', pk=pk)

    errors = {}
    new_invitations_count = 0


    if request.method == 'POST':
        selected_guest_ids = request.POST.getlist('guests') 

        if not selected_guest_ids:
            errors['guests'] = "Будь ласка, виберіть хоча б одного гостя."
        else:
            for guest_id in selected_guest_ids:
                try:
                    guest = User.objects.get(id=guest_id)
                    if guest != event.organizer and not Invitation.objects.filter(event=event, guest=guest).exists():
                        Invitation.objects.create(event=event, guest=guest, status=Invitation.Status.invited)
                        new_invitations_count += 1
                except User.DoesNotExist:
                    messages.warning(request, f"Користувач з ID {guest_id} не знайдений.")
                    continue

            if new_invitations_count > 0:
                messages.success(request, f"Запрошення успішно надіслано {new_invitations_count} гостям!")
                return redirect('event_planner:event_detail', pk=pk)
            elif not errors: 
                messages.info(request, "Немає нових гостей для запрошення або всі вибрані вже запрошені.")
                return redirect('event_planner:event_detail', pk=pk)
        
        if errors:
            messages.error(request, "Не вдалося надіслати запрошення. Будь ласка, перевірте форму.")

    return render(request, 'event_invite.html')


def invitation_list(request):
    invitations = Invitation.objects.filter(guest=request.user).order_by('-event__start_time')
    context = {
        'invitations': invitations,
    }
    return render(request, 'invitation_list.html', context)


def invitation_respond(request, pk):

    invitation = get_object_or_404(Invitation, pk=pk)


    if request.user != invitation.guest:
        messages.error(request, "У вас немає дозволу на відповідь на це запрошення.")
        return redirect('event_planner:invitation_list')

    if request.method == 'POST':
        form = InvitationForm(request.POST, instance=invitation, fields=['status'])
        if form.is_valid():
            form.save()
            messages.success(request, "Вашу відповідь на запрошення успішно збережено!")
            return redirect('event_planner:invitation_list')
        else:
            messages.error(request, "Не вдалося зберегти відповідь. Будь ласка, перевірте форму.")
    else:
        form = InvitationForm(instance=invitation, fields=['status'])
    
    context = {
        'form': form,
        'invitation': invitation,
    }
    return render(request, 'invitation_respond.html', context)
