from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = "Create admin user if it does not exist"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "HMS-admin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@gmail.com")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "Hmsadmin@123")

        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Updated admin user: {username}"))
        else:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(self.style.SUCCESS(f"Created admin user: {username}"))