from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


class Profile(models.Model):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=20, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"



class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='patient_appointments'
    )
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_appointments'
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField()
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    reminder_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.patient.username} -> Dr. {self.doctor.username} on {self.appointment_date} {self.appointment_time}"

class ChatRoom(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_rooms')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('patient', 'doctor')

    def __str__(self):
        return f"{self.patient.username} ↔ {self.doctor.username}"


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.message[:30]}"


class Feedback(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
    

class Branch(models.Model):
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    description = models.TextField(blank=True, null=True)
    map_embed_url = models.URLField(help_text="Paste Google Maps embed URL")
    image = models.ImageField(upload_to='branches/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    def clean(self):
        if self.map_embed_url and "google.com/maps/embed" not in self.map_embed_url:
            raise ValidationError({
                "map_embed_url": "Please paste a valid Google Maps embed URL."
            })
    def __str__(self):
        return f"{self.name} - {self.city}"
    

class RegistrationOTP(models.Model):
    email = models.EmailField()
    username = models.CharField(max_length=150)
    otp = models.CharField(max_length=6)
    password = models.CharField(max_length=128)  # temporary store before account creation
    role = models.CharField(max_length=20, default='patient')
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        return f"{self.username} - {self.email} - {self.otp}"