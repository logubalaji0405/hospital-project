from django.core.mail import send_mail
from django.conf import settings


def send_booking_confirmation_email(appointment):
    patient_email = appointment.patient.email

    if not patient_email:
        print("Patient email is empty. Mail not sent.")
        return False

    subject = "Appointment Confirmed"
    message = f"""
Hello {appointment.patient.first_name or appointment.patient.username},

Your appointment has been confirmed successfully.

Doctor: Dr. {appointment.doctor.first_name or appointment.doctor.username}
Date: {appointment.appointment_date}
Time: {appointment.appointment_time}
Reason: {appointment.reason}
Status: {appointment.status}

Thank you,
Hospital Management Team
"""

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [patient_email],
            fail_silently=False,
        )
        print(f"Confirmation email sent to {patient_email}")
        return True
    except Exception as e:
        print("Email sending error:", e)
        return False


def send_reminder_email(appointment):
    patient_email = appointment.patient.email

    if not patient_email:
        print("Patient email is empty. Reminder not sent.")
        return False

    subject = "Appointment Reminder - 5 Minutes Left"
    message = f"""
Hello {appointment.patient.first_name or appointment.patient.username},

This is a reminder that your appointment will start in 5 minutes.

Doctor: Dr. {appointment.doctor.first_name or appointment.doctor.username}
Date: {appointment.appointment_date}
Time: {appointment.appointment_time}
Reason: {appointment.reason}

Please be ready.

Thank you,
Hospital Management Team
"""

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [patient_email],
            fail_silently=False,
        )
        print(f"Reminder email sent to {patient_email}")
        return True
    except Exception as e:
        print("Reminder email sending error:", e)
        return False