import re
import logging
import hmac
import hashlib
import uuid

logger = logging.getLogger('movies.tasks')


def validate_youtube_url(url):
    """
    Validates and sanitizes YouTube URL.
    Prevents XSS injection and malicious scripts.
    Returns embed URL if valid, None if invalid.
    """
    if not url:
        return None

    # allowed YouTube URL patterns — supports all formats including ?si= params
    youtube_patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})(?:.*)?',
        r'https?://(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})(?:\?.*)?',
        r'https?://(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})(?:.*)?',
    ]

    video_id = None
    for pattern in youtube_patterns:
        match = re.match(pattern, url.strip())
        if match:
            video_id = match.group(1)
            break

    if not video_id:
        logger.warning(f'Invalid YouTube URL attempted: {url}')
        return None

    # return safe embed URL with security parameters
    safe_embed_url = (
        f'https://www.youtube.com/embed/{video_id}'
        f'?rel=0&modestbranding=1&loading=lazy'
    )

    logger.info(f'Valid YouTube URL validated: {video_id}')
    return safe_embed_url


def get_youtube_thumbnail(url):
    """
    Returns YouTube thumbnail URL for fallback display.
    """
    if not url:
        return None

    youtube_patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})(?:.*)?',
        r'https?://(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})(?:\?.*)?',
        r'https?://(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})(?:.*)?',
    ]

    for pattern in youtube_patterns:
        match = re.match(pattern, url.strip())
        if match:
            video_id = match.group(1)
            return f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'

    return None


def generate_idempotency_key():
    """Generate unique idempotency key to prevent duplicate transactions"""
    return str(uuid.uuid4())


def verify_payment_signature(payment_id, order_id, signature, secret_key):
    """
    Verify payment signature from payment provider.
    Prevents fraud and replay attacks.
    Server-side only — never trust frontend callbacks.
    """
    try:
        message = f"{order_id}|{payment_id}"
        generated_signature = hmac.new(
            secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(generated_signature, signature)
    except Exception as e:
        logger.error(f'Signature verification failed: {str(e)}')
        return False


def calculate_total_amount(num_seats, ticket_price=250):
    """Calculate total payment amount"""
    return num_seats * ticket_price