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

        found = 0
        sent = 0

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
            print("Time:", appointment_time)
            print("Minutes left:", minutes_left)
            print("Status:", a.status)
            print("Reminder sent:", a.reminder_sent)

            # ✅ MAIN CONDITION
            if 0 < minutes_left <= 5:
                found += 1

                ok = send_reminder_email(a)

                if ok:
                    a.reminder_sent = True
                    a.save()
                    sent += 1
                    print("✅ Reminder sent successfully")
                else:
                    print("❌ Failed to send")

        print("\n🔍 Matching:", found)
        print("📧 Sent:", sent)