from functools import wraps
from django.http import JsonResponse
from users.models import Role_Group

def permit_if_role_in(allowed_roles):
    """
    Decorator to check if the logged-in user has one of the allowed roles.
    """
    def view_wrapper_function(decorated_view_function):

        @wraps(decorated_view_function)
        def enforce_user_permissions(request, *args, **kwargs):
            print(allowed_roles)
            # تحقق من صلاحية المستخدم
            if not Role_Group.objects.filter(
                group__user=request.user_id,  # استخدم request.user وليس request.user_id
                permission__Per_name=allowed_roles
            ).exists():
                return JsonResponse(
                    {"message": "Permission denied "},
                    status=403
                )
            
            # إذا كان لديه الصلاحية، استدعي الـ view الأصلي
            response = decorated_view_function(request, *args, **kwargs)
            return response

        return enforce_user_permissions
    return view_wrapper_function
