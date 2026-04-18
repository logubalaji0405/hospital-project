from django.core.mail import send_mail
from django.conf import settings


def send_booking_confirmation_email(appointment):
    patient_email = appointment.patient.email

    if not patient_email:
        print("No patient email found")
        return False

    subject = "Your Appointment is Confirmed ✅"

    message = f"""
Dear {appointment.patient.first_name or appointment.patient.username},

We are pleased to inform you that your appointment has been successfully confirmed.

Appointment Details
-------------------
Doctor : Dr. {appointment.doctor.first_name or appointment.doctor.username}
Date   : {appointment.appointment_date}
Time   : {appointment.appointment_time}
Reason : {appointment.reason}

Please arrive at least 10 minutes before your scheduled appointment time.

If you need to reschedule or cancel your appointment, please contact us in advance.

Thank you for choosing our hospital.

Best regards,
Healix Hospital Management System
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
        print("Confirmation email error:", e)
        return False



def send_reminder_email(appointment):
    patient_email = appointment.patient.email

    if not patient_email:
        print("No patient email found for reminder")
        return False

    subject = "Reminder: Your Appointment Starts Soon ⏰"

    message = f"""
Hello {appointment.patient.first_name or appointment.patient.username},

This is a friendly reminder that your appointment will begin shortly.

Appointment Details
-------------------
Doctor : Dr. {appointment.doctor.first_name or appointment.doctor.username}
Date   : {appointment.appointment_date}
Time   : {appointment.appointment_time}
Reason : {appointment.reason}

Please make sure you are ready.

If you are unable to attend, kindly inform us as soon as possible.

Thank you,
Healix Hospital Management System
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
        print("Reminder email error:", e)
        return False