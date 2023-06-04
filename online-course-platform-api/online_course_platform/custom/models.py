from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from .validators import FileSizeValidator

class CourseCategory(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.title

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # TODO: allow category to be null
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='courses')

    def __str__(self) -> str:
        return self.title
    
class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course, blank=True, related_name='teachers')
    profile_picture = models.ImageField(null=True, default=None, upload_to='teacher/images', validators=[
        FileSizeValidator(max_mb=1),
        FileExtensionValidator(allowed_extensions=['jpg', 'png', 'webp'])
        ])

    def __str__(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'
    
class TeacherJoinCourseRequest(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_join_course_requests')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='teacher_join_course_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    
class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course, blank=True, related_name='students')
    profile_picture = models.ImageField(null=True, default=None, upload_to='student/images', validators=[
        FileSizeValidator(max_mb=1),
        FileExtensionValidator(allowed_extensions=['jpg', 'png', 'webp'])
        ])

    def __str__(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'

class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    allow_submit = models.BooleanField(default=True)
    teacher = models.ForeignKey(Teacher, null=True, blank=True, on_delete=models.SET_NULL, related_name='assignments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')

    def __str__(self) -> str:
        return self.title

class AssignmentMaterial(models.Model):
    name = models.CharField(max_length=255) # non unique name
    file = models.FileField(upload_to='assignment', validators=[
        FileSizeValidator(max_mb=5),
        FileExtensionValidator(allowed_extensions=['jpg', 'png', 'webp', 'zip', 'pdf', 'txt', 'docx', 'xlsx', 'pptx'])
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='materials')

class Lesson(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    teacher = models.ForeignKey(Teacher, null=True, blank=True, on_delete=models.SET_NULL, related_name='lessons')
    video = models.FileField(
        upload_to='course/videos', 
        validators=[FileSizeValidator(max_mb=10), FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'ogg'])],
        null=True, 
        blank=True
    )