from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse, HttpResponseForbidden

from .models import Profile, Appointment, ChatMessage, ChatRoom, Feedback
from .utils import send_booking_confirmation_email
from datetime import datetime
from django.http import HttpResponse
from django.utils import timezone
from .utils import send_reminder_email

def home(request):
    return render(request, 'home.html')


def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        role = request.POST.get('role', 'patient').strip()
        department = request.POST.get('department', '').strip()

        if not first_name or not username or not email or not password1 or not password2:
            messages.error(request, "Please fill all required fields.")
            return redirect('register')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        if role == 'doctor' and not department:
            messages.error(request, "Department is required for doctor registration.")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            email=email,
            password=password1
        )

        Profile.objects.create(
            user=user,
            role=role,
            phone=phone,
            department=department if role == 'doctor' else '',
            is_approved=False if role == 'doctor' else True
        )

        messages.success(request, "Registration successful. Please login.")
        return redirect('login')

    return render(request, 'register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

        profile, _ = Profile.objects.get_or_create(
            user=user,
            defaults={
                'role': 'admin' if user.is_superuser else 'patient',
                'is_approved': True
            }
        )

        if profile.role == 'doctor' and not profile.is_approved:
            messages.error(request, "Doctor account is waiting for admin approval.")
            return redirect('login')

        login(request, user)
        messages.success(request, "Login successful.")
        return redirect('home')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')


@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'profile.html', {
        'profile': profile,
        'role': profile.role
    })


@login_required
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        profile.phone = request.POST.get('phone', '')
        profile.age = request.POST.get('age') or None
        profile.address = request.POST.get('address', '')

        if profile.role == 'doctor':
            profile.department = request.POST.get('department', '')
            profile.description = request.POST.get('description', '')

        if request.FILES.get('profile_image'):
            profile.profile_image = request.FILES.get('profile_image')

        profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')

    return render(request, 'edit_profile.html', {'profile': profile})


@login_required
def patient_dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.role != 'patient':
        return redirect('home')

    doctors = Profile.objects.filter(
        role='doctor',
        is_approved=True
    ).select_related('user')[:6]

    total_doctors = Profile.objects.filter(role='doctor', is_approved=True).count()
    my_bookings = Appointment.objects.filter(patient=request.user).count()
    upcoming = Appointment.objects.filter(
        patient=request.user
    ).order_by('appointment_date', 'appointment_time')[:5]
    history = Appointment.objects.filter(
        patient=request.user
    ).order_by('-created_at')[:6]

    context = {
        'total_doctors': total_doctors,
        'my_bookings': my_bookings,
        'upcoming': upcoming,
        'history': history,
        'doctors': doctors,
    }
    return render(request, 'patient_dashboard.html', context)


@login_required
def doctor_dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.role != 'doctor':
        return redirect('home')

    total_bookings = Appointment.objects.filter(doctor=request.user).count()
    pending_bookings = Appointment.objects.filter(doctor=request.user, status='pending').count()
    confirmed_bookings = Appointment.objects.filter(doctor=request.user, status='confirmed').count()
    appointments = Appointment.objects.filter(doctor=request.user).order_by('-created_at')

    return render(request, 'doctor_dashboard.html', {
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'appointments': appointments,
    })


@login_required
def admin_dashboard(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            'role': 'admin' if request.user.is_superuser else 'patient',
            'is_approved': True
        }
    )

    if profile.role != 'admin':
        return redirect('home')

    pending_doctors = Profile.objects.filter(role='doctor', is_approved=False)
    total_patients = Profile.objects.filter(role='patient').count()
    total_doctors = Profile.objects.filter(role='doctor', is_approved=True).count()
    total_appointments = Appointment.objects.count()
    daily_stats = Appointment.objects.values('appointment_date').annotate(
        total=Count('id')
    ).order_by('-appointment_date')[:7]

    return render(request, 'admin_dashboard.html', {
        'pending_doctors': pending_doctors,
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
        'daily_stats': daily_stats,
    })


@login_required
def book_appointment(request):
    doctors = User.objects.filter(
        profile__role='doctor',
        profile__is_approved=True
    ).select_related('profile')

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')

        if not doctor_id or not appointment_date or not appointment_time or not reason:
            messages.error(request, "All fields are required.")
            return render(request, 'book_appointment.html', {'doctors': doctors})

        try:
            doctor = User.objects.get(
                id=doctor_id,
                profile__role='doctor',
                profile__is_approved=True
            )

            appointment = Appointment.objects.create(
                patient=request.user,
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                reason=reason,
                status='pending',
                reminder_sent=False
            )

            try:
                send_booking_confirmation_email(appointment)
                messages.success(request, "Appointment booked successfully. Confirmation email sent.")
            except Exception as e:
                print("Booking confirmation email failed:", e)
                messages.success(request, "Appointment booked successfully, but email was not sent.")

            return redirect('booking_history')

        except User.DoesNotExist:
            messages.error(request, "Doctor not found.")
        except Exception as e:
            messages.error(request, f"Booking failed: {str(e)}")

    return render(request, 'book_appointment.html', {'doctors': doctors})


@login_required
def booking_history(request):
    appointments = Appointment.objects.filter(
        patient=request.user
    ).order_by('-appointment_date', '-appointment_time')
    return render(request, 'booking_history.html', {'appointments': appointments})


@login_required
def confirm_booking(request, appointment_id):
    profile = get_object_or_404(Profile, user=request.user)

    if profile.role != 'doctor':
        return redirect('home')

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        doctor=request.user
    )

    appointment.status = 'confirmed'
    appointment.reminder_sent = False
    appointment.save()

    print("👉 Confirm clicked")
    print("👉 Patient email:", appointment.patient.email)

    email_ok = send_booking_confirmation_email(appointment)

    if email_ok:
        messages.success(request, "✅ Appointment confirmed & email sent")
    else:
        messages.warning(request, "⚠️ Appointment confirmed but email failed")

    return redirect('doctor_dashboard')
    

@login_required
def reject_booking(request, appointment_id):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.role != 'doctor':
        return redirect('home')

    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    appointment.status = 'rejected'
    appointment.save()

    messages.success(request, "Appointment rejected.")
    return redirect('doctor_dashboard')


@login_required
def approve_doctor(request, profile_id):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.role != 'admin':
        return redirect('home')

    doctor_profile = get_object_or_404(Profile, id=profile_id, role='doctor')
    doctor_profile.is_approved = True
    doctor_profile.save()

    messages.success(request, "Doctor approved successfully.")
    return redirect('admin_dashboard')


@login_required
def doctor_list(request):
    if request.user.profile.role != 'patient':
        return redirect('home')

    doctors = User.objects.filter(
        profile__role='doctor',
        profile__is_approved=True
    ).select_related('profile')

    return render(request, 'chat/doctor_list.html', {'doctors': doctors})


@login_required
def start_chat(request, doctor_id):
    if request.user.profile.role != 'patient':
        return HttpResponseForbidden("Only patients can start chat.")

    doctor = get_object_or_404(
        User,
        id=doctor_id,
        profile__role='doctor',
        profile__is_approved=True
    )

    room, created = ChatRoom.objects.get_or_create(
        patient=request.user,
        doctor=doctor
    )

    return redirect('chat_room', room_id=room.id)


@login_required
def my_chats(request):
    if request.user.profile.role == 'patient':
        rooms = ChatRoom.objects.filter(patient=request.user).select_related(
            'doctor', 'patient', 'doctor__profile'
        )
    elif request.user.profile.role == 'doctor':
        rooms = ChatRoom.objects.filter(doctor=request.user).select_related(
            'doctor', 'patient', 'patient__profile'
        )
    else:
        rooms = ChatRoom.objects.none()

    room_list = []
    for room in rooms:
        unread_count = room.messages.filter(is_read=False).exclude(sender=request.user).count()
        last_message = room.messages.order_by('-timestamp').first()
        other_user = room.doctor if request.user == room.patient else room.patient

        room_list.append({
            'room': room,
            'other_user': other_user,
            'unread_count': unread_count,
            'last_message': last_message,
        })

    return render(request, 'chat/my_chats.html', {'room_list': room_list})


@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom.objects.select_related('patient', 'doctor'), id=room_id)

    if request.user != room.patient and request.user != room.doctor:
        return HttpResponseForbidden("You are not allowed to access this chat.")

    other_user = room.doctor if request.user == room.patient else room.patient
    room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    return render(request, 'chat/chat_room.html', {
        'room': room,
        'other_user': other_user,
    })


@login_required
@require_GET
def get_messages(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    if request.user != room.patient and request.user != room.doctor:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    messages_qs = room.messages.select_related('sender').order_by('timestamp')

    data = []
    for msg in messages_qs:
        data.append({
            'id': msg.id,
            'message': msg.message,
            'sender': msg.sender.username,
            'sender_id': msg.sender.id,
            'is_me': msg.sender_id == request.user.id,
            'timestamp': msg.timestamp.strftime('%d %b %Y, %I:%M %p'),
        })

    return JsonResponse({'messages': data})


@login_required
@require_POST
def send_message(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    if request.user != room.patient and request.user != room.doctor:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    message_text = request.POST.get('message', '').strip()
    if not message_text:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)

    msg = ChatMessage.objects.create(
        room=room,
        sender=request.user,
        message=message_text
    )

    return JsonResponse({
        'success': True,
        'id': msg.id,
        'message': msg.message,
        'sender': msg.sender.username,
        'sender_id': msg.sender.id,
        'is_me': True,
        'timestamp': msg.timestamp.strftime('%d %b %Y, %I:%M %p'),
    })


@login_required
@require_GET
def chat_notification_count(request):
    if request.user.profile.role == 'patient':
        rooms = ChatRoom.objects.filter(patient=request.user)
    elif request.user.profile.role == 'doctor':
        rooms = ChatRoom.objects.filter(doctor=request.user)
    else:
        rooms = ChatRoom.objects.none()

    unread = ChatMessage.objects.filter(
        room__in=rooms,
        is_read=False
    ).exclude(sender=request.user).count()

    return JsonResponse({'unread_count': unread})


def about(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Please login as patient to submit feedback.")
            return redirect('login')

        patient_profile = get_object_or_404(Profile, user=request.user)
        if patient_profile.role != 'patient':
            messages.error(request, "Only patients can submit feedback.")
            return redirect('about')

        name = request.POST.get('name', '').strip() or request.user.first_name or request.user.username
        email = request.POST.get('email', '').strip() or request.user.email
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        rating = request.POST.get('rating', '5')

        if not name or not email or not subject or not message:
            messages.error(request, "Please fill all fields.")
            return redirect('about')

        Feedback.objects.create(
            patient=request.user,
            name=name,
            email=email,
            subject=subject,
            message=message,
            rating=int(rating)
        )

        messages.success(request, "Feedback submitted successfully.")
        return redirect('about')

    feedback_list = Feedback.objects.order_by('-created_at')[:6]
    return render(request, 'about.html', {'feedback_list': feedback_list})


@login_required
def feedback_list(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.role != 'admin':
        return redirect('home')

    feedbacks = Feedback.objects.select_related('patient').order_by('-created_at')
    return render(request, 'feedback_list.html', {'feedbacks': feedbacks})


def run_reminders(request):
    secret_key = request.GET.get("key")

    if secret_key != "mysecret123":
        return HttpResponse("Unauthorized", status=403)

    now = timezone.localtime()

    appointments = Appointment.objects.filter(
        status='confirmed',
        reminder_sent=False,
        appointment_date=now.date()
    ).select_related('patient', 'doctor')

    found = 0
    sent = 0

    for appointment in appointments:
        appointment_datetime = datetime.combine(
            appointment.appointment_date,
            appointment.appointment_time
        )

        appointment_datetime = timezone.make_aware(
            appointment_datetime,
            timezone.get_current_timezone()
        )

        minutes_left = (appointment_datetime - now).total_seconds() / 60

        print("Appointment ID:", appointment.id)
        print("Minutes left:", minutes_left)
        print("Status:", appointment.status)
        print("Reminder sent:", appointment.reminder_sent)
        print("Patient email:", appointment.patient.email)

        if 0 < minutes_left <= 15:
            found += 1

            ok = send_reminder_email(appointment)

            if ok:
                appointment.reminder_sent = True
                appointment.save()
                sent += 1
                print(f"Reminder sent for appointment #{appointment.id}")
            else:
                print(f"Reminder failed for appointment #{appointment.id}")

    return HttpResponse(f"Matching appointments found: {found}, Reminders sent: {sent}")