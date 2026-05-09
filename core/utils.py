import resend
import random

from django.conf import settings
from django.urls import reverse


# =====================================
# RESEND CONFIG
# =====================================

resend.api_key = settings.RESEND_API_KEY


# =====================================
# COMMON EMAIL FUNCTION
# =====================================

def send_email(subject, html_content, to_email):

    try:

        params = {
            "from": "onboarding@resend.dev",
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }

        email = resend.Emails.send(params)

        print("✅ EMAIL SENT:", email)

        return True

    except Exception as e:

        print("❌ EMAIL ERROR:", str(e))

        return False


# =====================================
# GENERATE OTP
# =====================================

def generate_otp():

    return str(random.randint(100000, 999999))


# =====================================
# OTP EMAIL
# =====================================

def send_registration_otp(email, otp, username):

    verify_url = settings.SITE_URL + reverse("verify_register_otp")

    html = f"""
    <html>

    <body style="font-family:Arial;background:#f4f4f4;padding:20px;">

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

            <p>Your verification code is:</p>

            <h1 style="
                text-align:center;
                background:#0d6efd;
                color:white;
                padding:15px;
                border-radius:8px;
                letter-spacing:5px;
            ">
                {otp}
            </h1>

            <p>
                OTP expires in 10 minutes.
            </p>

            <p>
                Verification page:
            </p>

            <p>
                {verify_url}
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


# =====================================
# BOOKING EMAIL
# =====================================

def send_booking_confirmation_email(appointment):

    email = appointment.patient.email

    html = f"""
    <html>

    <body style="font-family:Arial;background:#f4f4f4;padding:20px;">

        <div style="
            max-width:600px;
            margin:auto;
            background:white;
            padding:30px;
            border-radius:10px;
        ">

            <h2 style="color:green;">
                Appointment Confirmed
            </h2>

            <p>
                Your appointment booking is confirmed.
            </p>

            <table style="width:100%;">

                <tr>
                    <td><b>Doctor</b></td>
                    <td>{appointment.doctor.first_name}</td>
                </tr>

                <tr>
                    <td><b>Date</b></td>
                    <td>{appointment.appointment_date}</td>
                </tr>

                <tr>
                    <td><b>Time</b></td>
                    <td>{appointment.appointment_time}</td>
                </tr>

            </table>

            <hr>

            <p style="font-size:12px;color:gray;">
                Healix Hospital Management System
            </p>

        </div>

    </body>

    </html>
    """

    return send_email(
        "Appointment Confirmed - Healix Hospital",
        html,
        email
    )


# =====================================
# REMINDER EMAIL
# =====================================

def send_reminder_email(appointment):

    email = appointment.patient.email

    html = f"""
    <html>

    <body style="font-family:Arial;background:#f4f4f4;padding:20px;">

        <div style="
            max-width:600px;
            margin:auto;
            background:white;
            padding:30px;
            border-radius:10px;
        ">

            <h2 style="color:#ff9800;">
                Appointment Reminder
            </h2>

            <p>
                You have an upcoming appointment.
            </p>

            <table style="width:100%;">

                <tr>
                    <td><b>Doctor</b></td>
                    <td>{appointment.doctor.first_name}</td>
                </tr>

                <tr>
                    <td><b>Date</b></td>
                    <td>{appointment.appointment_date}</td>
                </tr>

                <tr>
                    <td><b>Time</b></td>
                    <td>{appointment.appointment_time}</td>
                </tr>

            </table>

            <hr>

            <p style="font-size:12px;color:gray;">
                Healix Hospital Management System
            </p>

        </div>

    </body>

    </html>
    """

    return send_email(
        "Appointment Reminder - Healix Hospital",
        html,
        email
    )