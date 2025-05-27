from django.db import models
from django.utils import timezone

class Paper(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    creation_year = models.IntegerField(null=True, blank=True)  # Made optional
    file = models.FileField(upload_to='papers/')
    upload_date = models.DateTimeField(auto_now_add=True)
    view_count = models.IntegerField(default=0)
    tags = models.ManyToManyField('Tag', related_name='papers')
    uploader_name = models.CharField(max_length=100, blank=True, null=True)  # For unauthenticated users

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.title

class Tag(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')  # Existing tags are approved

    def __str__(self):
        return self.name