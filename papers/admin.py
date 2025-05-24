from django.contrib import admin
from .models import Paper, Tag

@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'creation_year', 'upload_date', 'view_count')
    list_filter = ('creation_year', 'tags')
    search_fields = ('title', 'description')
    filter_horizontal = ('tags',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)