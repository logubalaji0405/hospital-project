from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import random


# OTP GENERATE
def generate_otp():
    return str(random.randint(100000, 999999))


# COMMON EMAIL FUNCTION (IMPORTANT)
def send_email(subject, message, to_email):
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
            fail_silently=False
        )
        print("✅ EMAIL SENT")
        return True

    except Exception as e:
        print("❌ EMAIL ERROR:", e)
        return False


# OTP EMAIL
def send_registration_otp(email, otp, username):
    verify_url = settings.SITE_URL + reverse("verify_register_otp")

    subject = "Your Healix OTP Code"

    message = f"""
Hello {username},

Your verification code is: {otp}

This code is valid for 5 minutes.

Verify here:
{verify_url}

If you did not request this, ignore this email.

Regards,
Healix Hospital Team
"""

    return send_email(subject, message, email)


# BOOKING CONFIRMATION
def send_booking_confirmation_email(appointment):
    email = appointment.patient.email

    if not email:
        return False

    subject = "Appointment Confirmed - Healix Hospital"

    message = f"""
Hello {appointment.patient.first_name},

Your appointment has been successfully confirmed.

Doctor: Dr. {appointment.doctor.first_name}
Date: {appointment.appointment_date}
Time: {appointment.appointment_time}

Please arrive 10 minutes early.

Regards,
Healix Hospital Team
"""

    return send_email(subject, message, email)


# REMINDER EMAIL
def send_reminder_email(appointment):
    email = appointment.patient.email

    if not email:
        return False

    subject = "Appointment Reminder - Healix Hospital"

    message = f"""
Hello {appointment.patient.first_name},

This is a reminder for your upcoming appointment.

Doctor: Dr. {appointment.doctor.first_name}
Date: {appointment.appointment_date}
Time: {appointment.appointment_time}

Please be on time.

Regards,
Healix Hospital Team
"""

    return send_email(subject, message, email)