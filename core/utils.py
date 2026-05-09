from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
from django.urls import reverse
import random


# ==========================================
# COMMON SENDGRID EMAIL FUNCTION
# ==========================================
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

        print("✅ SENDGRID STATUS:", response.status_code)

        return response.status_code in [200, 202]

    except Exception as e:
        print("❌ SENDGRID ERROR:", str(e))
        return False


# ==========================================
# GENERATE OTP
# ==========================================
def generate_otp():
    return str(random.randint(100000, 999999))


# ==========================================
# REGISTRATION OTP EMAIL
# ==========================================
def send_registration_otp(email, otp, username):

    verify_url = settings.SITE_URL + reverse("verify_register_otp")

    html = f"""
    <div style="font-family:Arial;padding:20px;">
        <h2 style="color:#2563eb;">Healix Hospital</h2>

        <p>Hello <b>{username}</b>,</p>

        <p>Your OTP is:</p>

        <h1 style="color:#2563eb;">{otp}</h1>

        <p>This OTP is valid for 5 minutes.</p>

        <p>
            <a href="{verify_url}"
               style="
               background:#2563eb;
               color:white;
               padding:10px 20px;
               text-decoration:none;
               border-radius:5px;">
               Verify OTP
            </a>
        </p>

        <hr>

        <p style="font-size:12px;color:gray;">
            Healix Hospital Secure Verification
        </p>
    </div>
    """

    return send_email(
        "Healix HMS OTP Verification",
        html,
        email
    )


# ==========================================
# BOOKING CONFIRMATION EMAIL
# ==========================================
def send_booking_confirmation_email(appointment):

    patient_email = appointment.patient.email

    if not patient_email:
        return False

    html = f"""
    <div style="font-family:Arial;padding:20px;">
        <h2 style="color:#16a34a;">Appointment Confirmed</h2>

        <p>Hello <b>{appointment.patient.first_name}</b>,</p>

        <p>Your appointment has been confirmed.</p>

        <ul>
            <li>
                <b>Doctor:</b>
                Dr. {appointment.doctor.first_name}
            </li>

            <li>
                <b>Date:</b>
                {appointment.appointment_date}
            </li>

            <li>
                <b>Time:</b>
                {appointment.appointment_time}
            </li>
        </ul>

        <p>Please arrive 10 minutes early.</p>

        <hr>

        <p style="font-size:12px;color:gray;">
            Healix Hospital
        </p>
    </div>
    """

    return send_email(
        "Appointment Confirmed | Healix Hospital",
        html,
        patient_email
    )


# ==========================================
# REMINDER EMAIL
# ==========================================
def send_reminder_email(appointment):

    patient_email = appointment.patient.email

    if not patient_email:
        return False

    html = f"""
    <div style="font-family:Arial;padding:20px;">
        <h2 style="color:#f59e0b;">Appointment Reminder</h2>

        <p>Hello <b>{appointment.patient.first_name}</b>,</p>

        <p>This is a reminder for your upcoming appointment.</p>

        <ul>
            <li>
                <b>Doctor:</b>
                Dr. {appointment.doctor.first_name}
            </li>

            <li>
                <b>Date:</b>
                {appointment.appointment_date}
            </li>

            <li>
                <b>Time:</b>
                {appointment.appointment_time}
            </li>
        </ul>

        <p>Please be on time.</p>

        <hr>

        <p style="font-size:12px;color:gray;">
            Healix Hospital Reminder System
        </p>
    </div>
    """

    return send_email(
        "Appointment Reminder | Healix Hospital",
        html,
        patient_email
    )