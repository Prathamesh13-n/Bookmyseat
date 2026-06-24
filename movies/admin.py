from django.contrib import admin
from .models import Movie, Theater, Seat, Booking, SeatLock

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'cast','description']

@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ['name', 'movie', 'time']

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['theater', 'seat_number']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'seat', 'movie', 'theater', 'show_date', 'booked_at']

@admin.register(SeatLock)
class SeatLockAdmin(admin.ModelAdmin):
    list_display = ['seat', 'user', 'show_date', 'is_active', 'expires_at']


from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'venue', 'event_date']