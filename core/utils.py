from django.core.mail import send_mail
from django.conf import settings


def send_booking_confirmation_email(appointment):
    patient_email = appointment.patient.email

    if not patient_email:
        print("❌ Patient email missing")
        return False

    subject = "Appointment Confirmed"

    message = f"""
Hello {appointment.patient.first_name or appointment.patient.username},

Your appointment has been CONFIRMED.

Doctor: Dr. {appointment.doctor.first_name or appointment.doctor.username}
Date: {appointment.appointment_date}
Time: {appointment.appointment_time}
Reason: {appointment.reason}

Thank you,
Hospital Team
"""

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [patient_email],
            fail_silently=False,
        )
        print("✅ Email sent to:", patient_email)
        return True

    except Exception as e:
        print("❌ Email error:", e)
        return False


def send_reminder_email(appointment):
    patient_email = appointment.patient.email

    if not patient_email:
        print("❌ No email for reminder")
        return False

    subject = "Reminder: Appointment in 5 Minutes"

    message = f"""
Hello {appointment.patient.first_name or appointment.patient.username},

Your appointment will start in 5 minutes.

Doctor: Dr. {appointment.doctor.first_name or appointment.doctor.username}
Time: {appointment.appointment_time}

Please be ready.

Thanks,
Hospital Team
"""

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [patient_email],
            fail_silently=False,
        )
        print("✅ Reminder sent")
        return True

    except Exception as e:
        print("❌ Reminder error:", e)
        return False