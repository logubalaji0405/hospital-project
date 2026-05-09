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

    try:

        email = appointment.patient.email

        if not email:
            print("❌ No patient email")
            return False

        html = f"""
        <h2>Appointment Confirmed</h2>

        <p>Hello {appointment.patient.first_name},</p>

        <p>Your appointment is confirmed.</p>

        <hr>

        <p>
        <strong>Doctor:</strong>
        Dr. {appointment.doctor.first_name}
        </p>

        <p>
        <strong>Date:</strong>
        {appointment.appointment_date}
        </p>

        <p>
        <strong>Time:</strong>
        {appointment.appointment_time}
        </p>

        <hr>

        <p>Please arrive 10 minutes early.</p>

        <h3>Healix Hospital</h3>
        """

        return send_email(
            "Appointment Confirmed - Healix Hospital",
            html,
            email
        )

    except Exception as e:
        print("❌ BOOKING EMAIL ERROR:", str(e))
        return False


# =========================
# REMINDER EMAIL
# =========================
def send_reminder_email(appointment):

    try:

        email = appointment.patient.email

        if not email:
            return False

        html = f"""
        <h2>Appointment Reminder</h2>

        <p>Hello {appointment.patient.first_name},</p>

        <p>This is reminder for your appointment.</p>

        <hr>

        <p>
        <strong>Doctor:</strong>
        Dr. {appointment.doctor.first_name}
        </p>

        <p>
        <strong>Date:</strong>
        {appointment.appointment_date}
        </p>

        <p>
        <strong>Time:</strong>
        {appointment.appointment_time}
        </p>

        <hr>

        <h3>Healix Hospital</h3>
        """

        return send_email(
            "Appointment Reminder - Healix Hospital",
            html,
            email
        )

    except Exception as e:
        print("❌ REMINDER EMAIL ERROR:", str(e))
        return False

