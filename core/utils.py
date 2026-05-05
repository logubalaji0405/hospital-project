from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
from django.urls import reverse
import random


# ======================
# SENDGRID SAFE EMAIL
# ======================
def send_email(subject, html_content, to_email):
    try:
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)

        print("✅ SendGrid:", response.status_code)
        return response.status_code in [200, 202]

    except Exception as e:
        print("❌ SendGrid Error:", e)
        return False


# ======================
# OTP
# ======================
def generate_otp():
    return str(random.randint(100000, 999999))


def send_registration_otp(email, otp, username):
    verify_url = settings.SITE_URL + reverse("verify_register_otp")

    html = f"""
    <h2>Healix Hospital</h2>
    <p>Hello {username},</p>
    <p>Your OTP is:</p>
    <h1>{otp}</h1>
    <p>Verify here:</p>
    <a href="{verify_url}">Verify OTP</a>
    """

    return send_email("OTP Verification", html, email)


# ======================
# BOOKING EMAIL
# ======================
def send_booking_confirmation_email(appointment):
    email = appointment.patient.email

    html = f"""
    <h2>Appointment Confirmed</h2>
    <p>Doctor: {appointment.doctor.first_name}</p>
    <p>Date: {appointment.appointment_date}</p>
    <p>Time: {appointment.appointment_time}</p>
    """

    return send_email("Appointment Confirmed", html, email)


# ======================
# REMINDER
# ======================
def send_reminder_email(appointment):
    email = appointment.patient.email

    html = f"""
    <h2>Reminder</h2>
    <p>Doctor: {appointment.doctor.first_name}</p>
    <p>Date: {appointment.appointment_date}</p>
    <p>Time: {appointment.appointment_time}</p>
    """

    return send_email("Appointment Reminder", html, email)