from django.core.mail import send_mail
from django.conf import settings
import random
import time


# OTP GENERATE
def generate_otp():
    return str(random.randint(100000, 999999))


# SAFE EMAIL (RETRY SYSTEM)
def safe_send_mail(subject, message, to_email):
    for attempt in range(3):
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
            print(f"❌ Attempt {attempt+1} failed:", e)
            time.sleep(2)

    return False


# OTP EMAIL
def send_registration_otp(email, otp, username):
    message = f"""
Hello {username},

Your OTP is: {otp}

Valid for 5 minutes.

Healix Hospital
"""
    return safe_send_mail("OTP Verification", message, email)


# BOOKING EMAIL
def send_booking_confirmation_email(appointment):
    return safe_send_mail(
        "Appointment Confirmed",
        f"""
Hello {appointment.patient.first_name},

Your appointment is confirmed.

Doctor: Dr. {appointment.doctor.first_name}
Date: {appointment.appointment_date}
Time: {appointment.appointment_time}
""",
        appointment.patient.email
    )


# REMINDER EMAIL
def send_reminder_email(appointment):
    return safe_send_mail(
        "Appointment Reminder",
        f"""
Hello {appointment.patient.first_name},

Reminder for your appointment:

Doctor: Dr. {appointment.doctor.first_name}
Date: {appointment.appointment_date}
Time: {appointment.appointment_time}
""",
        appointment.patient.email
    )