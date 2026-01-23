
from .models import Job

def categories_processor(request):
    # Lấy danh sách ngành nghề duy nhất từ Database
    categories = Job.objects.exclude(category__isnull=True).exclude(category="").values_list('category', flat=True).distinct()
    return {
        'all_categories': categories  # Biến này sẽ dùng được ở TẤT CẢ các file HTML
    }