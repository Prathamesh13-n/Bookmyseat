from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid


class Movie(models.Model):

    GENRE_CHOICES = [
        ('action', 'Action'),
        ('comedy', 'Comedy'),
        ('drama', 'Drama'),
        ('horror', 'Horror'),
        ('romance', 'Romance'),
        ('thriller', 'Thriller'),
        ('sci-fi', 'Sci-Fi'),
        ('animation', 'Animation'),
    ]

    LANGUAGE_CHOICES = [
        ('english', 'English'),
        ('hindi', 'Hindi'),
        ('marathi', 'Marathi'),
        ('tamil', 'Tamil'),
        ('telugu', 'Telugu'),
        ('kannada', 'Kannada'),
    ]

    name = models.CharField(max_length=255, db_index=True)
    image = models.ImageField(upload_to="movies/")
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    cast = models.TextField()
    description = models.TextField(blank=True, null=True)
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES, default='action', db_index=True)
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES, default='english', db_index=True)
    release_date = models.DateField(null=True, blank=True)
    trailer_url = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['genre', 'language']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return self.name


class Theater(models.Model):

    SHOW_TIME_CHOICES = [
        ('10:00 AM', '10:00 AM - Morning Show'),
        ('01:00 PM', '01:00 PM - Afternoon Show'),
        ('04:00 PM', '04:00 PM - Evening Show'),
        ('07:00 PM', '07:00 PM - Night Show'),
        ('10:00 PM', '10:00 PM - Late Night Show'),
    ]

    name = models.CharField(max_length=255)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='theaters')
    time = models.DateTimeField()
    show_time = models.CharField(
        max_length=20,
        choices=SHOW_TIME_CHOICES,
        default='07:00 PM',
        db_index=True
    )

    def __str__(self):
        return f'{self.name} - {self.movie.name} at {self.show_time}'


class Seat(models.Model):

    CATEGORY_CHOICES = [
        ('vip', 'VIP Lounge'),
        ('premium', 'Premium Recliner'),
        ('gold', 'Executive Gold'),
        ('silver', 'Classic Silver'),
        ('basic', 'Basic'),
    ]

    CATEGORY_MULTIPLIERS = {
        'vip': 3.0,
        'premium': 2.0,
        'gold': 1.5,
        'silver': 1.2,
        'basic': 1.0,
    }

    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)
    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        default='basic',
        db_index=True
    )

    class Meta:
        ordering = ['seat_number']

    def get_base_price(self):
        """Base price determined by movie rating"""
        rating = float(self.theater.movie.rating)
        if rating >= 8.0:
            return 200
        elif rating >= 6.0:
            return 150
        else:
            return 120

    def get_price(self):
        """Final price = base price x category multiplier"""
        base = self.get_base_price()
        multiplier = self.CATEGORY_MULTIPLIERS.get(self.category, 1.0)
        return round(base * multiplier)

    def __str__(self):
        return f'{self.seat_number} ({self.category}) - ₹{self.get_price()} in {self.theater.name}'


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    show_date = models.DateField(db_index=True)
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['seat', 'theater', 'show_date'],
                name='unique_booking_per_seat_show_date'
            )
        ]
        indexes = [
            models.Index(fields=['theater', 'show_date'], name='booking_theater_date_idx'),
            models.Index(fields=['user', 'show_date'], name='booking_user_date_idx'),
        ]

    def __str__(self):
        return (
            f'Booking by {self.user.username} for {self.seat.seat_number} '
            f'at {self.theater.name} on {self.show_date}'
        )


class Payment(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    idempotency_key = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    payment_signature = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f'Payment {self.idempotency_key} — {self.status}'


class SeatLock(models.Model):
    """
    Temporarily locks a seat for 2 minutes during booking process.
    Prevents double booking under simultaneous requests.
    """
    seat = models.ForeignKey(
        Seat,
        on_delete=models.CASCADE,
        related_name='locks'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    show_date = models.DateField(db_index=True)
    locked_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['seat', 'show_date'],
                name='unique_lock_per_seat_show_date'
            )
        ]
        indexes = [
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_active', 'expires_at']),
            models.Index(fields=['seat', 'show_date', 'is_active'], name='seatlock_seat_date_active_idx'),
        ]

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=2)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return (
            f'Lock on {self.seat.seat_number} for {self.show_date} '
            f'by {self.user.username} expires {self.expires_at}'
        )
    


class Event(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="events/")
    description = models.TextField(blank=True, null=True)
    venue = models.CharField(max_length=255, blank=True, null=True)
    event_date = models.DateField(null=True, blank=True)
    ticket_price = models.DecimalField(max_digits=8, decimal_places=2, default=500)
    total_tickets = models.PositiveIntegerField(default=100)

    class Meta:
        ordering = ['event_date']

    def tickets_booked(self):
        return sum(b.quantity for b in self.bookings.filter(status='success'))

    def tickets_remaining(self):
        return self.total_tickets - self.tickets_booked()

    def __str__(self):
        return self.name


class EventBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    idempotency_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.event.name} x{self.quantity}'