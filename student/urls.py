from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .import views

router = DefaultRouter()
router.register('list', views.StudentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.StudentRegistrationAPIView.as_view(), name='student_register'),
    path('login/', views.StudentLoginApiView.as_view(), name='student_login'),
    path('logout/', views.StudentLogoutView.as_view(), name='student_logout'),
    path('active/<uid64>/<token>/', views.student_activate, name = 'student_activate'),
]