import random
import time
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse


# 🔁 SAFE SEND (fix Render network issue)
def safe_send_email(msg):
    for i in range(3):
        try:
            msg.send()
            print("✅ Email sent")
            return True
        except Exception as e:
            print(f"Retry {i+1}:", e)
            time.sleep(5)
    return False


# 🎯 COMMON EMAIL BUILDER (ANTI-SPAM)
def build_email(subject, text_content, html_content, to_email):
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [to_email]
    )

    msg.attach_alternative(html_content, "text/html")

    msg.extra_headers = {
        "Reply-To": settings.DEFAULT_FROM_EMAIL,
        "X-Mailer": "Healix HMS",
    }

    return msg


# 🔐 OTP GENERATOR
def generate_otp():
    return str(random.randint(100000, 999999))


# 📩 OTP EMAIL
def send_registration_otp(email, otp, username):
    verify_url = settings.SITE_URL + reverse("verify_register_otp")

    subject = "Your Healix OTP (Valid 5 mins)"

    text_content = f"""
Hello {username},

Your OTP is: {otp}

Verify here:
{verify_url}

Healix Hospital
"""

    html_content = f"""
<h2>Healix Hospital</h2>
<p>Hello <b>{username}</b>,</p>
<p>Your OTP is:</p>
<h1>{otp}</h1>

<p><a href="{verify_url}">Verify Now</a></p>

<hr>
<p>Healix Hospital</p>
"""

    msg = build_email(subject, text_content, html_content, email)
    return safe_send_email(msg)


# 📅 BOOKING EMAIL
def send_booking_confirmation_email(appointment):
    email = appointment.patient.email

    subject = "Appointment Confirmed - Healix Hospital"

    text_content = f"""
Hello {appointment.patient.first_name},

Your appointment is confirmed.

Doctor: Dr. {appointment.doctor.first_name}
Date: {appointment.appointment_date}
Time: {appointment.appointment_time}

Healix Hospital
"""

    html_content = f"""
<h2>Healix Hospital</h2>
<p>Hello <b>{appointment.patient.first_name}</b>,</p>

<p>Your appointment is confirmed.</p>

<ul>
<li><b>Doctor:</b> Dr. {appointment.doctor.first_name}</li>
<li><b>Date:</b> {appointment.appointment_date}</li>
<li><b>Time:</b> {appointment.appointment_time}</li>
</ul>

<hr>
<p>Healix Hospital</p>
"""

    msg = build_email(subject, text_content, html_content, email)
    return safe_send_email(msg)


# ⏰ REMINDER EMAIL
def send_reminder_email(appointment):
    email = appointment.patient.email

    subject = "Reminder: Your Appointment Today"

    text_content = f"""
Hello {appointment.patient.first_name},

Reminder for your appointment:

Doctor: Dr. {appointment.doctor.first_name}
Time: {appointment.appointment_time}

Healix Hospital
"""

    html_content = f"""
<h2>Healix Hospital</h2>
<p>Hello <b>{appointment.patient.first_name}</b>,</p>

<p>This is your appointment reminder.</p>

<ul>
<li><b>Doctor:</b> Dr. {appointment.doctor.first_name}</li>
<li><b>Time:</b> {appointment.appointment_time}</li>
</ul>

<hr>
<p>Healix Hospital</p>
"""

    msg = build_email(subject, text_content, html_content, email)
    return safe_send_email(msg)