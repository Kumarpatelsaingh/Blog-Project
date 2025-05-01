from django.urls import path

from core.views import (
    CommentCreateAPIView,
    CommentDeleteAPIView,
    CommentListAPIView,
    CommentUpdateAPIView,
    FollowersCreateAPIView,
    FollowersListAPIView,
    FollowingListAPIView,
    LikeCreateAPIView,
    LikeListAPIView,
    LikeRetrieveAPIView,
    PostCommentsListAPIView,
    PostCreateAPIView,
    PostDeleteAPIView,
    PostListAPIView,
    PostRetrieveAPIView,
    PostUpdateAPIView,
    # StudentByEmailAPIView,
    # StudentByNameAPIView,
    # StudentEnrolledSubjectAPIView,
    # StudentFilterAPIView,
    # StudentLearnByTeacherAPIView,
    # StudentsExcludingSAPIView,
    # TotalStudentsAPIView,
)

urlpatterns = [
    path("post/create/", PostCreateAPIView.as_view(), name="postcreate"),
    path("post/get/<uuid:pk>/", PostRetrieveAPIView.as_view(), name="postget"),
    path("post/list/", PostListAPIView.as_view(), name="postlist"),
    path("post/update/<uuid:pk>/", PostUpdateAPIView.as_view(), name="postupdate"),
    path("post/delete/<uuid:pk>/", PostDeleteAPIView.as_view(), name="postdelete"),
    path(
        "comments/post/<uuid:pk>/", PostCommentsListAPIView.as_view(), name="postdata"
    ),
    path("comments/user/<int:pk>/", CommentListAPIView.as_view(), name="commentuser"),
    path("comment/create/", CommentCreateAPIView.as_view(), name="commentcreate"),
    path(
        "comment/delete/<uuid:pk>/",
        CommentDeleteAPIView.as_view(),
        name="commentdelete",
    ),
    path(
        "comment/update/<uuid:pk>/",
        CommentUpdateAPIView.as_view(),
        name="commentupdate",
    ),
    path(
        "followers/user/<int:pk>/",
        FollowersListAPIView.as_view(),
        name="followers_of_user",
    ),
    path(
        "followings/user/<int:pk>/",
        FollowingListAPIView.as_view(),
        name="following_of_user",
    ),
    path(
        "follower/create/<int:pk>/",
        FollowersCreateAPIView.as_view(),
        name="followercreate",
    ),
    path("like/create/", LikeCreateAPIView.as_view(), name="likecreate"),
    path("like/get/<uuid:pk>/", LikeRetrieveAPIView.as_view(), name="likeget"),
    path("like/list/", LikeListAPIView.as_view(), name="likelist"),
    # path("students/name/", StudentByNameAPIView.as_view(), name="student-by-name"),
    # path("students/email/", StudentByEmailAPIView.as_view(), name="student-by-name"),
    # path(
    #     "students/teacher/",
    #     StudentLearnByTeacherAPIView.as_view(),
    #     name="student-by-teacher",
    # ),
    # path(
    #     "students/exclude/", StudentsExcludingSAPIView.as_view(), name="student-by-name"
    # ),
    # path("students/total/", TotalStudentsAPIView.as_view(), name="student-total"),
    # path(
    #     "students/subject/", StudentEnrolledSubjectAPIView.as_view(), name="student-sub"
    # ),
    # path("students/all/", StudentFilterAPIView.as_view(), name="student-sub"),
]
