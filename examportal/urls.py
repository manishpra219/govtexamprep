from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('contact/', views.contact_view, name='contact'),
    
    # Content URLs
    path('notes/', views.notes, name='notes'),
    path('notes/<slug:category_slug>/', views.notes_by_category, name='notes_by_category'),
    path('upcoming-exams/', views.upcoming_exams, name='upcoming_exams'),
    path('announcements/', views.announcements, name='announcements'),
    path('admit-cards/', views.admit_cards, name='admit_cards'),
    path('results/', views.results, name='results'),
    path('answer-keys/', views.answer_keys, name='answer_keys'),
    path('search/', views.search, name='search'),
    
    # Progress Tracking URLs
    path('progress/mark-completed/<int:note_id>/', views.mark_note_completed, name='mark_note_completed'),
    path('progress/start-session/', views.start_study_session, name='start_study_session'),
    path('progress/end-session/<int:session_id>/', views.end_study_session, name='end_study_session'),
    path('progress/set-exam-target/', views.set_exam_target, name='set_exam_target'),
    
    # Debug URLs
    path('debug-upcoming/', views.debug_upcoming_exams, name='debug_upcoming'),
    path('debug-announcements/', views.debug_announcements, name='debug_announcements'),
    path('debug-admit-cards/', views.debug_admit_cards, name='debug_admit_cards'),
    path('debug-results/', views.debug_results, name='debug_results'),

    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('about-us/', views.about_us, name='about_us'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
]