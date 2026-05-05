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
from .utils import generate_otp,send_registration_otp,send_booking_confirmation_email,send_reminder_email
from datetime import datetime
from django.http import HttpResponse
from django.utils import timezone
from .utils import send_reminder_email
from .utils import generate_otp, send_registration_otp
from django.contrib.auth.hashers import make_password
import threading

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
            messages.error(request, "Username already exists")
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

        # ✅ SAFE BACKGROUND EMAIL
        send_in_background(send_registration_otp, email, otp, username)

        messages.success(request, "OTP sent to your email")
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

    send_in_background(send_registration_otp, email, otp, otp_entry.username)

    messages.success(request, "OTP resent")
    return redirect("verify_register_otp")
    
        
def verify_register_otp_view(request):
    email = request.session.get("register_email")

    if not email:
        return redirect("register")

    if request.method == "POST":
        entered_otp = request.POST.get("otp")

        try:
            otp_entry = RegistrationOTP.objects.get(email=email)

            if otp_entry.otp == entered_otp:
                user = User.objects.create_user(
                    username=otp_entry.username,
                    email=otp_entry.email,
                    password=otp_entry.password,
                    first_name=otp_entry.first_name
                )

                Profile.objects.create(user=user)
                otp_entry.delete()

                messages.success(request, "Account created successfully")
                return redirect("login")

            else:
                messages.error(request, "Invalid OTP")

        except RegistrationOTP.DoesNotExist:
            messages.error(request, "OTP expired")

    return render(request, "verify_register_otp.html")

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

    


@login_required
def book_appointment(request):
    doctors = User.objects.filter(profile__role='doctor')
    branches = Branch.objects.filter(is_active=True)

    if request.method == "POST":
        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=User.objects.get(id=request.POST.get("doctor")),
            branch=Branch.objects.get(id=request.POST.get("branch")),
            appointment_date=request.POST.get("appointment_date"),
            appointment_time=request.POST.get("appointment_time"),
            reason=request.POST.get("reason"),
            status='pending'
        )

        messages.success(request, "Appointment booked")
        return redirect("booking_history")

    return render(request, "book_appointment.html", {
        "doctors": doctors,
        "branches": branches
    })


@login_required
def booking_history(request):
    appointments = Appointment.objects.filter(
        patient=request.user
    ).order_by('-appointment_date', '-appointment_time')
    return render(request, 'booking_history.html', {'appointments': appointments})


@login_required
def confirm_booking(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    appointment.status = "confirmed"
    appointment.reminder_sent = False
    appointment.save()

    # ✅ SAFE EMAIL (NO CRASH)
    send_in_background(send_booking_confirmation_email, appointment)

    messages.success(request, "Appointment confirmed")
    return redirect("doctor_dashboard")
    

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
    key = request.GET.get("key")

    if key != "hms_secure_key_123":
        return JsonResponse({"error": "unauthorized"}, status=403)

    now = timezone.localtime()

    appointments = Appointment.objects.filter(
        status='confirmed',
        reminder_sent=False,
        appointment_date=now.date()
    )

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

        if 0 < minutes_left <= 10:
            if send_reminder_email(a):
                a.reminder_sent = True
                a.save()
                sent += 1

    return JsonResponse({"status": "ok", "sent": sent})


def verify_register_otp_view(request):
    email = request.session.get("register_email")

    if not email:
        return redirect("register")

    if request.method == "POST":
        entered_otp = request.POST.get("otp")

        try:
            otp_entry = RegistrationOTP.objects.get(email=email)

            if otp_entry.otp == entered_otp:
                user = User.objects.create_user(
                    username=otp_entry.username,
                    email=otp_entry.email,
                    password=otp_entry.password,
                    first_name=otp_entry.first_name
                )

                Profile.objects.create(user=user)
                otp_entry.delete()

                messages.success(request, "Account created successfully")
                return redirect("login")

            else:
                messages.error(request, "Invalid OTP")

        except RegistrationOTP.DoesNotExist:
            messages.error(request, "OTP expired")

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


def send_in_background(func, *args):
    def wrapper():
        try:
            func(*args)
        except Exception as e:
            print("❌ Background email error:", e)

    threading.Thread(target=wrapper).start()
