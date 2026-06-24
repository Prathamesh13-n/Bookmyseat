import django.db.models.deletion
from django.db import migrations, models
from django.utils import timezone


def populate_show_dates(apps, schema_editor):
    Booking = apps.get_model('movies', 'Booking')
    SeatLock = apps.get_model('movies', 'SeatLock')

    for booking in Booking.objects.all():
        if booking.show_date:
            continue
        if booking.booked_at:
            booking.show_date = timezone.localtime(booking.booked_at).date()
        else:
            booking.show_date = timezone.localdate()
        booking.save(update_fields=['show_date'])

    today = timezone.localdate()
    for lock in SeatLock.objects.all():
        if lock.show_date:
            continue
        lock.show_date = today
        lock.save(update_fields=['show_date'])


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0007_seatlock'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='show_date',
            field=models.DateField(db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='seatlock',
            name='show_date',
            field=models.DateField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='seat',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='movies.seat',
            ),
        ),
        migrations.AlterField(
            model_name='seatlock',
            name='seat',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='locks',
                to='movies.seat',
            ),
        ),
        migrations.RunPython(populate_show_dates, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='booking',
            name='show_date',
            field=models.DateField(db_index=True),
        ),
        migrations.AlterField(
            model_name='seatlock',
            name='show_date',
            field=models.DateField(db_index=True),
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['theater', 'show_date'], name='booking_theater_date_idx'),
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['user', 'show_date'], name='booking_user_date_idx'),
        ),
        migrations.AddIndex(
            model_name='seatlock',
            index=models.Index(fields=['seat', 'show_date', 'is_active'], name='seatlock_seat_date_active_idx'),
        ),
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.UniqueConstraint(
                fields=('seat', 'theater', 'show_date'),
                name='unique_booking_per_seat_show_date',
            ),
        ),
        migrations.AddConstraint(
            model_name='seatlock',
            constraint=models.UniqueConstraint(
                fields=('seat', 'show_date'),
                name='unique_lock_per_seat_show_date',
            ),
        ),
    ]
