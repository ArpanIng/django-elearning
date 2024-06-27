from django.db.models import Count, Q
from .models import Course

difficulty_levels = Course.DifficultyLevel
price_status = Course.PriceStatus


def filter_courses(request, kwargs, queryset):
    query = request.GET.get("q")
    category = kwargs.get("category_slug")
    subcategory = kwargs.get("subcategory_slug")

    # filter course based on search params
    if query:
        lookups = Q(title__icontains=query) | Q(description__icontains=query)
        queryset = queryset.filter(lookups)

    # filter course based on category or subcategory
    if category:
        queryset = queryset.filter(category__slug=category)

    if subcategory:
        queryset = queryset.filter(subcategory__slug=subcategory)

    return queryset

def get_course_counts_by_difficulty_level(queryset):
    """
    Return a list of tuples containing the difficulty level (value), its label, and the count of courses at that level.

    Args:
        queryset: A QuerySet of courses.
    """

    course_counts = queryset.values("level").annotate(count=Count("level"))
    course_count_dict = {item["level"]: item["count"] for item in course_counts}
    # appending the course count
    levels = [
        (level.value, level.label, course_count_dict.get(level.value, 0))
        for level in difficulty_levels
    ]
    return levels


def get_course_counts_by_price_status(queryset):
    """
    Return a list of tuples containing price status, its label, and the count of courses with at that status.

    Args:
        queryset: A QuerySet of courses.
    """

    course_counts = queryset.values("price_status").annotate(count=Count("price_status"))
    course_count_dict = {item["price_status"]: item["count"] for item in course_counts}
    statuses = [
        (status.value, status.label, course_count_dict.get(status.value, 0))
        for status in price_status
    ]
    return statuses
