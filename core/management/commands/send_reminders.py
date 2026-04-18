from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Appointment
from core.utils import send_reminder_email


class Command(BaseCommand):
    help = "Send reminder emails 5 minutes before appointment"

    def handle(self, *args, **kwargs):
        now = timezone.localtime()
        target_start = now + timedelta(minutes=29)
        target_end = now + timedelta(minutes=31)

        print("Current time:", now)
        print("Checking between:", target_start, "and", target_end)

        appointments = Appointment.objects.filter(
            status='confirmed',
            reminder_sent=False
        ).select_related('patient', 'doctor')

        found = 0

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

            print(
                f"Checking appointment #{appointment.id} | "
                f"{appointment_datetime} | "
                f"status={appointment.status} | "
                f"reminder_sent={appointment.reminder_sent}"
            )

            if target_start <= appointment_datetime <= target_end:
                found += 1
                print(f"Matched appointment #{appointment.id}")

                try:
                    ok = send_reminder_email(appointment)
                    if ok:
                        appointment.reminder_sent = True
                        appointment.save()
                        print(f"Reminder sent for appointment #{appointment.id}")
                except Exception as e:
                    print(f"Reminder failed for appointment #{appointment.id}: {e}")

        if found == 0:
            print("No appointments found in 5-minute reminder window.")
        else:
            print("Reminder check completed.")