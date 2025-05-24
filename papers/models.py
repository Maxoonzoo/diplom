from django.db import models
from django.utils.translation import gettext_lazy as _

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50)  # e.g., 'author', 'year', 'field', 'paper_type'

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

class Paper(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='papers/')
    creation_year = models.PositiveIntegerField()
    upload_date = models.DateTimeField(auto_now_add=True)
    view_count = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, related_name='papers')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Paper")
        verbose_name_plural = _("Papers")