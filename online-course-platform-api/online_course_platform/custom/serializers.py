from rest_framework import serializers
from rest_framework import status
from .models import Course, CourseCategory, Teacher, TeacherJoinCourseRequest, Student, Assignment, AssignmentMaterial, Lesson
# FIXME: decouple
from core.models import User
from django.conf import settings
from rest_framework.exceptions import ParseError, NotFound, PermissionDenied

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class SimpleCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title']

class RetrieveCourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = ['id', 'title', 'courses']
    
    courses = SimpleCourseSerializer(many=True, read_only=True)
    
class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = ['title', 'courses']
    
class SimpleCourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = ['id', 'title']

class SimpleTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'user', 'profile_picture']

    user = SimpleUserSerializer(read_only=True)
    
class SimpleStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'user', 'profile_picture']
    
    user = SimpleUserSerializer(read_only=True)

class RetrieveCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'created_at', 'category', 'teachers', 'students']

    category = SimpleCourseCategorySerializer(read_only=True)
    teachers = SimpleTeacherSerializer(many=True, read_only=True)
    students = SimpleStudentSerializer(many=True, read_only=True)

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['title', 'category']
        # TODO: allow category to be null  

    def validate(self, attrs):
        if len(attrs['title']) < 3:
            raise serializers.ValidationError('Course title must not be at least 3 letters long')
        return super().validate(attrs)
    
class UpdateTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['profile_picture']

class RetrieveTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'user', 'courses', 'profile_picture']

    user = SimpleUserSerializer(read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)

class UpdateStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['profile_picture']

class RetrieveStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'user', 'courses', 'profile_picture']
    
    user = SimpleUserSerializer(read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)

class TeacherJoinCourseRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherJoinCourseRequest
        fields = ['course']

    def create(self, validated_data):
        request = self.context['request']

        teacher = Teacher.objects.filter(user_id=request.user.id).first()
        if not teacher:
            raise PermissionDenied("This method is only allowed to teachers")

        course_pk = validated_data['course'].id
        course = Course.objects.filter(pk=course_pk).first()
        if not course:
            raise NotFound(f"Course with id = {course_pk} not found.")
        
        if course.id in (teacher_course.id for teacher_course in teacher.courses.all()):
            raise PermissionDenied("You are already in this course.")

        validated_data['teacher_id'] = teacher.id
        return super().create(validated_data)

class RetrieveTeacherJoinCourseRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherJoinCourseRequest
        fields = ['id', 'teacher', 'course', 'created_at']

    teacher = SimpleTeacherSerializer()
    course = SimpleCourseSerializer()

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'allow_submit', 'teacher']

    id = serializers.IntegerField(read_only=True)
    teacher = SimpleTeacherSerializer(read_only=True)
    
    def create(self, validated_data):
        validated_data['course_id'] = self.context['course_pk']

        request = self.context['request']
        teacher = Teacher.objects.filter(user_id=request.user.id).first()
        if teacher:
            validated_data['teacher_id'] = teacher.id
            
        return super().create(validated_data)

class AssignmentMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentMaterial
        fields = ['id', 'name', 'file', 'created_at']

    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    def create(self, validated_data):
        validated_data['assignment_id'] = self.context['assignment_pk']
        return super().create(validated_data)

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'course', 'video', 'created_at', 'updated_at', 'teacher', 'description']

    id = serializers.IntegerField(read_only=True)
    course = SimpleCourseSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    teacher = SimpleTeacherSerializer(read_only=True)
    
    def create(self, validated_data):
        validated_data['course_id'] = self.context['course_pk']

        request = self.context['request']
        teacher = Teacher.objects.filter(user_id=request.user.id).first()
        if teacher:
            validated_data['teacher_id'] = teacher.id
            
        return super().create(validated_data)