from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings
import traceback
import random
import requests

def send_email(subject, html_content, to_email):
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_content, "text/html")
        result = msg.send(fail_silently=False)
        print("✅ EMAIL SENT:", result)
        return True
    except Exception as e:
        print("❌ EMAIL ERROR:", str(e))
        traceback.print_exc()
        return False


def generate_otp():
    return str(random.randint(100000, 999999))



def send_registration_otp(email, otp, username):
    try:
        url = "https://api.brevo.com/v3/smtp/email"

        payload = {
            "sender": {
                "name": "Healix Hospital",
                "email": settings.DEFAULT_FROM_EMAIL
            },
            "to": [
                {
                    "email": email,
                    "name": username
                }
            ],
            "subject": "OTP Verification - Healix Hospital",
            "htmlContent": f"""
                <h2>Healix Hospital OTP Verification</h2>
                <p>Hello {username},</p>
                <p>Your OTP is:</p>
                <h1>{otp}</h1>
                <p>This OTP is valid for 5 minutes.</p>
                <br>
                <p>Healix Hospital Team</p>
            """
        }

        headers = {
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        print("BREVO API STATUS:", response.status_code)
        print("BREVO API RESPONSE:", response.text)

        return response.status_code in [200, 201, 202]

    except Exception as e:
        print("BREVO API ERROR:", e)
        return False


def send_booking_confirmation_email(appointment):
    try:
        subject = "Appointment Confirmed | Healix Hospital"

        message = f"""
Hello {appointment.patient.first_name or appointment.patient.username},

Your appointment has been confirmed.

Doctor: Dr. {appointment.doctor.first_name or appointment.doctor.username}
Date: {appointment.appointment_date}
Time: {appointment.appointment_time}

Thank you,
Healix Hospital
"""

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.patient.email],
            fail_silently=True,
        )

        print("✅ Confirmation email sent")
        return True

    except Exception as e:
        print("❌ Confirmation email error:", e)
        return False


def send_reminder_email(appointment):
    try:
        subject = "Appointment Reminder | Healix Hospital"

        message = f"""
Hello {appointment.patient.first_name or appointment.patient.username},

Reminder for your appointment.

Doctor: Dr. {appointment.doctor.first_name or appointment.doctor.username}
Date: {appointment.appointment_date}
Time: {appointment.appointment_time}

Thank you,
Healix Hospital
"""

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.patient.email],
            fail_silently=True,
        )

        print("✅ Reminder email sent")
        return True

    except Exception as e:
        print("❌ Reminder email error:", e)
        return False