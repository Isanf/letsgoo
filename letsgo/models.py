from django.db import models
from django.contrib.auth.models import User
# Create your models here.


#Purchage***********************************************************************************************************
class Purchage(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    purchage_date = models.DateField(auto_now_add=True)
    pack = models.IntegerField()
    activated = models.BooleanField(default=True)


#AccessTuto***********************************************************************************************************
class AccessTuto(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='creator')
    access_date = models.DateField(auto_now_add=True)


#Category********************************************************************************************************************
class Category(models.Model):
    title = models.CharField(max_length=100)
    thumbnail = models.ImageField(upload_to='categories/', default='none')

    def __str__(self):
        return self.title


class VideoPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    desc = models.TextField()
    video_file = models.FileField(upload_to='videos')
    thumbnail = models.ImageField(upload_to='videos/thumbnail/', default='none')
    category = models.CharField(max_length=50, default='none')
    pub_date = models.DateField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='likes')
    video_views = models.ManyToManyField(User, related_name='video_views')

    def __str__(self):
        return self.title


#Steper********************************************************************************************************************
class StepPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(VideoPost, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    desc = models.TextField()
    video_file = models.FileField(upload_to='videos/steps')
    pub_date = models.DateField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='like')
    video_views = models.ManyToManyField(User, related_name='video_view')

    def __str__(self):
        return self.title


class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField()
    profile_pic = models.ImageField(upload_to='pic/', default='pic/default.jpg')
    subscribers = models.ManyToManyField(User, related_name='subscribers')




class Comment(models.Model):
    post = models.ForeignKey(VideoPost, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=300)

    def __str__(self):
        return self.user.username
