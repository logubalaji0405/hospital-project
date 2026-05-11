import random
import requests
from django.conf import settings


def generate_otp():
    return str(random.randint(100000, 999999))


def send_brevo_email(to_email, to_name, subject, html_content):
    try:
        url = "https://api.brevo.com/v3/smtp/email"

        payload = {
            "sender": {
                "name": "Healix Hospital",
                "email": settings.DEFAULT_FROM_EMAIL
            },
            "to": [
                {
                    "email": to_email,
                    "name": to_name
                }
            ],
            "subject": subject,
            "htmlContent": html_content
        }

        headers = {
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        print("BREVO STATUS:", response.status_code)
        print("BREVO RESPONSE:", response.text)

        return response.status_code in [200, 201, 202]

    except Exception as e:
        print("BREVO ERROR:", e)
        return False


def send_registration_otp(email, otp, username):
    html = f"""
    <h2>Healix Hospital OTP Verification</h2>
    <p>Hello {username},</p>
    <p>Your OTP is:</p>
    <h1 style="color:#0d6efd;">{otp}</h1>
    <p>This OTP is valid for 5 minutes.</p>
    <br>
    <p>Healix Hospital Team</p>
    """

    return send_brevo_email(
        email,
        username,
        "OTP Verification - Healix Hospital",
        html
    )


def send_booking_confirmation_email(appointment):
    html = f"""
    <h2>✅ Appointment Confirmed</h2>
    <p>Hello {appointment.patient.first_name or appointment.patient.username},</p>
    <p>Your appointment has been confirmed successfully.</p>

    <p><b>Doctor:</b> Dr. {appointment.doctor.first_name or appointment.doctor.username}</p>
    <p><b>Date:</b> {appointment.appointment_date}</p>
    <p><b>Time:</b> {appointment.appointment_time}</p>
    <p><b>Reason:</b> {appointment.reason}</p>

    <p>Please arrive 10 minutes before your appointment time.</p>
    <br>
    <p>Healix Hospital Team</p>
    """

    return send_brevo_email(
        appointment.patient.email,
        appointment.patient.username,
        "Appointment Confirmed - Healix Hospital",
        html
    )


def send_booking_rejected_email(appointment):
    html = f"""
    <h2>❌ Appointment Rejected</h2>
    <p>Hello {appointment.patient.first_name or appointment.patient.username},</p>
    <p>Sorry, your appointment request has been rejected.</p>

    <p><b>Doctor:</b> Dr. {appointment.doctor.first_name or appointment.doctor.username}</p>
    <p><b>Date:</b> {appointment.appointment_date}</p>
    <p><b>Time:</b> {appointment.appointment_time}</p>
    <p><b>Reason:</b> {appointment.reason}</p>

    <p>Please book another available appointment slot.</p>
    <br>
    <p>Healix Hospital Team</p>
    """

    return send_brevo_email(
        appointment.patient.email,
        appointment.patient.username,
        "Appointment Rejected - Healix Hospital",
        html
    )


def send_reminder_email(appointment):
    html = f"""
    <h2>⏰ Appointment Reminder</h2>
    <p>Hello {appointment.patient.first_name or appointment.patient.username},</p>
    <p>This is a reminder for your upcoming appointment.</p>

    <p><b>Doctor:</b> Dr. {appointment.doctor.first_name or appointment.doctor.username}</p>
    <p><b>Date:</b> {appointment.appointment_date}</p>
    <p><b>Time:</b> {appointment.appointment_time}</p>
    <p><b>Reason:</b> {appointment.reason}</p>

    <p>Please arrive 10 minutes early.</p>
    <br>
    <p>Healix Hospital Team</p>
    """

    return send_brevo_email(
        appointment.patient.email,
        appointment.patient.username,
        "Appointment Reminder - Healix Hospital",
        html
    )