def user_roles(request):
    return {
        'is_admin': request.session.get('is_admin', False),
        'is_banker': request.session.get('is_banker', False),
    }