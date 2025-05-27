from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Count, Q
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Paper, Tag
from django.utils import timezone
import datetime

def home(request):
    query = request.GET.get('q', '')
    top_tags = {
        'author': Tag.objects.filter(category='author', status='approved').annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))[:5],
        'year': Tag.objects.filter(category='year', status='approved').annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))[:5],
        'field': Tag.objects.filter(category='field', status='approved').annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))[:5],
        'paper_type': Tag.objects.filter(category='paper_type', status='approved').annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))[:5],
    }
    return render(request, 'papers/home.html', {'top_tags': top_tags, 'query': query})

def search_results(request):
    query = request.GET.get('q', '')
    selected_author_tags = request.GET.getlist('tags_author')
    selected_field_tags = request.GET.getlist('tags_field')
    selected_paper_type_tags = request.GET.getlist('tags_paper_type')
    selected_year_tags = request.GET.getlist('tags_year')
    sort = request.GET.get('sort', 'latest')

    papers = Paper.objects.filter(status='approved')
    tags = {
        'author': Tag.objects.filter(category='author', status='approved'),
        'field': Tag.objects.filter(category='field', status='approved'),
        'paper_type': Tag.objects.filter(category='paper_type', status='approved'),
        'year': Tag.objects.filter(category='year', status='approved'),
    }

    if query:
        papers = papers.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if selected_author_tags:
        papers = papers.filter(tags__id__in=selected_author_tags).distinct()
    if selected_field_tags:
        papers = papers.filter(tags__id__in=selected_field_tags).distinct()
    if selected_paper_type_tags:
        papers = papers.filter(tags__id__in=selected_paper_type_tags).distinct()
    if selected_year_tags:
        papers = papers.filter(tags__id__in=selected_year_tags).distinct()
    if sort == 'popular':
        papers = papers.order_by('-view_count')
    else:
        papers = papers.order_by('-upload_date')

    return render(request, 'papers/search_results.html', {
        'papers': papers,
        'tags': tags,
        'query': query,
        'selected_author_tags': selected_author_tags,
        'selected_field_tags': selected_field_tags,
        'selected_paper_type_tags': selected_paper_type_tags,
        'selected_year_tags': selected_year_tags,
        'sort': sort,
    })

def paper_detail(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    all_tags = paper.tags.all()  # Get all tags associated with the paper
    return render(request, 'papers/paper_detail.html', {'paper': paper, 'all_tags': all_tags})

def upload_paper(request):
    tags = {
        'author': Tag.objects.filter(category='author', status='approved'),
        'year': Tag.objects.filter(category='year', status='approved'),
        'field': Tag.objects.filter(category='field', status='approved'),
        'paper_type': Tag.objects.filter(category='paper_type', status='approved'),
    }
    error = None

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        file = request.FILES.get('file')
        uploader_name = request.POST.get('uploader_name') if not request.user.is_authenticated else None

        # Handle tags for each category
        new_tags = []
        selected_tags = []
        for category in ['author', 'year', 'field', 'paper_type']:
            tag_inputs = request.POST.getlist(f'tags_{category}')
            for tag_input in tag_inputs:
                if tag_input:
                    # Check if tag exists
                    existing_tag = Tag.objects.filter(category=category, name=tag_input, status='approved').first()
                    if existing_tag:
                        selected_tags.append(existing_tag.id)
                    else:
                        # Create a new tag with pending status
                        new_tag = Tag.objects.create(category=category, name=tag_input, status='pending')
                        new_tags.append(new_tag)
                        selected_tags.append(new_tag.id)

        if not (title and file):
            error = "Title and file are required"
        else:
            try:
                # No creation_year validation since it's optional
                pass
            except (ValueError, TypeError):
                error = "Invalid input"

        if not error:
            paper = Paper(
                title=title,
                description=description,
                file=file,
                upload_date=timezone.now(),
                view_count=0,
                status='pending',
                uploader_name=uploader_name
            )
            paper.save()
            if selected_tags:
                paper.tags.set(selected_tags)
            return redirect('home')

    return render(request, 'papers/upload.html', {'tags': tags, 'error': error})

@user_passes_test(lambda u: u.is_superuser)
def moderate_papers(request):
    pending_papers = Paper.objects.filter(status='pending')
    # Prepare a list of papers with their pending tags
    papers_with_pending_tags = []
    for paper in pending_papers:
        pending_tags = paper.tags.filter(status='pending')
        papers_with_pending_tags.append({
            'paper': paper,
            'pending_tags': pending_tags
        })
    return render(request, 'papers/moderate_papers.html', {'papers_with_pending_tags': papers_with_pending_tags})

@user_passes_test(lambda u: u.is_superuser)
def approve_paper(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    paper.status = 'approved'
    paper.save()
    # Approve associated pending tags
    pending_tags = paper.tags.filter(status='pending')
    for tag in pending_tags:
        tag.status = 'approved'
        tag.save()
    return redirect('moderate_papers')

@user_passes_test(lambda u: u.is_superuser)
def reject_paper(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    paper.status = 'rejected'
    paper.save()
    # Reject associated pending tags
    pending_tags = paper.tags.filter(status='pending')
    for tag in pending_tags:
        tag.status = 'rejected'
        tag.save()
    return redirect('moderate_papers')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('moderate_papers')
            else:
                return redirect('home')
        else:
            error = "Invalid username or password"
            return render(request, 'papers/login.html', {'error': error})
    return render(request, 'papers/login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

def tag_list(request, category):
    tags = Tag.objects.filter(category=category, status='approved').annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
    return render(request, 'papers/tag_list.html', {'tags': tags, 'category': category})

def get_current_language(request):
    from django.utils.translation import get_language
    return HttpResponse(f"Current language: {get_language()}")