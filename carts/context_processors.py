def cart(request):
    cart = request.cart
    courses = cart.get_courses()
    return {"courses": courses, "course_count": len(courses)}