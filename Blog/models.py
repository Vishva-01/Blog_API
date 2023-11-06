from django.db import models
from django.contrib.auth.models import User

class TagModel(models.Model):
    tag = models.CharField(max_length=25)

    def __str__(self) -> str:
        return self.tag
    
class BlogModel(models.Model):
    title = models.CharField(max_length=50)
    about = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Approved')
    tag=models.ManyToManyField(TagModel)

    def __str__(self):
        return self.title
    
class CommentModel(models.Model):
    comment = models.TextField()
    blog = models.ForeignKey(BlogModel,on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class MailModel(models.Model):
    email = models.EmailField(unique=True)
    subscribed = models.BooleanField(default=False)