from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Avg, Count, Q
from .models import Profile, Appointment, ChatMessage, ChatRoom,RegistrationOTP, Feedback,Branch
from .utils import send_booking_confirmation_email
from datetime import datetime
from django.http import HttpResponse
from django.utils import timezone
import random
from .utils import send_reminder_email
from .utils import generate_otp, send_registration_otp
from django.contrib.auth.hashers import make_password

def home(request):
    return render(request, 'home.html')

from django.shortcuts import render

def doctor_pending(request):
    return render(request, "doctor_pending.html")

def register_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username exists")
            return redirect("register")

        otp = generate_otp()

        RegistrationOTP.objects.filter(email=email).delete()

        RegistrationOTP.objects.create(
            first_name=first_name,
            username=username,
            email=email,
            password=password,
            otp=otp
        )

        request.session["register_email"] = email

        try:
            send_registration_otp(email, otp, username)
            messages.success(request, "OTP sent to email")
        except Exception:
            messages.warning(request, f"OTP: {otp}")  # fallback

        return redirect("verify_register_otp")

    return render(request, "register.html")


def resend_register_otp_view(request):
    email = request.session.get("register_email")

    if not email:
        return redirect("register")

    otp_entry = RegistrationOTP.objects.filter(email=email).first()

    if not otp_entry:
        return redirect("register")

    otp = generate_otp()
    otp_entry.otp = otp
    otp_entry.save()

    try:
        send_registration_otp(email, otp, otp_entry.username)
        messages.success(request, "OTP resent")
    except:
        messages.warning(request, f"OTP: {otp}")

    return redirect("verify_register_otp")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            profile = getattr(user, "profile", None)

            if profile and profile.role == "doctor" and not profile.is_approved:
                return render(request, "doctor_pending_approval.html")

            login(request, user)

            if profile:
                if profile.role == "admin":
                    return redirect("home")
                elif profile.role == "doctor":
                    return redirect("home")
                else:
                    return redirect("home")

            return redirect("home")

        messages.error(request, "Invalid username or password")

    return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")

@login_required
def approve_doctor(request, doctor_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('home')

    doctor = get_object_or_404(Profile, id=doctor_id, role='doctor')
    doctor.is_approved = True
    doctor.save()

    messages.success(request, f"{doctor.user.username} approved successfully.")
    return redirect('admin_dashboard')


@login_required
def reject_doctor(request, doctor_id):
    if not hasattr(request.user, "profile") or request.user.profile.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("home")

    doctor = get_object_or_404(Profile, id=doctor_id, role="doctor")
    username = doctor.user.username
    doctor.user.delete()

    messages.success(request, f"{username} rejected successfully.")
    return redirect("admin_dashboard")

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
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('home')

    total_patients = Profile.objects.filter(role='patient').count()
    total_doctors = Profile.objects.filter(role='doctor', is_approved=True).count()
    total_appointments = Appointment.objects.count()

    pending_doctors = Profile.objects.filter(role='doctor', is_approved=False).select_related('user')
    approved_doctors = Profile.objects.filter(role='doctor', is_approved=True).select_related('user')
    recent_patients = Profile.objects.filter(role='patient').select_related('user').order_by('-id')[:6]

    today = timezone.localdate()
    today_appointments = Appointment.objects.filter(
        appointment_date=today
    ).select_related('patient', 'doctor').order_by('appointment_time')

    today_appointments_count = today_appointments.count()
    confirmed_appointments = Appointment.objects.filter(status='confirmed').count()
    pending_appointments = Appointment.objects.filter(status='pending').count()

    daily_stats = Appointment.objects.values('appointment_date').annotate(
        total=Count('id')
    ).order_by('-appointment_date')[:10]

    daily_stats = list(daily_stats)[::-1]

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
        'pending_doctors': pending_doctors,
        'approved_doctors': approved_doctors,
        'recent_patients': recent_patients,
        'today_appointments': today_appointments,
        'today_appointments_count': today_appointments_count,
        'confirmed_appointments': confirmed_appointments,
        'pending_appointments': pending_appointments,
        'daily_stats': daily_stats,
    }
    return render(request, 'admin_dashboard.html', context)

    

def book_appointment(request):
    doctors = User.objects.filter(profile__role='doctor')
    branches = Branch.objects.filter(is_active=True)
    selected_branch = request.GET.get('branch', '')

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        branch_id = request.POST.get('branch')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')

        if not doctor_id or not branch_id or not appointment_date or not appointment_time or not reason:
            messages.error(request, "Please fill all fields.")
            return redirect('book_appointment')

        doctor = User.objects.get(id=doctor_id)
        branch = Branch.objects.get(id=branch_id)

        Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            branch=branch,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=reason,
            status='pending'
        )

        messages.success(request, "Appointment booked successfully.")
        return redirect('booking_history')

    return render(request, 'book_appointment.html', {
        'doctors': doctors,
        'branches': branches,
        'selected_branch': selected_branch,
    })

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
def approve_doctor(request, doctor_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('home')

    doctor = get_object_or_404(Profile, id=doctor_id, role='doctor')
    doctor.is_approved = True
    doctor.save()

    messages.success(request, f"{doctor.user.username} approved successfully.")
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
    feedback_list = Feedback.objects.all().order_by('-id')[:6]
    branches = Branch.objects.filter(is_active=True).order_by('city')

    if request.method == 'POST':
        if request.user.is_authenticated:
            name = request.POST.get('name')
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            rating = request.POST.get('rating')
            message = request.POST.get('message')

            Feedback.objects.create(
                name=name,
                email=email,
                subject=subject,
                rating=rating,
                message=message
            )
            return redirect('about')

    return render(request, 'about.html', {
        'feedback_list': feedback_list,
        'branches': branches
    })


@login_required
def feedback_list(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('home')

    feedbacks = Feedback.objects.all().order_by('-created_at')

    stats = feedbacks.aggregate(
        avg_rating=Avg('rating'),
        high_rating_count=Count('id', filter=Q(rating__gte=4))
    )

    context = {
        'feedbacks': feedbacks,
        'avg_rating': round(stats['avg_rating'], 1) if stats['avg_rating'] else 0,
        'high_rating_count': stats['high_rating_count'] or 0,
    }
    return render(request, 'feedback_list.html', context)


def run_reminders(request):
    secret_key = request.GET.get("key")

    if secret_key != "mysecret123":
        return HttpResponse("Unauthorized", status=403)

    now = timezone.localtime()

    appointments = Appointment.objects.filter(
        status='confirmed',
        reminder_sent=False,
        appointment_date__gte=now.date()
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
        print("Appointment time:", appointment_datetime)
        print("Current time:", now)
        print("Minutes left:", minutes_left)
        print("Status:", appointment.status)
        print("Reminder sent:", appointment.reminder_sent)
        print("Patient email:", appointment.patient.email)

        # 24 hours before reminder
        if 1435 <= minutes_left <= 1445:
            found += 1

            ok = send_reminder_email(appointment)

            if ok:
                appointment.reminder_sent = True
                appointment.save()
                sent += 1
                print(f"24-hour reminder sent for appointment #{appointment.id}")
            else:
                print(f"Reminder failed for appointment #{appointment.id}")

    return HttpResponse(f"Matching appointments found: {found}, Reminders sent: {sent}")


def verify_register_otp_view(request):
    email = request.session.get("register_email")

    if not email:
        messages.error(request, "Session expired")
        return redirect("register")

    if request.method == "POST":
        entered_otp = request.POST.get("otp")

        try:
            otp_entry = RegistrationOTP.objects.get(email=email, otp=entered_otp)
        except RegistrationOTP.DoesNotExist:
            messages.error(request, "Invalid OTP")
            return redirect("verify_register_otp")

        user = User.objects.create_user(
            username=otp_entry.username,
            email=otp_entry.email,
            password=otp_entry.password,
            first_name=otp_entry.first_name
        )

        Profile.objects.create(user=user)

        otp_entry.delete()
        request.session.pop("register_email", None)

        messages.success(request, "Registration successful")
        return redirect("login")

    return render(request, "verify_register_otp.html")


@login_required
def reject_doctor(request, doctor_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('home')

    doctor = get_object_or_404(Profile, id=doctor_id, role='doctor')
    username = doctor.user.username
    doctor.user.delete()

    messages.success(request, f"{username} rejected and removed successfully.")
    return redirect('admin_dashboard')