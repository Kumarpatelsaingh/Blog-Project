from rest_framework import serializers

from authentication.serializers import UserDataSerializer
from core.models import Comment, Follow, Like, Post, Student, Course, Teacher


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = "__all__"


class PostGetSerializer(serializers.ModelSerializer):
    user = UserDataSerializer()
    count_comments = serializers.SerializerMethodField()
    count_likes = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = "__all__"

    def get_count_comments(self, obj):
        return Comment.objects.filter(post__user=obj.user).count()

    def get_count_likes(self, obj):
        return Like.objects.filter(post__user=obj.user).count()

    def get_comments(self, obj):
        comments = Comment.objects.filter(post__user=obj.user)
        return CommentSerializer(comments, many=True).data

    def get_likes(self, obj):
        comments = Like.objects.filter(post__user=obj.user)
        return LikeSerializer(comments, many=True).data


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = "__all__"


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = "__all__"


class FollowersSerializer(serializers.ModelSerializer):
    user = UserDataSerializer()

    class Meta:
        model = Follow
        fields = ["uuid", "user"]


class FollowingsSerializer(serializers.ModelSerializer):
    user_following = UserDataSerializer()

    class Meta:
        model = Follow
        fields = ["uuid", "user_following"]


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'roll', 'address', 'email', 'courses']


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name']


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['name']