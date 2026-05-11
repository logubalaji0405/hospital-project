from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Appointment
from core.utils import send_reminder_email


class Command(BaseCommand):
    help = "Send reminder emails 24 hours before appointment"

    def handle(self, *args, **kwargs):
        now = timezone.localtime()

        target_start = now + timedelta(hours=24)
        target_end = target_start + timedelta(minutes=5)

        self.stdout.write(f"Current time: {now}")
        self.stdout.write(f"Checking between: {target_start} and {target_end}")

        appointments = Appointment.objects.filter(
            status="confirmed",
            reminder_sent=False,
            appointment_date__gte=now.date()
        ).select_related("patient", "doctor")

        found = 0
        sent = 0

        for appointment in appointments:
            appointment_datetime = datetime.combine(
                appointment.appointment_date,
                appointment.appointment_time
            )

            if timezone.is_naive(appointment_datetime):
                appointment_datetime = timezone.make_aware(
                    appointment_datetime,
                    timezone.get_current_timezone()
                )

            self.stdout.write(
                f"Checking appointment #{appointment.id}: {appointment_datetime}"
            )

            if target_start <= appointment_datetime <= target_end:
                found += 1

                ok = send_reminder_email(appointment)

                if ok:
                    appointment.reminder_sent = True
                    appointment.save(update_fields=["reminder_sent"])
                    sent += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ 24-hour reminder sent for #{appointment.id}")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Reminder failed for #{appointment.id}")
                    )

        self.stdout.write(f"Matching: {found}")
        self.stdout.write(f"Sent: {sent}")