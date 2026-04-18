import threading
import time
from django.core.management import call_command


def start():
    def run():
        while True:
            try:
                print("Running reminder scheduler...")
                call_command("send_reminders")
            except Exception as e:
                print("Scheduler error:", e)

            time.sleep(60)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()