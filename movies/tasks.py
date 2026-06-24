import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger('movies.tasks')


def send_booking_confirmation_email(booking_id):
    try:
        from .models import Booking
        booking = Booking.objects.select_related(
            'user', 'movie', 'theater', 'seat'
        ).get(id=booking_id)

        subject = f'Booking Confirmed — {booking.movie.name}'

        html_content = render_to_string(
            'movies/email_confirmation.html',
            {
                'user': booking.user,
                'movie': booking.movie,
                'theater': booking.theater,
                'seat': booking.seat,
                'booking': booking,
            }
        )
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email='BookMySeat <noreply@bookmyseat.com>',
            to=[booking.user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        logger.info(
            f'SUCCESS: Email sent for booking ID {booking_id} '
            f'to {booking.user.email}'
        )
        return True

    except Booking.DoesNotExist:
        logger.error(f'FAILED: Booking ID {booking_id} not found')
        return False

    except Exception as e:
        logger.error(
            f'FAILED: Email failed for booking ID {booking_id}. '
            f'Error: {str(e)}'
        )
        raise


def release_expired_seat_locks():
    """
    Background scheduler task — automatically releases
    expired seat locks every 30 seconds.
    Handles edge cases:
    - User closing the app
    - Network interruption during booking
    - Multiple seat selections across devices
    """
    from .models import SeatLock
    from django.utils import timezone

    try:
        # find all expired locks
        expired_locks = SeatLock.objects.filter(
            is_active=True,
            expires_at__lt=timezone.now()
        )

        count = 0
        for lock in expired_locks:
            # release the lock
            lock.is_active = False
            lock.save()
            count += 1

        if count > 0:
            logger.info(f'Released {count} expired seat locks')
        
        return count

    except Exception as e:
        logger.error(f'Error releasing seat locks: {str(e)}')
        return 0