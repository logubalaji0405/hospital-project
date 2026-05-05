from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Appointment
from core.utils import send_reminder_email


class Command(BaseCommand):
    help = "Send reminder emails before appointment"

    def handle(self, *args, **kwargs):
        now = timezone.localtime()

        print("\n⏰ Current Time:", now)

        appointments = Appointment.objects.filter(
            status='confirmed',
            reminder_sent=False,
            appointment_date=now.date()
        )

        for a in appointments:
            appointment_time = datetime.combine(
                a.appointment_date,
                a.appointment_time
            )

            appointment_time = timezone.make_aware(
                appointment_time,
                timezone.get_current_timezone()
            )

            minutes_left = (appointment_time - now).total_seconds() / 60

            print(f"\n📌 Appointment ID: {a.id}")
            print("Minutes left:", minutes_left)

            # ✅ send before 10 mins (better than 5)
            if 0 < minutes_left <= 10:
                print("🚀 Sending reminder...")

                ok = send_reminder_email(a)

                if ok:
                    a.reminder_sent = True
                    a.save()
                    print("✅ Reminder sent")

                else:
                    print("❌ Failed to send")