from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import random


# OTP GENERATE
def generate_otp():
    return str(random.randint(100000, 999999))


# OTP EMAIL
def send_registration_otp(email, otp, username):
    verify_url = settings.SITE_URL + reverse("verify_register_otp")

    subject = "Healix HMS OTP Verification"

    message = f"""
Hello {username},

Your OTP is: {otp}

This OTP is valid for 5 minutes.

Verify here:
{verify_url}

Healix Hospital
"""

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        print("✅ OTP EMAIL SENT")
        return True

    except Exception as e:
        print("❌ EMAIL ERROR:", e)
        return False


# BOOKING EMAIL
def send_booking_confirmation_email(appointment):
    email = appointment.patient.email

    if not email:
        return False

    subject = "Appointment Confirmed - Healix Hospital"

    message = f"""
Hello {appointment.patient.first_name},

Your appointment is confirmed.

Doctor: Dr. {appointment.doctor.first_name}
Date: {appointment.appointment_date}
Time: {appointment.appointment_time}

Please arrive 10 minutes early.

Healix Hospital
"""

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        print("✅ BOOKING EMAIL SENT")
        return True

    except Exception as e:
        print("❌ BOOKING EMAIL ERROR:", e)
        return False


# REMINDER EMAIL
def send_reminder_email(appointment):
    email = appointment.patient.email

    if not email:
        return False

    subject = "Appointment Reminder - Healix Hospital"

    message = f"""
Hello {appointment.patient.first_name},

Reminder for your appointment:

Doctor: Dr. {appointment.doctor.first_name}
Date: {appointment.appointment_date}
Time: {appointment.appointment_time}

Please be on time.

Healix Hospital
"""

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        print("✅ REMINDER EMAIL SENT")
        return True

    except Exception as e:
        print("❌ REMINDER EMAIL ERROR:", e)
        return False