from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from ckeditor_uploader.fields import RichTextUploadingField




# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse("home")



class UserProfile(models.Model):
    user = models. OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    bio = models.TextField()
    profile_pic = models.ImageField(blank=True, null=True, upload_to="images/profile/", default='images/profile/profile1.png/')
    website_url = models.CharField(max_length=250, blank=True, null=True)
    facebook_url = models.CharField(max_length=250, blank=True, null=True)
    twitter_url = models.CharField(max_length=250, blank=True, null=True)
    instagram_url = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return str(self.user)


class Post(models.Model):
    options = (
        ('draft', 'Draft'),
        ('published', 'Published')
    )

    title = models.CharField(max_length=250)
    created_on = models.DateTimeField(default=timezone.now)
    header_image = models.ImageField(blank=True, null=True, upload_to="images/")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')
    text = RichTextUploadingField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=options, default='draft')
    category = models.ManyToManyField(Category, related_name="blog_category")
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="blog_likes")
    # fields = (title, created_on, header_image, text, category)
    # labels = {
    #         'title': 'Title',
    #         'created_on': 'Date',
    #         'header_image': 'Featured Image',
    #         'text': '',
    #         'category': 'Categories',
    #     }

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse("home")
    
    class Meta:
        ordering = ['-created_on']


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    body = models.TextField()
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.name}'

    # def get_absolute_url(self):
    #     return reverse('post',kwargs={'pk':'self.post.id'})