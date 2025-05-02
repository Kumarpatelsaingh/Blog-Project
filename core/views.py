from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# from rest_framework.views import APIView

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
)

from .models import Comment, Follow, Like, Post
from .permissions import IsOwnerOrReadOnly
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
            serializer = self.get_serializer(post, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {"msg": "Post Updated Partially!"},
                    status=status.HTTP_200_OK,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
            send_comment_creation_email.delay(
                comment.id
            )  # This sends email in the background
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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

        if Follow.objects.filter(user=request.user, user_following=pk).exists():
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
            return Response({"msg": "Already Liked!"}, status=status.HTTP_200_OK)

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