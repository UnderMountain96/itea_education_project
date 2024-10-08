from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone

from .managers import PostPublishedManager

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50)

    class Meta:
        verbose_name = 'categories'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_CHOICES = (
        ('d', 'Draft'),
        ('p', 'Published')
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique_for_date='publish')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts')
    body = models.TextField(verbose_name='Content')
    publish = models.DateTimeField(default=timezone.localtime)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image_url = models.URLField(max_length=255)
    status = models.CharField(max_length=1,
                              choices=STATUS_CHOICES,
                              default='d')
    category = models.ForeignKey(Category,
                                 on_delete=models.PROTECT,
                                 related_name='posts')
    objects = models.Manager()
    published = PostPublishedManager()

    class Meta:
        ordering = ('-publish', '-created')
        indexes = [
            models.Index(fields=['-publish', '-created'])
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'blog:post_detail',
            args=[
                self.publish.year,
                self.publish.month,
                self.publish.day,
                self.slug
            ]
        )

    def likes_count(self):
        return self.likes.count()

    def dislikes_count(self):
        return self.dislikes.count()

    def is_liked_by(self, user) -> bool:
        return self.likes.filter(user=user).exists()

    def is_disliked_by(self, user) -> bool:
        return self.dislikes.filter(user=user).exists()


class PostLike(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='likes')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='post_likes')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')


class PostDisLike(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='dislikes')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='post_dislikes')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments')
    body = models.TextField(verbose_name='Content')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('-updated', '-created')
        indexes = [
            models.Index(fields=['-updated', '-created'])
        ]

    def __str__(self):
        return f'{self.author.username} - {self.post.title}'

    def likes_count(self):
        return self.likes.count()

    def dislikes_count(self):
        return self.dislikes.count()

    def is_liked_by(self, user) -> bool:
        return self.likes.filter(user=user).exists()

    def is_disliked_by(self, user) -> bool:
        return self.dislikes.filter(user=user).exists()


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment,
                                on_delete=models.CASCADE,
                                related_name='likes')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='comment_likes')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user')


class CommentDislike(models.Model):
    comment = models.ForeignKey(Comment,
                                on_delete=models.CASCADE,
                                related_name='dislikes')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='comment_dislikes')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user')


class Follow(models.Model):
    follower = models.ForeignKey(User,
                                 on_delete=models.CASCADE,
                                 related_name='following')
    followed = models.ForeignKey(User,
                                 on_delete=models.CASCADE,
                                 related_name='followed')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')

    def is_following(self, followed_user: User) -> bool:
        return Follow.objects.filter(follower=self.follower, followed=followed_user).exists()

    def is_followed_by(self, follower_user: User) -> bool:
        return Follow.objects.filter(followed=self.followed, follower=follower_user).exists()
