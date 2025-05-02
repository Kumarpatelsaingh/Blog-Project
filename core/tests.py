import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Like, Post

User = get_user_model()


@pytest.mark.django_db
def test_create_post_success():
    client = APIClient()

    # Create and authenticate user with required fields (first_name, last_name, and gender).
    # This creates a new user in your test database with all required fields.
    user = User.objects.create_user(
        email="test@example.com",
        password="strongpass123",
        first_name="Test",
        last_name="User",
        gender="M",
    )
    client.force_authenticate(user=user)

    payload = {"title": "Test Post", "content": "This is a test post content"}

    response = client.post("/api/post/create/", data=payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["msg"] == "Post Created Successfully!"


# ---------------------------------------------------------------------------
@pytest.fixture
def user(db):
    """Fixture to create a user for testing"""
    return User.objects.create_user(
        first_name="Test",
        last_name="User",
        email="testuser@example.com",
        password="strongpassword123",
        gender="M",
    )

@pytest.fixture
def auth_client(user):
    """Authenticated API client"""
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def post(user):
    """Fixture to create a post for testing"""
    return Post.objects.create(
        user=user,
        title="Test Post",
        content="This is a test post content",
    )

@pytest.mark.django_db
def test_retrieve_post_success(auth_client, post):
    """Test that the post can be retrieved successfully"""
    url = f"/api/post/get/{post.uuid}/"
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["uuid"] == str(post.uuid)
    assert response.data["title"] == post.title
    assert response.data["content"] == post.content

@pytest.mark.django_db
def test_retrieve_post_invalid_id(auth_client):
    """Test that trying to retrieve a post with an invalid ID returns an error"""
    invalid_uuid = "123e4567-e89b-12d3-a456-426614174000"
    url = f"/api/post/get/{invalid_uuid}/"
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in response.data
    assert "No Post matches the given query." in str(response.data["detail"])

# -----------------------------------------------------------------------------------------------
@pytest.fixture
def multiple_posts(user):
    return [
        Post.objects.create(user=user, title="Post 1", content="Content 1"),
        Post.objects.create(user=user, title="Post 2", content="Content 2"),
        Post.objects.create(user=user, title="Post 3", content="Content 3"),
    ]


@pytest.mark.django_db
def test_post_list_api_returns_all_posts(user, multiple_posts):
    client = APIClient()
    # If authentication is enabled, uncomment the next line
    # client.force_authenticate(user=user)

    response = client.get("/api/post/list/")  # Adjust the URL if needed

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3
    titles = [post["title"] for post in response.data]
    assert "Post 1" in titles
    assert "Post 2" in titles
    assert "Post 3" in titles

# --------------------------------------------------------------------------------
@pytest.mark.django_db
def test_delete_post_success(auth_client, post):
    """Test successful deletion of a post"""
    url = f"/api/post/delete/{post.uuid}/"
    response = auth_client.delete(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["msg"] == "Post Deleted Successfully!"
    assert not Post.objects.filter(uuid=post.uuid).exists()

@pytest.mark.django_db
def test_delete_post_invalid_id(auth_client):
    """Test deletion with invalid post UUID"""
    invalid_uuid = "123e4567-e89b-12d3-a456-426614174000"
    url = f"/api/post/delete/{invalid_uuid}/"
    response = auth_client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in response.data
# -------------------------------------------------------------------------------------------------

@pytest.mark.django_db
def test_post_comments_and_likes_list_success():
    """
    Test that comments and likes can be retrieved successfully for a given post.
    """
    client = APIClient()

    # Create and authenticate a user
    user = get_user_model().objects.create_user(
        email="testuser@example.com",
        password="password123",
        first_name="Test",
        last_name="User",
        gender="M",
    )
    client.force_authenticate(user=user)

    # Create a post
    post = Post.objects.create(
        user=user, title="Test Post", content="This is a test post"
    )
    # Create likes for the post (Use get_or_create to avoid IntegrityError due to UNIQUE constraint)
    Like.objects.get_or_create(post=post, user=user)
    url = f"/api/comments/post/{post.uuid}/"
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert "Count Of Likes" in response.data
    assert response.data["Count Of Likes"] == 1


@pytest.mark.django_db
def test_post_comments_and_likes_list_no_comments_no_likes():
    """
    Test that a post with no comments or likes returns a 404 error with the appropriate message.
    """
    client = APIClient()

    # Create and authenticate a user
    user = get_user_model().objects.create_user(
        email="testuser@example.com",
        password="password123",
        first_name="Test",
        last_name="User",
        gender="M",
    )
    client.force_authenticate(user=user)

    # Create a post without comments or likes
    post = Post.objects.create(
        user=user,
        title="Test Post Without Comments or Likes",
        content="This post has no comments or likes",
    )

    url = f"/api/comments/post/{post.uuid}/"
    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data == {"msg": "No Likes and Comments on this Post!"}
# ---------------------------------------------------------------------------------------
@pytest.mark.django_db
def test_update_post_success():
    """
    Test that a user can successfully update their own post.
    """
    client = APIClient()

    # Create and authenticate a user
    user = get_user_model().objects.create_user(
        email="testuser@example.com",
        password="password123",
        first_name="Test",
        last_name="User",
        gender="M",
    )
    client.force_authenticate(user=user)

    # Create a post by the authenticated user
    post = Post.objects.create(
        user=user, title="Original Title", content="Original content"
    )

    # Define the updated data
    updated_data = {"title": "Updated Title", "content": "Updated content"}

    url = f"/api/post/update/{post.uuid}/"
    response = client.put(url, data=updated_data, format="json")

    assert response.status_code == status.HTTP_200_OK

    assert response.data["msg"] == "Post Updated Successfully!"

    post.refresh_from_db()

    assert post.title == updated_data["title"]
    assert post.content == updated_data["content"]
