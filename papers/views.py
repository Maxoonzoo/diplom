from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils.translation import gettext_lazy as _
from .models import Paper, Tag
from datetime import datetime

def home(request):
    # Get top 5 tags for each category
    categories = ['author', 'year', 'field', 'paper_type']
    top_tags = {}
    for category in categories:
        top_tags[category] = Tag.objects.filter(category=category).annotate(
            num_papers=Count('papers')
        ).order_by('-num_papers')[:5]
    
    return render(request, 'papers/home.html', {'top_tags': top_tags})

def search_results(request):
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'latest')
    selected_tags = request.GET.getlist('tags')
    
    papers = Paper.objects.all()
    
    if query:
        papers = papers.filter(Q(title__icontains=query))
    
    if selected_tags:
        papers = papers.filter(tags__id__in=selected_tags).distinct()
    
    if sort == 'popular':
        papers = papers.order_by('-view_count')
    else:
        papers = papers.order_by('-upload_date')
    
    # Increment view count for displayed papers
    for paper in papers:
        paper.view_count += 1
        paper.save()
    
    tags = Tag.objects.all()
    return render(request, 'papers/search_results.html', {
        'papers': papers,
        'query': query,
        'sort': sort,
        'tags': tags,
        'selected_tags': selected_tags,
    })

@login_required
def upload_paper(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        creation_year = request.POST.get('creation_year')
        file = request.FILES.get('file')
        tags = request.POST.getlist('tags')
        
        if title and creation_year and file:
            try:
                creation_year = int(creation_year)
                paper = Paper.objects.create(
                    title=title,
                    description=description,
                    creation_year=creation_year,
                    file=file
                )
                paper.tags.set(tags)
                return redirect('home')
            except ValueError:
                error = _("Invalid year format")
        else:
            error = _("Title, year, and file are required")
        return render(request, 'papers/upload.html', {'error': error})
    
    tags = Tag.objects.all()
    return render(request, 'papers/upload.html', {'tags': tags})

def tag_list(request, category):
    tags = Tag.objects.filter(category=category).annotate(
        num_papers=Count('papers')
    ).order_by('-num_papers')
    return render(request, 'papers/tag_list.html', {
        'category': category,
        'tags': tags,
    })