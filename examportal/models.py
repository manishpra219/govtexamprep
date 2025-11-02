from django.db import models
from ckeditor.fields import RichTextField
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User  # Move this import to the top

class ExamCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-book')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Exam Categories"

class UserProfile(models.Model):
    EXAM_CHOICES = [
        ('ssc', 'SSC Exams'),
        ('banking', 'Banking Exams'),
        ('teaching', 'Teaching Exams'),
        ('upsc', 'UPSC Exams'),
        ('railway', 'Railway Exams'),
        ('defense', 'Defense Exams'),
        ('multiple', 'Multiple Exams'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    exam_interests = models.CharField(max_length=20, choices=EXAM_CHOICES, default='multiple')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} Profile"

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"

class Subject(models.Model):
    exam_category = models.ForeignKey(ExamCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.exam_category.name} - {self.name}"

class Note(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = RichTextField()
    file = models.FileField(upload_to='notes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title

class UpcomingExam(models.Model):
    # Basic Information (Required)
    title = models.CharField(max_length=200)
    exam_category = models.ForeignKey(ExamCategory, on_delete=models.CASCADE)
    description = models.TextField()
    
    # Dates (Required)
    application_start = models.DateField()
    application_end = models.DateField()
    exam_date = models.DateField(null=True, blank=True)
    
    # Important Links (Optional)
    apply_link = models.URLField(blank=True, help_text="Apply Online Link")
    date_extend_notice = models.URLField(blank=True, help_text="Date Extend Notice Link")
    information_bulletin = models.URLField(blank=True, help_text="Download Information Bulletin")
    official_notification = models.URLField(blank=True, help_text="Official Notification PDF")
    official_website = models.URLField(blank=True, help_text="Official Website Link")
    
    # Exam Details (Optional)
    eligibility_criteria = models.TextField(blank=True, help_text="Educational qualification, age limit, etc.")
    exam_pattern = models.TextField(blank=True, help_text="Exam stages, marks distribution, etc.")
    syllabus = models.TextField(blank=True, help_text="Topics and subjects covered")
    vacancy_details = models.TextField(blank=True, help_text="Number of posts, categories, etc.")
    application_fee = models.CharField(max_length=200, blank=True, help_text="General/OBC/SC/ST fees")
    
    # New Detailed Fields
    total_vacancies = models.IntegerField(default=0, help_text="Total number of vacancies")
    age_min = models.IntegerField(null=True, blank=True, help_text="Minimum age requirement")
    age_max = models.IntegerField(null=True, blank=True, help_text="Maximum age requirement")
    age_relaxation_details = models.TextField(blank=True, help_text="Age relaxation rules")
    
    # Application fee details
    fee_general = models.CharField(max_length=200, blank=True, help_text="Fee for General category")
    fee_obc = models.CharField(max_length=200, blank=True, help_text="Fee for OBC category")
    fee_sc_st = models.CharField(max_length=200, blank=True, help_text="Fee for SC/ST category")
    fee_female = models.CharField(max_length=200, blank=True, help_text="Fee for Female candidates")
    fee_refund_policy = models.TextField(blank=True, help_text="Fee refund policy details")
    payment_modes = models.TextField(blank=True, help_text="Accepted payment modes")
    
    # Important dates
    fee_payment_last_date = models.DateField(null=True, blank=True, help_text="Last date for fee payment")
    correction_dates = models.CharField(max_length=200, blank=True, help_text="Correction window dates")
    
    # Vacancy breakdown
    vacancy_breakdown = models.TextField(blank=True, help_text="JSON or formatted text for category-wise vacancies")
    
    # Educational qualifications
    educational_qualification = models.TextField(blank=True, help_text="Required educational qualifications")
    percentage_required = models.TextField(blank=True, help_text="Percentage requirements for different categories")
    
    # How to apply
    how_to_apply = models.TextField(blank=True, help_text="Step-by-step application process")
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_exam_date_display(self):
        if self.exam_date:
            return self.exam_date.strftime("%d %b %Y")
        return "Coming Soon"
    
    def is_open_for_application(self):
        today = timezone.now().date()
        return self.application_start <= today <= self.application_end
    
    def __str__(self):
        return self.title

class Announcement(models.Model):
    ANNOUNCEMENT_TYPES = [
        ('new', 'New'),
        ('update', 'Update'),
        ('important', 'Important'),
        ('general', 'General'),
    ]
    
    title = models.CharField(max_length=200)
    content = RichTextField()
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPES, default='general')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class AdmitCard(models.Model):
    exam = models.ForeignKey(UpcomingExam, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    download_link = models.URLField(blank=True)
    release_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.exam.title} - {self.title}"

class Result(models.Model):
    exam = models.ForeignKey(UpcomingExam, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    result_link = models.URLField(blank=True)
    result_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.exam.title} - {self.title}"
    
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
    
class AnswerKey(models.Model):
    EXAM_TYPE_CHOICES = [
        ('prelims', 'Preliminary Exam'),
        ('mains', 'Mains Exam'),
        ('both', 'Both Prelims & Mains'),
    ]
    
    exam = models.ForeignKey(UpcomingExam, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES, default='prelims')
    answer_key_file = models.FileField(upload_to='answer_keys/', blank=True, null=True)
    answer_key_link = models.URLField(blank=True)
    release_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.exam.title} - {self.title}"
    
    def get_download_url(self):
        if self.answer_key_file:
            return self.answer_key_file.url
        return self.answer_key_link

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    completed_notes = models.ManyToManyField('Note', blank=True)
    total_notes = models.IntegerField(default=0)
    progress_percentage = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    def update_progress(self):
        self.total_notes = self.subject.note_set.filter(is_active=True).count()
        completed_count = self.completed_notes.count()
        if self.total_notes > 0:
            self.progress_percentage = int((completed_count / self.total_notes) * 100)
        else:
            self.progress_percentage = 0
        self.save()
    
    def __str__(self):
        return f"{self.user.username} - {self.subject.name}"

class UserStudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)
    notes_covered = models.ManyToManyField('Note', blank=True)
    
    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            duration = self.end_time - self.start_time
            self.duration_minutes = int(duration.total_seconds() / 60)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.subject.name} - {self.start_time.date()}"

class ExamTarget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(UpcomingExam, on_delete=models.CASCADE)
    target_date = models.DateField()
    daily_study_goal = models.IntegerField(default=120)  # minutes
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.exam.title}"