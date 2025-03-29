from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tracker import views

router = DefaultRouter()
router.register(r'students', views.StudentViewSet)
router.register(r'attendance', views.AttendanceViewSet)
router.register(r'performance', views.PerformanceViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]







'''from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tracker import views

router = DefaultRouter()
router.register(r'students', views.StudentViewSet)
router.register(r'attendance', views.AttendanceViewSet)
router.register(r'performance', views.PerformanceViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Add this line
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]'''