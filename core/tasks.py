# blogging/tasks.py

from celery import shared_task
from .models import Post, Comment
from django.core.mail import send_mail
from django.contrib.auth.models import User
from time import sleep


# Task for sending email after post creation (simulate email sending delay)
@shared_task
def send_post_creation_email(post_id):
    post = Post.objects.get(uuid=post_id)
    user = post.user  # Assuming post has a user field

    # Simulate email sending (you would actually use Django's email system)
    subject = "New Post Created!"
    message = f"Dear {user.username},\n\nYour post titled '{post.title}' has been successfully created!"
    recipient_list = [user.email]

    # Simulate a delay to demonstrate asynchronous behavior
    sleep(5)
    send_mail(subject, message, 'from@example.com', recipient_list)

    return f"Post creation email sent to {user.email}"


# Task for sending email after comment creation (simulate email sending delay)
@shared_task
def send_comment_creation_email(comment_id):
    comment = Comment.objects.get(id=comment_id)
    post = comment.post  # Get the post the comment belongs to
    user = post.user  # Assuming post has a user field

    subject = "New Comment on Your Post!"
    message = f"Dear {user.username},\n\nA new comment has been posted on your post titled '{post.title}'."
    recipient_list = [user.email]

    # Simulate a delay
    sleep(5)
    send_mail(subject, message, 'from@example.com', recipient_list)

    return f"Comment creation email sent to {user.email}"
