from django.core.mail import send_mail
from django.conf import settings
import random


def send_booking_confirmation_email(appointment):
    patient_email = appointment.patient.email

    if not patient_email:
        print("No patient email found")
        return False

    subject = "✅ Appointment Confirmed | Healix Hospital"

    message = f"""
Dear {appointment.patient.first_name or appointment.patient.username},

🎉 Your appointment has been successfully confirmed!

━━━━━━━━━━━━━━━━━━━━━━━
📋 APPOINTMENT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━
👨‍⚕️ Doctor   : Dr. {appointment.doctor.first_name or appointment.doctor.username}
📅 Date     : {appointment.appointment_date}
⏰ Time     : {appointment.appointment_time}
📝 Reason   : {appointment.reason}

━━━━━━━━━━━━━━━━━━━━━━━

⏳ Please arrive at least 10 minutes before your scheduled time.

📌 Need help?
• Reschedule or cancel your appointment anytime.
• Contact us for any assistance.

💙 Thank you for trusting Healix Hospital.
We are committed to your care and well-being.

Warm regards,  
Healix Hospital Team
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

    subject = "⏰ Reminder: Upcoming Appointment | Healix Hospital"

    message = f"""
Hello {appointment.patient.first_name or appointment.patient.username},

🔔 This is a reminder for your upcoming appointment.

━━━━━━━━━━━━━━━━━━━━━━━
📋 APPOINTMENT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━
👨‍⚕️ Doctor   : Dr. {appointment.doctor.first_name or appointment.doctor.username}
📅 Date     : {appointment.appointment_date}
⏰ Time     : {appointment.appointment_time}
📝 Reason   : {appointment.reason}

━━━━━━━━━━━━━━━━━━━━━━━

📌 Please ensure you arrive on time.

⚠️ If you are unable to attend:
• Kindly reschedule or cancel in advance.

💙 We look forward to serving you and ensuring your health.

Best regards,  
Healix Hospital Team
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
    


def generate_otp():
    return str(random.randint(100000, 999999))



def send_registration_otp(email, otp, username):
    subject = "Healix HMS OTP"

    message = f"""
Hello {username},

Your OTP is: {otp}

Valid for 5 minutes.
"""

    try:
        # If env vars missing → skip email safely
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            print("⚠ Email not configured, OTP:", otp)
            return

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=True  # 🔥 IMPORTANT: prevent crash
        )

        print("✅ Email sent")

    except Exception as e:
        print("❌ Email error:", e)
        # DO NOT raise → prevents 502 crash