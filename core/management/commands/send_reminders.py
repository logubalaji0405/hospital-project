from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Appointment
from core.utils import send_reminder_email


class Command(BaseCommand):
    help = "Send reminder emails 5 minutes before appointment"

    def handle(self, *args, **kwargs):
        now = timezone.localtime()
        target_start = now + timedelta(minutes=3)
        target_end = now + timedelta(minutes=7)

        self.stdout.write(f"Current time: {now}")
        self.stdout.write(f"Checking appointments between: {target_start} and {target_end}")

        appointments = Appointment.objects.filter(
            status='confirmed',
            reminder_sent=False
        ).select_related('patient', 'doctor')

        found = 0
        sent = 0

        for appointment in appointments:
            appointment_datetime = datetime.combine(
                appointment.appointment_date,
                appointment.appointment_time
            )

            current_tz = timezone.get_current_timezone()
            appointment_datetime = timezone.make_aware(appointment_datetime, current_tz)

            if target_start <= appointment_datetime <= target_end:
                found += 1
                try:
                    send_reminder_email(appointment)
                    appointment.reminder_sent = True
                    appointment.save()

                    sent += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Reminder sent for appointment #{appointment.id} to {appointment.patient.email}"
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Failed to send reminder for appointment #{appointment.id}: {str(e)}"
                        )
                    )

        self.stdout.write(self.style.SUCCESS(f"Matching appointments found: {found}"))
        self.stdout.write(self.style.SUCCESS(f"Reminders sent: {sent}"))