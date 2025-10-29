from django.db import models
from ckeditor.fields import RichTextField
from django.utils import timezone
from django.utils.text import slugify

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

# class ExamCategory(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     icon = models.CharField(max_length=50, default='fas fa-book')
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return self.name
    
#     class Meta:
#         verbose_name_plural = "Exam Categories"
from django.contrib.auth.models import User
from django.db import models

# Add these models at the end of your existing models

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
    activity_type = models.CharField(max_length=50)  # login, download, view_notes, etc.
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
    title = models.CharField(max_length=200)
    exam_category = models.ForeignKey(ExamCategory, on_delete=models.CASCADE)
    description = models.TextField()
    application_start = models.DateField()
    application_end = models.DateField()
    # exam_date = models.DateField()
    exam_date = models.DateField(null=True, blank=True)
    
    apply_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def get_exam_date_display(self):
        """Smart display for exam date"""
        if self.exam_date:
            return self.exam_date.strftime("%d %b %Y")
        return "Coming Soon"
    
    
    def __str__(self):
        return self.title
    
    def is_open_for_application(self):
        today = timezone.now().date()
        return self.application_start <= today <= self.application_end

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
    
# Add these progress tracking models to your existing models.py

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
    # created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.CharField(max_length=200)
    
    def __str__(self):
        return f"{self.user.username} - {self.exam.title}"