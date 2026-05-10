from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import traceback
import random


def send_email(subject, html_content, to_email):
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )

        msg.attach_alternative(html_content, "text/html")

        result = msg.send(fail_silently=True)

        print("✅ EMAIL SENT:", result)

        return True

    except Exception as e:
        print("❌ EMAIL ERROR:", str(e))
        traceback.print_exc()

        return False


def generate_otp():
    return str(random.randint(100000, 999999))


def send_registration_otp(email, otp, username):

    html = f"""
    <h2>Healix Hospital OTP Verification</h2>

    <p>Hello {username},</p>

    <p>Your OTP is:</p>

    <h1>{otp}</h1>

    <p>This OTP is valid for 5 minutes.</p>

    <br>

    <p>Healix Hospital Team</p>
    """

    return send_email(
        "OTP Verification - Healix Hospital",
        html,
        email
    )


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