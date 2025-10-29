from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import ExamCategory, UpcomingExam, Announcement, AdmitCard, Result, Note, UserProfile, UserActivity, Subject, AnswerKey
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, ContactForm

# Add these progress tracking models to your models.py first
try:
    from .models import UserProgress, UserStudySession, ExamTarget
except ImportError:
    # If models don't exist yet, define placeholder classes
    class UserProgress:
        objects = None
    class UserStudySession:
        objects = None  
    class ExamTarget:
        objects = None

def home(request):
    try:
        exam_categories = ExamCategory.objects.all()
        upcoming_exams = UpcomingExam.objects.filter(is_active=True).order_by('exam_date')[:5]
        announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')[:5]
        admit_cards = AdmitCard.objects.filter(is_active=True).order_by('-release_date')[:3]
        results = Result.objects.filter(is_active=True).order_by('-result_date')[:3]
    except Exception as e:
        exam_categories = []
        upcoming_exams = []
        announcements = []
        admit_cards = []
        results = []
    
    context = {
        'exam_categories': exam_categories,
        'upcoming_exams': upcoming_exams,
        'announcements': announcements,
        'admit_cards': admit_cards,
        'results': results,
    }
    return render(request, 'examportal/index.html', context)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                exam_interests=form.cleaned_data['exam_interests']
            )
            
            # Log activity
            UserActivity.objects.create(
                user=user,
                activity_type='registration',
                description='User registered successfully'
            )
            
            # Login user
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to GovtExamPrep.')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'examportal/auth/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Log activity
                UserActivity.objects.create(
                    user=user,
                    activity_type='login',
                    description='User logged in successfully'
                )
                
                messages.success(request, f'Welcome back, {user.username}!')
                
                # Redirect to next page if exists, else home
                next_page = request.GET.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'examportal/auth/login.html', {'form': form})

@login_required
def logout_view(request):
    # Log activity
    UserActivity.objects.create(
        user=request.user,
        activity_type='logout',
        description='User logged out'
    )
    
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def profile_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    
    # Get user activities
    user_activities = UserActivity.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    context = {
        'profile': user_profile,
        'form': form,
        'activities': user_activities,
    }
    return render(request, 'examportal/auth/profile.html', context)

@login_required
def dashboard_view(request):
    # Get or create user profile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Calculate basic stats
    total_logins = UserActivity.objects.filter(user=request.user, activity_type='login').count()
    total_downloads = UserActivity.objects.filter(user=request.user, activity_type='download').count()
    
    # Get recommended exams
    if user_profile.exam_interests != 'multiple':
        recommended_exams = UpcomingExam.objects.filter(
            exam_category__name__icontains=user_profile.get_exam_interests_display().split()[0].lower(),
            is_active=True
        )[:3]
    else:
        recommended_exams = UpcomingExam.objects.filter(is_active=True)[:3]
    
    # Progress Tracking Data (with error handling)
    try:
        user_progress = UserProgress.objects.filter(user=request.user)
        total_subjects = user_progress.count()
        completed_subjects = user_progress.filter(progress_percentage=100).count()
        
        # Study time analytics (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        study_sessions = UserStudySession.objects.filter(
            user=request.user, 
            start_time__gte=week_ago
        )
        total_study_time = sum(session.duration_minutes for session in study_sessions)
        average_daily_study = total_study_time / 7 if study_sessions else 0
        
        # Exam targets
        exam_targets = ExamTarget.objects.filter(user=request.user)
    except:
        # If progress models don't exist yet
        user_progress = []
        total_subjects = 0
        completed_subjects = 0
        total_study_time = 0
        average_daily_study = 0
        study_sessions = []
        exam_targets = []
    
    # Recent activity
    recent_activities = UserActivity.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'user_profile': user_profile,
        'profile': user_profile,
        'total_logins': total_logins,
        'total_downloads': total_downloads,
        'recommended_exams': recommended_exams,
        # Progress tracking data
        'user_progress': user_progress,
        'total_subjects': total_subjects,
        'completed_subjects': completed_subjects,
        'total_study_time': total_study_time,
        'average_daily_study': average_daily_study,
        'recent_activities': recent_activities,
        'exam_targets': exam_targets,
        'study_sessions': study_sessions,
    }
    return render(request, 'examportal/dashboard.html', context)

# Progress Tracking Views
@login_required
def mark_note_completed(request, note_id):
    try:
        if request.method == 'POST':
            note = get_object_or_404(Note, id=note_id)
            user_progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                subject=note.subject
            )
            
            if note not in user_progress.completed_notes.all():
                user_progress.completed_notes.add(note)
                user_progress.update_progress()
                
                # Log activity
                UserActivity.objects.create(
                    user=request.user,
                    activity_type='note_completed',
                    description=f'Completed note: {note.title}'
                )
                
                return JsonResponse({'success': True, 'progress': user_progress.progress_percentage})
        
        return JsonResponse({'success': False})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def start_study_session(request):
    try:
        if request.method == 'POST':
            subject_id = request.POST.get('subject_id')
            subject = get_object_or_404(Subject, id=subject_id)
            
            study_session = UserStudySession.objects.create(
                user=request.user,
                subject=subject,
                start_time=timezone.now()
            )
            
            return JsonResponse({'success': True, 'session_id': study_session.id})
        
        return JsonResponse({'success': False})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def end_study_session(request, session_id):
    try:
        if request.method == 'POST':
            study_session = get_object_or_404(UserStudySession, id=session_id, user=request.user)
            study_session.end_time = timezone.now()
            study_session.save()
            
            # Log activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='study_session',
                description=f'Studied {study_session.subject.name} for {study_session.duration_minutes} minutes'
            )
            
            return JsonResponse({'success': True, 'duration': study_session.duration_minutes})
        
        return JsonResponse({'success': False})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def set_exam_target(request):
    try:
        if request.method == 'POST':
            exam_id = request.POST.get('exam_id')
            target_date = request.POST.get('target_date')
            daily_goal = request.POST.get('daily_goal', 120)
            
            exam = get_object_or_404(UpcomingExam, id=exam_id)
            
            exam_target, created = ExamTarget.objects.get_or_create(
                user=request.user,
                exam=exam,
                defaults={
                    'target_date': target_date,
                    'daily_study_goal': daily_goal
                }
            )
            
            if not created:
                exam_target.target_date = target_date
                exam_target.daily_study_goal = daily_goal
                exam_target.save()
            
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            if request.user.is_authenticated:
                contact.user = request.user
            contact.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
    else:
        if request.user.is_authenticated:
            form = ContactForm(initial={
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email
            })
        else:
            form = ContactForm()
    
    return render(request, 'examportal/contact.html', {'form': form})

# Notes Views
def notes(request):
    exam_categories = ExamCategory.objects.all()
    subjects = Subject.objects.all()
    
    context = {
        'exam_categories': exam_categories,
        'subjects': subjects,
        'selected_category': None,
    }
    return render(request, 'examportal/notes.html', context)

def notes_by_category(request, category_slug):
    exam_categories = ExamCategory.objects.all()
    selected_category = get_object_or_404(ExamCategory, slug=category_slug)
    subjects = Subject.objects.filter(exam_category=selected_category)
    
    context = {
        'exam_categories': exam_categories,
        'selected_category': selected_category,
        'subjects': subjects,
    }
    return render(request, 'examportal/notes.html', context)

def upcoming_exams(request):
    try:
        # Get all active upcoming exams
        upcoming_exams_list = UpcomingExam.objects.filter(is_active=True).order_by('exam_date')
        
        # Get exam categories for filtering
        categories = ExamCategory.objects.all()
        
        context = {
            'upcoming_exams': upcoming_exams_list,
            'categories': categories,
        }
        
        print(f"Rendering template with {upcoming_exams_list.count()} exams")
        return render(request, 'examportal/upcoming_exams.html', context)
        
    except Exception as e:
        print(f"Error in upcoming_exams: {e}")
        from django.http import HttpResponse
        return HttpResponse(f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 50px; text-align: center;">
                <h1 style="color: #e74c3c;">Error Loading Page</h1>
                <p>{str(e)}</p>
                <a href="/" style="color: #3498db;">Return to Home</a>
            </body>
        </html>
        """)

def announcements(request):
    try:
        # Get all active announcements, ordered by newest first
        announcements_list = Announcement.objects.filter(is_active=True).order_by('-created_at')
        
        print(f"DEBUG: Found {announcements_list.count()} announcements")
        for ann in announcements_list:
            print(f"DEBUG: - {ann.title} (Type: {ann.announcement_type})")
        
        context = {
            'announcements': announcements_list,
        }
        return render(request, 'examportal/announcements.html', context)
        
    except Exception as e:
        print(f"ERROR in announcements view: {e}")
        from django.http import HttpResponse
        return HttpResponse(f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 50px; text-align: center;">
                <h1 style="color: #e74c3c;">Error Loading Announcements</h1>
                <p>Error: {str(e)}</p>
                <a href="/" style="color: #3498db;">Return to Home</a>
            </body>
        </html>
        """)

def admit_cards(request):
    try:
        # Get all active admit cards, ordered by release date
        admit_cards_list = AdmitCard.objects.filter(is_active=True).order_by('-release_date')
        
        print(f"DEBUG: Found {admit_cards_list.count()} admit cards")
        for card in admit_cards_list:
            print(f"DEBUG: - {card.title} (Exam: {card.exam.title})")
        
        context = {
            'admit_cards': admit_cards_list,
        }
        return render(request, 'examportal/admit_cards.html', context)
        
    except Exception as e:
        print(f"ERROR in admit_cards view: {e}")
        from django.http import HttpResponse
        return HttpResponse(f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 50px; text-align: center;">
                <h1 style="color: #e74c3c;">Error Loading Admit Cards</h1>
                <p>Error: {str(e)}</p>
                <a href="/" style="color: #3498db;">Return to Home</a>
            </body>
        </html>
        """)

def results(request):
    try:
        # Get all active results, ordered by result date
        results_list = Result.objects.filter(is_active=True).order_by('-result_date')
        
        print(f"Found {results_list.count()} active results")
        
        context = {
            'results': results_list,
        }
        return render(request, 'examportal/results.html', context)
        
    except Exception as e:
        print(f"Error in results view: {e}")
        from django.http import HttpResponse
        return HttpResponse(f"Error in results view: {str(e)}")

def answer_keys(request):
    try:
        # Get all active answer keys, ordered by release date
        answer_keys_list = AnswerKey.objects.filter(is_active=True).order_by('-release_date')
        
        # Get exam categories for filtering
        categories = ExamCategory.objects.all()
        
        # Get category filter from request
        category_filter = request.GET.get('category')
        if category_filter:
            answer_keys_list = answer_keys_list.filter(exam__exam_category__slug=category_filter)
        
        context = {
            'answer_keys': answer_keys_list,
            'categories': categories,
            'selected_category': category_filter,
        }
        return render(request, 'examportal/answer_keys.html', context)
        
    except Exception as e:
        print(f"Error in answer_keys view: {e}")
        from django.http import HttpResponse
        return HttpResponse(f"Error loading answer keys: {str(e)}")

def search(request):
    query = request.GET.get('q', '').strip()
    results = {
        'notes': [],
        'exams': [],
        'announcements': [],
        'answer_keys': [],
        'admit_cards': [],
        'results': [],
    }
    
    if query:
        # Search in Notes
        results['notes'] = Note.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(subject__name__icontains=query) |
            Q(subject__exam_category__name__icontains=query),
            is_active=True
        ).distinct()[:10]
        
        # Search in Upcoming Exams
        results['exams'] = UpcomingExam.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(exam_category__name__icontains=query),
            is_active=True
        ).distinct()[:10]
        
        # Search in Announcements
        results['announcements'] = Announcement.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query),
            is_active=True
        ).distinct()[:10]
        
        # Search in Answer Keys
        results['answer_keys'] = AnswerKey.objects.filter(
            Q(title__icontains=query) |
            Q(exam__title__icontains=query) |
            Q(exam__exam_category__name__icontains=query),
            is_active=True
        ).distinct()[:10]
        
        # Search in Admit Cards
        results['admit_cards'] = AdmitCard.objects.filter(
            Q(title__icontains=query) |
            Q(exam__title__icontains=query) |
            Q(exam__exam_category__name__icontains=query),
            is_active=True
        ).distinct()[:10]
        
        # Search in Results
        results['results'] = Result.objects.filter(
            Q(title__icontains=query) |
            Q(exam__title__icontains=query) |
            Q(exam__exam_category__name__icontains=query),
            is_active=True
        ).distinct()[:10]
    
    context = {
        'query': query,
        'results': results,
        'total_results': sum(len(items) for items in results.values()),
        'has_results': any(len(items) > 0 for items in results.values())
    }
    
    return render(request, 'examportal/search.html', context)

# Debug views
def debug_upcoming_exams(request):
    exams = UpcomingExam.objects.all()
    print(f"Total exams in database: {exams.count()}")
    for exam in exams:
        print(f"Exam: {exam.title}, Active: {exam.is_active}")
    from django.http import HttpResponse
    return HttpResponse(f"Total exams: {exams.count()}. Check console for details.")

def debug_announcements(request):
    announcements = Announcement.objects.all()
    print(f"Total announcements in database: {announcements.count()}")
    for announcement in announcements:
        print(f"Announcement: {announcement.title}, Active: {announcement.is_active}")
    from django.http import HttpResponse
    return HttpResponse(f"Total announcements: {announcements.count()}. Check console for details.")

def debug_admit_cards(request):
    admit_cards = AdmitCard.objects.all()
    print(f"Total admit cards in database: {admit_cards.count()}")
    for card in admit_cards:
        print(f"Admit Card: {card.title}, Active: {card.is_active}")
    from django.http import HttpResponse
    return HttpResponse(f"Total admit cards: {admit_cards.count()}. Check console for details.")

def debug_results(request):
    results = Result.objects.all()
    print(f"Total results in database: {results.count()}")
    for result in results:
        print(f"Result: {result.title}, Active: {result.is_active}")
    from django.http import HttpResponse
    return HttpResponse(f"Total results: {results.count()}. Check console for details.")

def privacy_policy(request):
    return render(request, 'examportal/privacy_policy.html')

def terms_conditions(request):
    return render(request, 'examportal/terms_conditions.html')

def about_us(request):
    return render(request, 'examportal/about.html')

def refund_policy(request):
    return render(request, 'examportal/refund_policy.html')

def disclaimer(request):
    return render(request, 'examportal/disclaimer.html')

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            if request.user.is_authenticated:
                contact.user = request.user
            contact.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
    else:
        if request.user.is_authenticated:
            form = ContactForm(initial={
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email
            })
        else:
            form = ContactForm()
    
    return render(request, 'examportal/contact.html', {'form': form})