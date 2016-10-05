from django.conf import settings

def api_host(request):
    return {"API_HOST": settings.API_HOST, "API_KEY": settings.API_KEY}
    #return {"API_HOST": "", "API_KEY": ""}
