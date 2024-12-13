from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .import views

router = DefaultRouter() 

router.register('list', views.TeacherViewset)
router.register('department_list', views.DepartmentViewset)
router.register('course_list', views.CourseListViewset)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.TeacherRegistrationAPIView.as_view(), name='teacher_register'),
    path('login/', views.TeacherLoginApiView.as_view(), name='teacher_login'),
    path('logout/', views.TeacherLogoutView.as_view(), name='teacher_logout'),
    path('active/<uid64>/<token>/', views.teacher_activate, name = 'teacher_activate'),
    path('course_detail/<int:pk>/', views.CourseDetailAPIView.as_view(), name='course_detail'),
    path('<int:teacher_id>/courses/', views.TeacherCoursesAPIView.as_view(), name='teacher-courses'),
    path('course_update/<int:pk>/', views.CourseUpdateAPIView.as_view(), name='course_update'),
]

