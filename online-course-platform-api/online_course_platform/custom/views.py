from .serializers import RetrieveCourseCategorySerializer, CourseSerializer, RetrieveCourseSerializer, CourseCategorySerializer, UpdateTeacherSerializer, RetrieveTeacherSerializer, UpdateStudentSerializer, RetrieveStudentSerializer, AssignmentSerializer, AssignmentMaterialSerializer, LessonSerializer, TeacherJoinCourseRequestSerializer, RetrieveTeacherJoinCourseRequestSerializer
from django.shortcuts import get_object_or_404
from .models import CourseCategory, Course, Teacher, TeacherJoinCourseRequest, Student, Assignment, AssignmentMaterial, Lesson
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, SAFE_METHODS
from django.db import transaction
from .permissions import IsAdminOrCourseTeacher, IsAdminOrCourseTeacherOrCourseStudent, IsAdminOrTeacher, IsNotAdminUser
from rest_framework.exceptions import ParseError, NotFound, MethodNotAllowed, PermissionDenied

class CourseCategoryViewSet(ModelViewSet):
    queryset = CourseCategory.objects.prefetch_related('courses').all()
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RetrieveCourseCategorySerializer
        return CourseCategorySerializer
        # request.data.course in [course.id for course in teacher.courses]

class TeacherViewSet(
    GenericViewSet,
    RetrieveModelMixin,
    ListModelMixin,
    DestroyModelMixin
):
    queryset = Teacher.objects.select_related('user').prefetch_related('courses').all()
    serializer_class = RetrieveTeacherSerializer

    def get_permissions(self):
        if '/me/' in self.request.path:
            return [IsNotAdminUser()]
        if self.request.method in SAFE_METHODS or self.request.method == 'DELETE':
            return [IsAdminUser()]
        raise MethodNotAllowed('POST, PUT')
    
    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated, IsNotAdminUser])
    def me(self, request):
        teacher = Teacher.objects.filter(user_id=request.user.id).select_related('user').first()
        if not teacher:
            return Response('your account is not a teacher account', status=status.HTTP_400_BAD_REQUEST)
        
        if request.method == 'GET':
            serializer = RetrieveTeacherSerializer(teacher)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = UpdateTeacherSerializer(teacher, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        
class TeacherJoinCourseRequestViewSet(
    ListModelMixin, 
    RetrieveModelMixin, 
    CreateModelMixin, 
    DestroyModelMixin, 
    GenericViewSet):
    def get_queryset(self):
        course_id = self.request.query_params.get('course')
        teacher_id = self.request.query_params.get('teacher')
        queryset = TeacherJoinCourseRequest.objects

        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        return queryset.select_related('teacher', 'course').all()

    def get_permissions(self):
        if self.request.method in SAFE_METHODS or self.request.method == 'DELETE':
            return [IsAuthenticated()]
        elif self.request.method == 'POST':
            return [IsNotAdminUser()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RetrieveTeacherJoinCourseRequestSerializer
        return TeacherJoinCourseRequestSerializer
    
    def destroy(self, request, *args, **kwargs):
        teacher = Teacher.objects.filter(user_id=request.user.id).first()
        instance = self.get_object()

        if not teacher or instance.course.id not in (teacher_course.id for teacher_course in teacher.courses.all()):
            raise PermissionDenied('You are not teacher of the course.')
        
        isAccept = (self.request.query_params.get('accept') == 'accept')
        with transaction.atomic():
            if isAccept:
                course = Course.objects.get(pk=instance.course.id)
                teacherInRequest = Teacher.objects.get(pk=instance.teacher.id)
                teacherInRequest.courses.add(course)
                teacherInRequest.save()
            return super().destroy(request, *args, **kwargs)
    
class StudentViewSet(
    GenericViewSet,
    RetrieveModelMixin,
    ListModelMixin,
    DestroyModelMixin
):
    queryset = Student.objects.select_related('user').prefetch_related('courses').all()
    serializer_class = RetrieveStudentSerializer

    def get_permissions(self):
        if '/me/' in self.request.path:
            return [IsNotAdminUser()]
        if self.request.method in SAFE_METHODS or self.request.method == 'DELETE':
            return [IsAdminUser()]
        raise MethodNotAllowed('POST, PUT')
    
    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated, IsNotAdminUser])
    def me(self, request):
        student = Student.objects.filter(user_id=request.user.id).select_related('user').first()
        if not student:
            return Response('your account is not a student account', status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'GET':
            serializer = RetrieveStudentSerializer(student)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = UpdateStudentSerializer(student, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class CourseViewSet(ModelViewSet):
    def get_queryset(self):
        return Course.objects\
            .select_related('category')\
            .prefetch_related('teachers', 'students', 'teachers__user', 'students__user')\
            .all()

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        elif self.request.method == 'PUT':
            return [IsAuthenticated(), IsAdminOrCourseTeacher()]
        elif self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminOrTeacher()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RetrieveCourseSerializer
        return CourseSerializer
    
    def perform_create(self, serializer):
        teacher = Teacher.objects.filter(user_id=self.request.user.id).first()    

        with transaction.atomic():
            newCourse = serializer.save()
            # if user is teacher, add course to the teacher
            if teacher:
                teacher.courses.add(newCourse)
                teacher.save()

class AssignmentViewSet(ModelViewSet):
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated(), IsAdminOrCourseTeacherOrCourseStudent()]
        if self.request.method in ('PUT', 'POST'):
            return [IsAuthenticated(), IsAdminOrCourseTeacher()]
        return [IsAdminUser()]

    def get_queryset(self):
        return Assignment.objects.filter(
            course_id=self.kwargs['course_pk']
            ).select_related('course', 'teacher', 'teacher__user').all()

    def get_serializer_context(self):
        # by calling super().get_serializer_context(), request will be passed to serializer context
        context = super().get_serializer_context()
        context['course_pk'] = self.kwargs['course_pk']
        return context

    def get_serializer_class(self):
        return AssignmentSerializer
    
class AssignmentMaterialViewSet(ModelViewSet):
    def get_permissions(self):
        # since 3 levels deep nested router won't check if the assignment with that assignment id exists or not in the course with that course id
        # thus need to check here and return 404 if not found
        if not Assignment.objects.filter(id=self.kwargs['assignment_pk'], course_id=self.kwargs['course_pk']).first():
            raise NotFound()
        
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated(), IsAdminOrCourseTeacherOrCourseStudent()]
        elif self.request.method in ('PUT', 'POST'):
            return [IsAuthenticated(), IsAdminOrCourseTeacher()]
        return [IsAdminUser()]

    def get_queryset(self):
        return AssignmentMaterial.objects.filter(assignment_id=self.kwargs['assignment_pk']).all()
    
    def get_serializer_class(self):
        return AssignmentMaterialSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['assignment_pk'] = self.kwargs['assignment_pk']
        return context

class LessonViewSet(ModelViewSet):
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated(), IsAdminOrCourseTeacherOrCourseStudent()]
        if self.request.method in ('PUT', 'POST'):
            return [IsAuthenticated(), IsAdminOrCourseTeacher()]
        return [IsAdminUser()]

    def get_queryset(self):
        return Lesson.objects.filter(
            course_id=self.kwargs['course_pk']
            ).select_related('course').all()

    def get_serializer_class(self):
        return LessonSerializer
    
    def get_serializer_context(self):
        # by calling super().get_serializer_context(), request will be passed to serializer context
        context = super().get_serializer_context()
        context['course_pk'] = self.kwargs['course_pk']
        return context