from django.core.mail import send_mail
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
from django.urls import reverse

def send_booking_confirmation_email(appointment):
    patient_email = appointment.patient.email

    if not patient_email:
        print("No email found")
        return False

    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=patient_email,
        subject="Appointment Confirmed - Healix Hospital",
        html_content=f"""
        <h2>Healix Hospital</h2>

        <p>Hello {appointment.patient.first_name},</p>

        <p>Your appointment has been confirmed.</p>

        <ul>
            <li><b>Doctor:</b> Dr. {appointment.doctor.first_name}</li>
            <li><b>Date:</b> {appointment.appointment_date}</li>
            <li><b>Time:</b> {appointment.appointment_time}</li>
        </ul>

        <p>Please arrive 10 minutes early.</p>

        <hr>
        <p>Healix Hospital</p>
        """
    )

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)

        print("SendGrid status:", response.status_code)

        return response.status_code in (200, 202)

    except Exception as e:
        print("Email error:", e)
        return False


def send_reminder_email(appointment):
    patient_email = appointment.patient.email

    if not patient_email:
        print("No patient email found for reminder")
        return False

    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=patient_email,
        subject="⏰ Appointment Reminder | Healix Hospital",
        html_content=f"""
        <div style="font-family:Arial;padding:20px;">
            <h2 style="color:#2563eb;">Healix Hospital</h2>

            <p>Hello <b>{appointment.patient.first_name}</b>,</p>

            <p>This is a reminder for your upcoming appointment.</p>

            <ul>
                <li><b>Doctor:</b> Dr. {appointment.doctor.first_name}</li>
                <li><b>Date:</b> {appointment.appointment_date}</li>
                <li><b>Time:</b> {appointment.appointment_time}</li>
            </ul>

            <p>Please arrive 10 minutes early.</p>

            <hr>
            <p style="font-size:12px;color:gray;">
            Healix Hospital • Appointment Reminder System
            </p>
        </div>
        """
    )

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)

        print("Reminder status:", response.status_code)

        return response.status_code in (200, 202)

    except Exception as e:
        print("Reminder email error:", e)
        return False    


def generate_otp():
    return str(random.randint(100000, 999999))


def send_registration_otp(email, otp, username):
    # ✅ Mobile-safe URL
    verify_url = settings.SITE_URL + reverse("verify_register_otp")

    html_content = f"""
    <div style="font-family:Arial;padding:20px;">
        <h2 style="color:#2563eb;">Healix Hospital</h2>

        <p>Hello <b>{username}</b>,</p>

        <p>Your OTP is:</p>

        <h1 style="color:#2563eb;">{otp}</h1>

        <p>This OTP is valid for 5 minutes.</p>

        <p>Or click below to verify:</p>

        <a href="{verify_url}"
           style="background:#2563eb;color:white;
           padding:10px 20px;
           text-decoration:none;
           border-radius:5px;">
           Verify OTP
        </a>

        <hr>
        <p style="font-size:12px;color:gray;">
        Healix Hospital • Secure System
        </p>
    </div>
    """

    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=email,
        subject="Healix HMS OTP Verification",
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print("SendGrid status:", response.status_code)

    except Exception as e:
        print("SendGrid error:", str(e))