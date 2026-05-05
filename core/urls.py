from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('register/verify-otp/', views.verify_register_otp_view, name='verify_register_otp'),
    path('register/resend-otp/', views.resend_register_otp_view, name='resend_register_otp'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('appointments/book/', views.book_appointment, name='book_appointment'),
    path('appointments/history/', views.booking_history, name='booking_history'),
    path('appointments/confirm/<int:appointment_id>/', views.confirm_booking, name='confirm_booking'),
    path('appointments/reject/<int:appointment_id>/', views.reject_booking, name='reject_booking'),

    path('approve-doctor/<int:doctor_id>/', views.approve_doctor, name='approve_doctor'),
    path('reject-doctor/<int:doctor_id>/', views.reject_doctor, name='reject_doctor'),

    path('doctor-list/', views.doctor_list, name='doctor_list'),
    path('chat/start/<int:doctor_id>/', views.start_chat, name='start_chat'),
    path('my-chats/', views.my_chats, name='my_chats'),
    path('chat-room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('get-messages/<int:room_id>/', views.get_messages, name='get_messages'),
    path('send-message/<int:room_id>/', views.send_message, name='send_message'),
    path('chat-notification-count/', views.chat_notification_count, name='chat_notification_count'),

    path('about/', views.about, name='about'),
    path('feedbacks/', views.feedback_list, name='feedback_list'),
    path("doctor/pending-approval/", views.doctor_pending, name="doctor_pending"),
    
    path("run-reminders/", views.run_reminders),
]