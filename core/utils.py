from django.core.mail import send_mail
from django.conf import settings


def send_booking_confirmation_email(appointment):
    if not appointment.patient.email:
        return False

    subject = "Appointment Booking Confirmation"
    message = f"""
Hello {appointment.patient.first_name or appointment.patient.username},

Your appointment has been booked successfully.

Doctor: Dr. {appointment.doctor.first_name or appointment.doctor.username}
Date: {appointment.appointment_date}
Time: {appointment.appointment_time}
Reason: {appointment.reason}
Status: {appointment.status}

Thank you.
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.patient.email],
        fail_silently=False,
    )
    return True


def send_reminder_email(appointment):
    if not appointment.patient.email:
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

Thank you.
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.patient.email],
        fail_silently=False,
    )
    return True