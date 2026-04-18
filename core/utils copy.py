from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client


def send_confirmation_email(appointment):
    patient_email = appointment.patient.email
    if not patient_email:
        return False

    subject = "Appointment Confirmed - Healix HMS"
    message = f"""
Hello {appointment.patient.first_name or appointment.patient.username},

Your appointment has been confirmed.

Doctor: Dr. {appointment.doctor.first_name or appointment.doctor.username}
Date: {appointment.appointment_date}
Time: {appointment.appointment_time}
Problem: {appointment.problem}

Thank you,
Healix HMS
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [patient_email],
        fail_silently=False,
    )
    return True



def send_appointment_whatsapp(appointment):
    try:
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )

        phone = appointment.patient.profile.phone
        print("Sending to:", phone)

        message = client.messages.create(
            body=(
                f"Hello {appointment.patient.first_name or appointment.patient.username}, "
                f"your appointment is confirmed with Dr. "
                f"{appointment.doctor.first_name or appointment.doctor.username} "
                f"on {appointment.appointment_date} at {appointment.appointment_time}."
            ),
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{phone}"
        )

        print("WhatsApp sent successfully:", message.sid)
        return True

    except Exception as e:
        print("WhatsApp send error:", e)
        return False