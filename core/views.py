from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authentication.models import User

# from core.CustomPagination import CustomPagination
from core.serializers import (
    CommentSerializer,
    FollowersSerializer,
    FollowingsSerializer,
    FollowSerializer,
    LikeSerializer,
    PostGetSerializer,
    PostSerializer,
    StudentSerializer
)

from .models import Comment, Follow, Like, Post, Student
from .permissions import IsOwnerOrReadOnly
from .tasks import send_post_creation_email
from .tasks import send_comment_creation_email

# from django.shortcuts import get_object_or_404


class PostCreateAPIView(CreateAPIView):
    """
    This view is used to create post
    """

    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if "user" not in request.data:
            request.data["user"] = request.user.id

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"msg": "Post Created Successfully!"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class PostCreateAPIView(CreateAPIView):
#     """
#     This view is used to create post
#     """

#     serializer_class = PostSerializer
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         if "user" not in request.data:
#             request.data["user"] = request.user.id

#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             post = serializer.save()
#             # Trigger the post creation email task asynchronously using Celery
#             send_post_creation_email.delay(post.uuid)  # This sends email in the background using uuid
#             return Response(
#                 {"msg": "Post Created Successfully!"},
#                 status=status.HTTP_201_CREATED,
#             )

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostRetrieveAPIView(RetrieveAPIView):
    """
    This view is used to retrieve post on given id
    """

    queryset = Post.objects.all()
    serializer_class = PostGetSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        # post = Post.objects.filter(pk=pk).first()
        post = self.get_object()

        if post:
            # serializer = PostGetSerializer(post)
            serializer = self.get_serializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"errors": {"msg": "Invalid Post Id!"}},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PostListAPIView(ListAPIView):
    """
    This view will show all the post.
    """

    queryset = Post.objects.all()
    serializer_class = PostGetSerializer
    # permission_classes = [IsAuthenticated]


class PostUpdateAPIView(UpdateAPIView):
    """ "
    This view will update the post
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def put(self, request, pk, *args, **kwargs):
        if "user" not in request.data:
            request.data["user"] = request.user.id

        # post = Post.objects.filter(pk=pk).first()
        # post = get_object_or_404(Post, pk=pk)
        post = self.get_object()

        if post:
            # serializer = PostSerializer(post, data=request.data)
            serializer = self.get_serializer(post, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {"msg": "Post Updated Successfully!"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"errors": {"msg": "Invalid Post Id!"}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk, *args, **kwargs):
        if "user" not in request.data:
            request.data["user"] = request.user.id

        # post = Post.objects.filter(pk=pk).first()
        post = self.get_object()

        if post:
            # serializer = PostSerializer(post, data=request.data,
            #                             partial=True)
            serializer = self.get_serializer(
                post, data=request.data, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {"msg": "Post Updated Partially!"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"errors": {"msg": "Invalid Post Id!"}},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PostDeleteAPIView(DestroyAPIView):
    """
    This view will delete the post based on a given id
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def delete(self, request, pk, *args, **kwargs):
        # post = Post.objects.filter(pk=pk).first()
        post = self.get_object()

        if post:
            post.delete()
            return Response(
                {"msg": "Post Deleted Successfully!"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"errors": {"msg": "Invalid Post Id!"}},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PostCommentsListAPIView(ListAPIView):
    """
    This view will show all comment on given post
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        likes = comments = 0
        post_data = {}

        all_comments = Comment.objects.filter(post=pk)
        if all_comments is not None:
            comment_serializer = CommentSerializer(all_comments, many=True)
            comments = all_comments.count()
            post_data["Count Of Comments"] = all_comments.count()
            post_data["Comments"] = comment_serializer.data

        all_likes = Like.objects.filter(post=pk)
        if all_likes is not None:
            like_serializer = LikeSerializer(all_likes, many=True)
            likes = len(like_serializer.data)
            post_data["Count Of Likes"] = likes

        if likes == 0 and comments == 0:
            return Response(
                {"msg": "No Likes and Comments on this Post!"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(post_data, status=status.HTTP_200_OK)


class CommentListAPIView(ListAPIView):
    """
    This view will show all comment of all the post
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        comments = Comment.objects.filter(user=pk)
        if comments:
            serializer = self.get_serializer(comments, many=True)
            return Response(
                {
                    "Count Of Comments": comments.count(),
                    "Comments": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"msg": "No Comments available for this User!"},
            status=status.HTTP_404_NOT_FOUND,
        )


# class CommentCreateAPIView(CreateAPIView):
#     """
#     This view will create comment on the post
#     """

#     serializer_class = CommentSerializer
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         if "user" not in request.data:
#             request.data["user"] = request.user.id

#         if "post" not in request.data:
#             return Response(
#                 {"msg": "Post ID is required!"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(
#                 {"msg": "Comment Created Successfully!"},
#                 status=status.HTTP_201_CREATED,
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentCreateAPIView(CreateAPIView):
    """
    This view will create comment on the post
    """

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if "user" not in request.data:
            request.data["user"] = request.user.id

        if "post" not in request.data:
            return Response(
                {"msg": "Post ID is required!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            comment = serializer.save()
            # Trigger the comment creation email task asynchronously using Celery
            send_comment_creation_email.delay(comment.id)  # This sends email in the background
            return Response(
                {"msg": "Comment Created Successfully!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentDeleteAPIView(DestroyAPIView):
    """
    This view will delete the comment based on a given id
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def delete(self, request, pk, *args, **kwargs):

        comment = self.get_object()

        if comment:
            comment.delete()
            return Response(
                {"msg": "comment Deleted Successfully!"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"errors": {"msg": "Invalid comment Id!"}},
            status=status.HTTP_400_BAD_REQUEST,
        )


class CommentUpdateAPIView(UpdateAPIView):
    """
    This view will update the comment
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def put(self, request, pk, *args, **kwargs):
        if "user" not in request.data:
            request.data["user"] = request.user.id
        comment = self.get_object()

        if comment:
            serializer = self.get_serializer(comment, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {"msg": "Comment Updated Successfully!"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"errors": {"msg": "Invalid Comment Id!"}},
            status=status.HTTP_400_BAD_REQUEST,
        )


class FollowersListAPIView(ListAPIView):
    """ "
    This view will show all the follower follow the login user
    """

    queryset = Follow.objects.all()
    serializer_class = FollowersSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        followers = Follow.objects.filter(user_following=pk)
        if followers:
            serializer = self.get_serializer(followers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"msg": "No Followers for this User!"},
            status=status.HTTP_404_NOT_FOUND,
        )


class FollowersCreateAPIView(CreateAPIView):

    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):

        user = request.user
        user_following = User.objects.filter(pk=pk).first()

        data = {"user": user.id, "user_following": user_following.id}

        if Follow.objects.filter(
            user=request.user, user_following=pk
        ).exists():
            msg = {"msg": "You are already following this user."}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"msg": "Follow Created Successfully!"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowingListAPIView(ListAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowingsSerializer
    # serializer_class = FollowingsSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        following = Follow.objects.filter(user=pk)
        if following:
            serializer = self.get_serializer(following, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"msg": "No Followings for this User!"},
            status=status.HTTP_404_NOT_FOUND,
        )


# class LikeCreateAPIView(CreateAPIView):
#     """
#     This view will create the user want to like the post"""
#     serializer_class = LikeSerializer
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         if "user" not in request.data:
#             request.data["user"] = request.user.id

#         user_id = int(request.data["user"])
#         post_id = request.data["post"]
#         likes = Like.objects.filter(user=user_id, post=post_id).exists()

#         if likes:
#             return Response(
#                 {"msg": "Already Liked!"}, status=status.HTTP_200_OK
#             )

#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(
#                 {"msg": "Liked Successfully!"},
# status=status.HTTP_201_CREATED
#             )
#         return Response(serializer.errors,
# status=status.HTTP_400_BAD_REQUEST)


class LikeCreateAPIView(CreateAPIView):
    """
    This view will create a like for a post by the user.
    """

    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Ensure the user field is set
        if "user" not in request.data:
            request.data["user"] = request.user.id

        # Ensure the post field is present
        if "post" not in request.data:
            return Response(
                {"error": "Post ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = int(request.data["user"])
        post_id = request.data["post"]

        # Check if the like already exists.
        likes = Like.objects.filter(user=user_id, post=post_id).exists()

        if likes:
            return Response(
                {"msg": "Already Liked!"}, status=status.HTTP_200_OK
            )

        # Proceed with the serialization and saving the like
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"msg": "Liked Successfully!"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikeRetrieveAPIView(RetrieveAPIView):
    """
    This view is used to get the specified Like details
    """

    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        like = Like.objects.filter(pk=pk).first()
        if like is not None:
            serializer = self.get_serializer(like)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"errors": {"msg": "Invalid Like Id!"}},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LikeListAPIView(ListAPIView):
    """
    This view will show all the likes on post"""

    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]


# --------------------------------------------------------------------------------------
#  fetch all students whose name starts with 'S'.
class StudentByNameAPIView(APIView):
    def post(self, request, *args, **kwargs):
        name_start = request.data.get('name_start', None)
        if name_start is None:
            return Response({"error": "name_start parameter is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        students = Student.objects.filter(name__startswith=name_start)

        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


#  fetch all students but exclude those whose name starts with 'S'.
class StudentsExcludingSAPIView(APIView):
    def post(self, request, *args, **kwargs):
        input_name = request.data.get("input_name", None)
        letter_exclude = Student.objects.exclude(id__in=Student.objects.filter
                                                 (name__startswith=input_name)
                                                 .values_list('id', flat=True))
        serializer = StudentSerializer(letter_exclude, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# fetch all students who email is exactly 'so@gmail.com'.
class StudentByEmailAPIView(APIView):

    def get(self, request, *args, **kwargs):
        email_is = request.query_params.get('email_is', 'so@gmail.com')
        students = Student.objects.filter(email=email_is)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# fetch all students who are learning from teacher named Neha.
class StudentLearnByTeacherAPIView(APIView):

    def post(self, request, *args, **kwargs):
        teacher_name = request.data.get('teacher_name', None)
        if teacher_name is None:
            return Response({"error": "teacher_name is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        students = Student.objects.filter(courses__teacher__name=teacher_name)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# write a query to print the total no. of students in the database.
class TotalStudentsAPIView(APIView):

    def get(self, request, *args, **kwargs):
        total_students = Student.objects.count()
        return Response({"total_students": total_students},
                        status=status.HTTP_200_OK)


#  all students who are enrolled in Python subject.
class StudentEnrolledSubjectAPIView(APIView):

    def post(self, request, *args, **kwargs):
        enrolled_sub = request.data.get('enrolled_sub', None)
        if enrolled_sub is None:
            return Response({"error": "enrolled_sub is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        students = Student.objects.filter(courses__subject=enrolled_sub)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
# -------------------------------------------------------------------------
#  1. fetch all students whose name starts with 'ab'.
# 2. fetch all students who email is exactly 'abc@gmail.com'.
# 3. fetch all students but exclude those whose name starts with 'H'.
# 4. fetch all students who are learning from teacher named Andrew.
# 5. fetch all students whose name is 'abc' or roll no. is greater than 10.
# 6. all students who are enrolled in english subject.
# 7. find all courses which are taught by teacher named Andrew.

# 8. write a query to print student name in all courses without hitting
# (n+1 queries).
# 9. write a query to print the total no. of students in the database.


class StudentFilterAPIView(APIView):

    def get(self, request, *args, **kwargs):
        # fetch all students whose name starts with 'So'
        students_name_So = Student.objects.filter(name__startswith='So')

        # fetch all students but exclude those whose name starts with 'S'.
        students_name_not_S = Student.objects.exclude(name__startswith='S')

        # fetch all students who email is exactly 'so@gmail.com'.
        students_email_exact = Student.objects.filter(email='so@gmail.com')

        # fetch all students who are learning from teacher named Neha.
        students_teacher_neha = Student.objects.filter(
            courses__teacher__name='Neha')

        #  all students who are enrolled in Python subject.
        students_enrolled_python = Student.objects.filter(
            courses__name='Python')

        #  find all courses which are taught by teacher named Poja.
        student_teacher_poja = Student.objects.filter(
            courses__teacher__name='Poja')

        # write a query to print the total no. of students in the database.
        # total_students = Student.objects.all().count()

        # write a query to print student name in all courses without hitting
# (n+1 queries).
        students = Student.objects.prefetch_related('courses')
        for student in students:
            print(f"Student: {student.name}")
            for course in student.courses.all():
                print(f"  Course: {course.name}")

        combined_queryset = students_name_So | students_name_not_S | students_email_exact | students_teacher_neha | students_enrolled_python | student_teacher_poja

        students = combined_queryset.distinct()
        serializer = StudentSerializer(students, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
