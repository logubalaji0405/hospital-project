from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
import random
import socket


# ==========================================
# COMMON EMAIL FUNCTION
# ==========================================

def send_email(subject, html_content, to_email):

    try:

        socket.setdefaulttimeout(30)

        msg = EmailMultiAlternatives(
            subject=subject,
            body="Healix Hospital Email",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email]
        )

        msg.attach_alternative(html_content, "text/html")

        msg.send(fail_silently=False)

        print("✅ EMAIL SENT")

        return True

    except Exception as e:

        print("❌ EMAIL ERROR:", str(e))

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

            <p>
                Thank you for registering with Healix Hospital.
            </p>

            <p>
                Your OTP verification code is:
            </p>

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
                This OTP expires in 10 minutes.
            </p>

            <p>
                Verification Page:
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


# ==========================================
# BOOKING CONFIRMATION EMAIL
# ==========================================
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
                Your appointment has been successfully booked.
            </p>

            <table style="width:100%;padding:10px;">

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
        "Appointment Confirmation - Healix Hospital",
        html,
        email
    )


# ==========================================
# REMINDER EMAIL
# ==========================================
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
                This is a reminder for your upcoming appointment.
            </p>

            <table style="width:100%;padding:10px;">

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