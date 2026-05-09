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
        html_content=html_content,
        plain_text_content="Healix Hospital verification email"
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

    html = f"""
    <html>
    <body style="font-family: Arial; background:#f4f4f4; padding:20px;">

        <div style="
            max-width:600px;
            margin:auto;
            background:white;
            padding:30px;
            border-radius:10px;
        ">

            <h2 style="color:#0d6efd;">
                Healix Hospital
            </h2>

            <p>Hello {username},</p>

            <p>
                Thank you for registering with Healix Hospital.
            </p>

            <p>
                Your verification code is:
            </p>

            <h1 style="
                background:#0d6efd;
                color:white;
                padding:15px;
                border-radius:8px;
                text-align:center;
                letter-spacing:5px;
            ">
                {otp}
            </h1>

            <p>
                This OTP will expire in 10 minutes.
            </p>

            <hr>

            <p style="font-size:12px;color:gray;">
                Healix Hospital Management System
            </p>

        </div>

    </body>
    </html>
    """

    return send_email(
        "Healix Hospital OTP Verification",
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

