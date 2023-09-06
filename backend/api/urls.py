from django.urls import include, path
from rest_framework.routers import DefaultRouter


# from api.views import 

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]