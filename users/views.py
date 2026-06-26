from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .forms import UserRegisterForm, UserUpdateForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from movies.models import Movie, Booking, Event
from django.utils import timezone


def home(request):
    from movies.models import Event, Play
    from django.utils import timezone

    movies = Movie.objects.all()
    events = Event.objects.filter(event_date__gte=timezone.localdate())[:6]
    plays = Play.objects.filter(play_date__gte=timezone.localdate())[:6]

    return render(request, 'home.html', {
        'movies': movies,
        'events': events,
        'plays': plays,
    })
def coming_soon(request, feature_name='Feature'):
    return render(request, 'coming_soon.html', {'feature_name': feature_name})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('profile')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def profile(request):
    from movies.models import EventBooking, PlayBooking

    bookings = Booking.objects.filter(user=request.user)
    event_bookings = EventBooking.objects.filter(user=request.user, status='success')
    play_bookings = PlayBooking.objects.filter(user=request.user, status='success')

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)

    return render(request, 'users/profile.html', {
        'u_form': u_form,
        'bookings': bookings,
        'event_bookings': event_bookings,
        'play_bookings': play_bookings,
    })


@login_required
def reset_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'users/reset_password.html', {'form': form})