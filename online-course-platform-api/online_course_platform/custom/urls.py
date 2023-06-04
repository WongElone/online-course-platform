from django.urls import path, include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register(r'course_categories', views.CourseCategoryViewSet)
router.register(r'courses', views.CourseViewSet, basename='courses')
router.register(r'teacher_join_course_requests', views.TeacherJoinCourseRequestViewSet, basename='teacher_join_course_requests')
router.register(r'teachers', views.TeacherViewSet)
router.register(r'students', views.StudentViewSet)

courses_router = routers.NestedDefaultRouter(router, r'courses', lookup='course')
courses_router.register(r'assignments', views.AssignmentViewSet, basename='course-assignments')
courses_router.register(r'lessons', views.LessonViewSet, basename='course-lessons')

assignments_router = routers.NestedDefaultRouter(courses_router, r'assignments', lookup='assignment')
assignments_router.register(r'materials', views.AssignmentMaterialViewSet, basename='course-assignment-materials')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(courses_router.urls)),
    path('', include(assignments_router.urls)),
]