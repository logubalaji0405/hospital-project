import random

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse


# =========================
# COMMON EMAIL FUNCTION
# =========================
def send_email(subject, html_content, to_email):

    try:

        msg = EmailMultiAlternatives(
            subject=subject,
            body="Healix Hospital Email",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )

        msg.attach_alternative(html_content, "text/html")

        msg.send(fail_silently=False)

        print("✅ EMAIL SENT SUCCESS")

        return True

    except Exception as e:

        print("❌ EMAIL ERROR:", str(e))

        return False


# =========================
# GENERATE OTP
# =========================
def generate_otp():
    return str(random.randint(100000, 999999))


# =========================
# REGISTRATION OTP EMAIL
# =========================
def send_registration_otp(email, otp, username):

    verify_url = settings.SITE_URL + reverse("verify_register_otp")

    html = f"""
    <div style="font-family: Arial; padding:20px;">

        <h2 style="color:#0d6efd;">
            Healix Hospital
        </h2>

        <p>Hello <b>{username}</b>,</p>

        <p>Your OTP for account verification is:</p>

        <h1 style="
            background:#0d6efd;
            color:white;
            padding:15px;
            border-radius:10px;
            width:200px;
            text-align:center;
        ">
            {otp}
        </h1>

        <p>
            Verify your account below:
        </p>

        <a href="{verify_url}" style="
            background:#198754;
            color:white;
            padding:12px 20px;
            text-decoration:none;
            border-radius:8px;
        ">
            Verify OTP
        </a>

        <br><br>

        <p>
            Thanks,<br>
            Healix Hospital
        </p>

    </div>
    """

    return send_email(
        "OTP Verification - Healix Hospital",
        html,
        email
    )


# =========================
# BOOKING CONFIRMATION
# =========================
def send_booking_confirmation_email(appointment):

    try:

        email = appointment.patient.email

        html = f"""
        <div style="font-family: Arial; padding:20px;">

            <h2 style="color:#198754;">
                Appointment Confirmed
            </h2>

            <p>Hello <b>{appointment.patient.username}</b>,</p>

            <p>Your appointment has been confirmed.</p>

            <table style="
                border-collapse: collapse;
                width:100%;
            " border="1" cellpadding="10">

                <tr>
                    <th>Doctor</th>
                    <td>
                        Dr. {appointment.doctor.first_name}
                    </td>
                </tr>

                <tr>
                    <th>Date</th>
                    <td>
                        {appointment.appointment_date}
                    </td>
                </tr>

                <tr>
                    <th>Time</th>
                    <td>
                        {appointment.appointment_time}
                    </td>
                </tr>

            </table>

            <br>

            <p>
                Thank you for choosing
                Healix Hospital.
            </p>

        </div>
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

        html = f"""
        <div style="font-family: Arial; padding:20px;">

            <h2 style="color:#ffc107;">
                Appointment Reminder
            </h2>

            <p>Hello <b>{appointment.patient.username}</b>,</p>

            <p>
                This is a reminder for your appointment.
            </p>

            <table style="
                border-collapse: collapse;
                width:100%;
            " border="1" cellpadding="10">

                <tr>
                    <th>Doctor</th>
                    <td>
                        Dr. {appointment.doctor.first_name}
                    </td>
                </tr>

                <tr>
                    <th>Date</th>
                    <td>
                        {appointment.appointment_date}
                    </td>
                </tr>

                <tr>
                    <th>Time</th>
                    <td>
                        {appointment.appointment_time}
                    </td>
                </tr>

            </table>

            <br>

            <p>
                Healix Hospital
            </p>

        </div>
        """

        return send_email(
            "Appointment Reminder - Healix Hospital",
            html,
            email
        )

    except Exception as e:

        print("❌ REMINDER EMAIL ERROR:", str(e))

        return False