from .models import ExamCategory

def exam_categories(request):
    categories = ExamCategory.objects.all()
    return {
        'exam_categories': categories
    }