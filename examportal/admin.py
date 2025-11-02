from django.contrib import admin
from .models import *

@admin.register(ExamCategory)
class ExamCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_category', 'order']
    list_filter = ['exam_category']
    search_fields = ['name']
    ordering = ['exam_category', 'order']

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'created_at', 'is_active']
    list_filter = ['subject', 'is_active', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('subject', 'title', 'content', 'file', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(UpcomingExam)
class UpcomingExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'exam_category', 'application_start', 'application_end', 'total_vacancies', 'is_active']
    list_filter = ['exam_category', 'is_active']
    search_fields = ['title', 'description']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'exam_category', 'description', 'is_active')
        }),
        ('Important Dates', {
            'fields': ('application_start', 'application_end', 'exam_date', 'fee_payment_last_date', 'correction_dates')
        }),
        ('Vacancy & Age Details', {
            'fields': ('total_vacancies', 'vacancy_breakdown', 'age_min', 'age_max', 'age_relaxation_details')
        }),
        ('Educational Qualifications', {
            'fields': ('educational_qualification', 'percentage_required', 'eligibility_criteria')
        }),
        ('Application Fee Details', {
            'fields': ('fee_general', 'fee_obc', 'fee_sc_st', 'fee_female', 'fee_refund_policy', 'payment_modes')
        }),
        ('Exam Content', {
            'fields': ('exam_pattern', 'syllabus', 'how_to_apply'),
            'classes': ('collapse',)
        }),
        ('Important Links', {
            'fields': ('apply_link', 'date_extend_notice', 'information_bulletin', 'official_notification', 'official_website'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'announcement_type', 'created_at', 'is_active']
    list_filter = ['announcement_type', 'is_active', 'created_at']
    search_fields = ['title', 'content']

@admin.register(AdmitCard)
class AdmitCardAdmin(admin.ModelAdmin):
    list_display = ['title', 'exam', 'release_date', 'is_active']
    list_filter = ['exam', 'is_active', 'release_date']
    search_fields = ['title', 'exam__title']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['title', 'exam', 'result_date', 'is_active']
    list_filter = ['exam', 'is_active', 'result_date']
    search_fields = ['title', 'exam__title']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'exam_interests', 'created_at']
    list_filter = ['exam_interests', 'created_at']
    search_fields = ['user__username', 'phone']

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__username', 'activity_type']
    readonly_fields = ['created_at']

@admin.register(AnswerKey)
class AnswerKeyAdmin(admin.ModelAdmin):
    list_display = ['title', 'exam', 'exam_type', 'release_date', 'is_active']
    list_filter = ['exam', 'exam_type', 'is_active', 'release_date']
    search_fields = ['title', 'exam__title']
    date_hierarchy = 'release_date'

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'progress_percentage', 'last_updated']
    list_filter = ['user', 'subject__exam_category']
    search_fields = ['user__username', 'subject__name']

@admin.register(UserStudySession)
class UserStudySessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'start_time', 'duration_minutes']
    list_filter = ['user', 'subject', 'start_time']
    search_fields = ['user__username', 'subject__name']

@admin.register(ExamTarget)
class ExamTargetAdmin(admin.ModelAdmin):
    list_display = ['user', 'exam', 'target_date', 'daily_study_goal', 'created_at']
    list_filter = ['user', 'exam']
    search_fields = ['user__username', 'exam__title']