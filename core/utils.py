from django.core.mail import send_mail
from django.conf import settings


def send_confirmation_email(appointment):
    patient_email = appointment.patient.email
    if not patient_email:
        print("Confirmation email failed: patient email missing")
        return False

    subject = "Appointment Confirmed - Healix HMS"
    message = f"""
Hello {appointment.patient.first_name or appointment.patient.username},

Your appointment has been confirmed.

Doctor: Dr. {appointment.doctor.first_name or appointment.doctor.username}
Date: {appointment.appointment_date}
Time: {appointment.appointment_time}
Problem: {appointment.problem}
Status: {appointment.status}

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

    print(f"Confirmation email sent for appointment #{appointment.id}")
    return True


def send_reminder_email(appointment):
    patient_email = appointment.patient.email
    if not patient_email:
        print("Reminder email failed: patient email missing")
        return False

    subject = "Reminder: Your Appointment Starts in 30 Minutes - Healix HMS"
    message = f"""
Hello {appointment.patient.first_name or appointment.patient.username},

This is a reminder that your appointment starts in 30 minutes.

Doctor: Dr. {appointment.doctor.first_name or appointment.doctor.username}
Date: {appointment.appointment_date}
Time: {appointment.appointment_time}
Problem: {appointment.problem}

Please be ready.

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

    print(f"Reminder email sent for appointment #{appointment.id}")
    return True