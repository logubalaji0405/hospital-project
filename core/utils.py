from django.core.mail import send_mail
from django.conf import settings
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings

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
    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,   # must be verified in SendGrid
        to_emails=email,
        subject="Healix HMS - OTP Verification",
        html_content=f"""
        <h2>Hello {username}</h2>
        <p>Your OTP is:</p>
        <h1 style="color:blue;">{otp}</h1>
        <p>This OTP is valid for 5 minutes.</p>
        """
    )

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print("✅ Email sent:", response.status_code)
    except Exception as e:
        print("❌ SendGrid Error:", str(e))
        raise e