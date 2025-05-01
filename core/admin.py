from django.contrib import admin

from .models import Comment, Course, Follow, Like, Post, Student, Teacher


# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["uuid", "user", "title", "content"]


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ["uuid", "user", "post"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["uuid", "post", "content"]


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ["uuid", "user", "user_following"]


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["name", "teacher"]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["name", "roll", "email", "display_courses", "address"]

    def display_courses(self, obj):
        return ", ".join(course.name for course in obj.courses.all())

    display_courses.short_description = "Courses"
