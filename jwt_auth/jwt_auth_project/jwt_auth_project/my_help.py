from django.http import JsonResponse

def JsonResponseUnauthorized(code: str, message: str | None = None):
    """
    إرجاع استجابة JSON بحالة 401 Unauthorized.
    - code: كود خطأ داخلي (سلسلة) لتسهيل التعرف على السبب في الواجهة الأمامية.
    - message: رسالة اختيارية توضيحية.
    """
    body = {
        "detail": message or "Unauthorized",
        "code": code
    }
    return JsonResponse(body, status=401)
