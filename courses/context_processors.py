from .models import Category

def menu_links(request):
    return {
        "categories": Category.get_categories().order_by("id")
    }