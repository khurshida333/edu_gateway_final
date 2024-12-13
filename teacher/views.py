from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import generics
from . import models
from . import serializers
from rest_framework import filters, pagination
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
# for sending email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import redirect
from rest_framework.filters import SearchFilter
from django.http import JsonResponse
from rest_framework import status


class DepartmentViewset(viewsets.ModelViewSet):
    queryset = models.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer
    
class TeacherPagination(pagination.PageNumberPagination):
    page_size = 1 
    page_size_query_param = 'page_size'
    max_page_size = 100

class TeacherViewset(viewsets.ModelViewSet):
    queryset = models.Teacher .objects.all()
    serializer_class = serializers.TeacherSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = TeacherPagination
    search_fields = ['user__first_name', 'user__email', 'department__name']

class TeacherCoursesAPIView(APIView):
    def get(self, request, teacher_id):
        try:

            teacher = models.Teacher.objects.get(id=teacher_id)

            courses = models.Course.objects.filter(teacher=teacher)

            serializer = serializers.CourseListSerializer(courses, many=True) 

            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.Teacher.DoesNotExist:
            return Response({"error": "Teacher not found"}, status=status.HTTP_404_NOT_FOUND)

       
class CourseListViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseListSerializer
    filter_backends = [SearchFilter]  
    filterset_fields = ['teacher',]
    search_fields = ['id', 'title', 'department__name']  
    def perform_create(self, serializer):
        user = self.request.user
        try:
            teacher = models.Teacher.objects.get(user=user) 
            serializer.save(teacher=teacher) 
        except models.Teacher.DoesNotExist:
            raise serializers.ValidationError("User is not associated with a teacher.")
    def destroy(self, request, pk=None):
        try:
            course = self.get_object()

            if course.teacher.user != request.user:
                return Response({"error": "You do not have permission to delete this course."}, status=status.HTTP_403_FORBIDDEN)
            course.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except models.Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

class CourseDetailAPIView(generics.RetrieveAPIView):
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseDetailSerializer
    permission_classes = [IsAuthenticated] 

class CourseUpdateAPIView(generics.UpdateAPIView):
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseDetailSerializer
    permission_classes = [IsAuthenticated]

class TeacherRegistrationAPIView(APIView):
    serializer_class = serializers.TeacherRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            print(user)
            token = default_token_generator.make_token(user)
            print("token", token)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            print("uid", uid)
            print(user.email)
            confirm_link = f"http://127.0.0.1:8000/teacher/active/{uid}/{token}"
            email_subject = "Confirm Your Email"
            email_body = render_to_string('confirm_teacher_email.html', {'confirm_link' : confirm_link})
            email = EmailMultiAlternatives(email_subject,'',to=[user.email])
            email.attach_alternative(email_body, "text/html")
            email.send()
            return JsonResponse({'message': 'Registration successful! Check your mail for confirmation !'})
        return JsonResponse({"errors": serializer.errors}, status=400)
    


def teacher_activate(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = User._default_manager.get(pk=uid)
    except(User.DoesNotExist):
        user = None 
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
      
        return redirect('http://127.0.0.1:5500/teacher_login.html')
    else:
       
        return redirect('http://127.0.0.1:5500/teacher_reg.html')

    

class TeacherLoginApiView(APIView):
    def post(self, request):
        serializer = serializers.TeacherLoginSerializer(data=self.request.data)
        
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)
            
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                login(request, user)

                
                try:
                    teacher = models.Teacher.objects.get(user=user)  
                    teacher_id = teacher.id 
                except models.Teacher.DoesNotExist:
                    return Response({'error': 'Teacher not found.'}, status=status.HTTP_404_NOT_FOUND)

                return Response({
                    'teacher_token': token.key,
                    'teacher_id': teacher_id,
                    'user_id': user.id  
                })
            else:
                return Response({'error': "Invalid Credential"}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeacherLogoutView(APIView):
    def get(self, request):
        try:
            
            if hasattr(request.user, 'auth_token'):
                request.user.auth_token.delete()  

            
            logout(request)

            
            return Response({"message": "Logout teacher successful"}, status=status.HTTP_200_OK)

        except Exception as e:
           
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

