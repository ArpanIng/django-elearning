def cart(request):
    cart = request.cart
    courses = cart.get_courses()
    return {"course_count": len(courses)}