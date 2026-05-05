import random
from django.conf import settings
from django.urls import reverse

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# OTP
def generate_otp():
    return str(random.randint(100000, 999999))


# SEND EMAIL FUNCTION (COMMON)
def send_email(to_email, subject, html_content):
    try:
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)

        print("✅ SendGrid status:", response.status_code)

        return response.status_code in (200, 202)

    except Exception as e:
        print("❌ SendGrid error:", str(e))
        return False


# OTP EMAIL
def send_registration_otp(email, otp, username):
    verify_url = settings.SITE_URL + reverse("verify_register_otp")

    html = f"""
    <h2>Healix Hospital</h2>

    <p>Hello <b>{username}</b></p>

    <p>Your OTP:</p>
    <h1>{otp}</h1>

    <p>Click below:</p>
    <a href="{verify_url}">Verify OTP</a>
    """

    return send_email(email, "OTP Verification", html)


# BOOKING EMAIL
def send_booking_confirmation_email(appointment):
    email = appointment.patient.email

    html = f"""
    <h2>Appointment Confirmed</h2>

    <p>Doctor: {appointment.doctor.first_name}</p>
    <p>Date: {appointment.appointment_date}</p>
    <p>Time: {appointment.appointment_time}</p>
    """

    return send_email(email, "Appointment Confirmed", html)


# REMINDER EMAIL
def send_reminder_email(appointment):
    email = appointment.patient.email

    html = f"""
    <h2>Reminder</h2>

    <p>Doctor: {appointment.doctor.first_name}</p>
    <p>Date: {appointment.appointment_date}</p>
    <p>Time: {appointment.appointment_time}</p>
    """

    return send_email(email, "Appointment Reminder", html)