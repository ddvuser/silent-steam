from django.core.mail import send_mail


def send_reset_pswd_link(user, link):
    """Send password reset link to the user"""
    subject = "Password Reset Link"
    message = f"Your password reset link is: {link}. Expires in 5 minutes."
    from_email = "support@silent-steam.com"
    to_email = user.email
    send_mail(subject, message, from_email, [to_email])
