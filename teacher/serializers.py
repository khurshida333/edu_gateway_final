from rest_framework import serializers
from . import models
from django.contrib.auth.models import User

class TeacherSerializer(serializers.ModelSerializer):

    user = serializers.StringRelatedField(many=False)
    department = serializers.StringRelatedField(many=False)
    name = serializers.SerializerMethodField()
    bio = serializers.StringRelatedField()
    
    class Meta:
        model = models.Teacher
        fields = ['id', 'user', 'name', 'department', 'bio']

    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"  

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Department
        fields = ['id', 'name']

class CourseListSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField( read_only=True)
    department = serializers.PrimaryKeyRelatedField(source='teacher.department', read_only=True)

    class Meta:
        model = models.Course
        fields = ['id', 'title', 'description', 'duration', 'format', 'key_features', 'teacher', 'department']

class CourseDetailSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField(many=False) 
    teacher = TeacherSerializer(many=False)
    class Meta:
        model = models.Course
        fields = ['id', 'title', 'description', 'duration', 'format', 'key_features', 'department', 'teacher']


class TeacherRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    bio = serializers.CharField(write_only=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=models.Department.objects.all(), many=False
    )

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'password', 'confirm_password', 'bio', 'department'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'password': "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        department = validated_data.pop('department', [])
        bio = validated_data.pop('bio')
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')


        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
        )
        user.set_password(password)
        user.is_active = False  
        user.save()


        teacher = models.Teacher.objects.create(user=user, bio=bio)
        teacher.department.set(department)

        return user

    
class TeacherLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required = True)
    password = serializers.CharField(required = True)