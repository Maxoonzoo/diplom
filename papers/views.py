from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Count, Q
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from .models import Paper, Tag
from django.utils import timezone
import datetime
import logging

# Налаштування логування
logger = logging.getLogger(__name__)

def home(request):
    # Відображає головну сторінку з топ-тегами та пошуковим запитом
    query = request.GET.get('q', '')
    top_tags = {
        'author': Tag.objects.filter(category='author', status='approved')
                            .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                            .filter(num_papers__gt=0)
                            .order_by('-num_papers')[:5],
        'year': Tag.objects.filter(category='year', status='approved')
                          .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                          .filter(num_papers__gt=0)
                          .order_by('-num_papers')[:5],
        'field': Tag.objects.filter(category='field', status='approved')
                           .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                           .filter(num_papers__gt=0)
                           .order_by('-num_papers')[:5],
        'paper_type': Tag.objects.filter(category='paper_type', status='approved')
                                .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                                .filter(num_papers__gt=0)
                                .order_by('-num_papers')[:5],
    }
    return render(request, 'papers/home.html', {'top_tags': top_tags, 'query': query})

def search_results(request):
    # Обробляє пошук статей за запитом та фільтрами, сортує результати
    query = request.GET.get('q', '')
    selected_author_tags = request.GET.getlist('tags_author')
    selected_field_tags = request.GET.getlist('tags_field')
    selected_paper_type_tags = request.GET.getlist('tags_paper_type')
    selected_year_tags = request.GET.getlist('tags_year')
    sort = request.GET.get('sort', 'latest')

    papers = Paper.objects.filter(status='approved')
    tags = {
        'author': Tag.objects.filter(category='author', status='approved')
                            .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                            .filter(num_papers__gt=0)
                            .order_by('-num_papers')[:5],
        'field': Tag.objects.filter(category='field', status='approved')
                           .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                           .filter(num_papers__gt=0)
                           .order_by('-num_papers')[:5],
        'paper_type': Tag.objects.filter(category='paper_type', status='approved')
                                .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                                .filter(num_papers__gt=0)
                                .order_by('-num_papers')[:5],
        'year': Tag.objects.filter(category='year', status='approved')
                          .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                          .filter(num_papers__gt=0)
                          .order_by('-num_papers')[:5],
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
    # Відображає деталі конкретної статті та дозволяє видаляти для суперкористувача
    paper = get_object_or_404(Paper, id=paper_id)
    all_tags = paper.tags.all()
    top_tags = {
        'author': Tag.objects.filter(category='author', status='approved')
                            .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                            .filter(num_papers__gt=0)
                            .order_by('-num_papers')[:5],
        'field': Tag.objects.filter(category='field', status='approved')
                           .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                           .filter(num_papers__gt=0)
                           .order_by('-num_papers')[:5],
        'paper_type': Tag.objects.filter(category='paper_type', status='approved')
                                .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                                .filter(num_papers__gt=0)
                                .order_by('-num_papers')[:5],
        'year': Tag.objects.filter(category='year', status='approved')
                          .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                          .filter(num_papers__gt=0)
                          .order_by('-num_papers')[:5],
    }
    if request.method == 'POST' and request.user.is_superuser:
        paper.delete()
        logger.info(f"Paper {paper.id} - {paper.title} deleted by superuser")
        return redirect('moderate_papers')
    return render(request, 'papers/paper_detail.html', {'paper': paper, 'all_tags': all_tags, 'top_tags': top_tags, 'is_superuser': request.user.is_superuser})

def upload_paper(request):
    # Обробляє завантаження нової статті, перевіряє теги та зберігає
    tags = {
        'author': Tag.objects.filter(category='author', status='approved')
                            .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                            .filter(num_papers__gt=0),
        'year': Tag.objects.filter(category='year', status='approved')
                          .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                          .filter(num_papers__gt=0),
        'field': Tag.objects.filter(category='field', status='approved')
                           .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                           .filter(num_papers__gt=0),
        'paper_type': Tag.objects.filter(category='paper_type', status='approved')
                                .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                                .filter(num_papers__gt=0),
    }
    error = None

    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description', '')
            file = request.FILES.get('file')
            uploader_name = request.POST.get('uploader_name') if not request.user.is_authenticated else None

            if not (title and file):
                error = "Title and file are required"
                logger.error("Missing required fields: title or file")
                return render(request, 'papers/upload.html', {'tags': tags, 'error': error})

            categories = ['author', 'year', 'field', 'paper_type']
            selected_tags_by_category = {}
            missing_categories = []

            for category in categories:
                tag_input = request.POST.getlist(f'tags_{category}')
                if tag_input:
                    selected_tags_by_category[category] = tag_input
                    if not tag_input:
                        missing_categories.append(category)
                else:
                    missing_categories.append(category)

            if missing_categories:
                error = f"Each category must have at least one tag. Missing tags for: {', '.join(missing_categories)}"
                logger.error(f"Validation failed: {error}")
                return render(request, 'papers/upload.html', {'tags': tags, 'error': error})

            new_tags = []
            selected_tags = []
            for category in categories:
                for tag_input in selected_tags_by_category[category]:
                    existing_tag = Tag.objects.filter(category=category, name=tag_input, status='approved').first()
                    if existing_tag:
                        selected_tags.append(existing_tag.id)
                        logger.info(f"Existing tag found: {existing_tag}")
                    else:
                        new_tag = Tag.objects.create(category=category, name=tag_input, status='pending')
                        new_tags.append(new_tag)
                        selected_tags.append(new_tag.id)
                        logger.info(f"New tag created: {new_tag}")

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
            logger.info(f"Paper created: {paper.id} - {paper.title}")

            if selected_tags:
                paper.tags.set(selected_tags)
                logger.info(f"Tags set for paper {paper.id}: {selected_tags}")

            return redirect('home')

        except Exception as e:
            error = f"Error uploading paper: {str(e)}"
            logger.error(f"Error creating paper: {str(e)}")
            return render(request, 'papers/upload.html', {'tags': tags, 'error': error})

    return render(request, 'papers/upload.html', {'tags': tags, 'error': error})

@user_passes_test(lambda u: u.is_superuser)
def moderate_papers(request):
    # Відображає список статей на модерацію для суперкористувачів
    pending_papers = Paper.objects.filter(status='pending')
    logger.info(f"Moderation query returned {pending_papers.count()} papers")
    papers_with_pending_tags = []
    for paper in pending_papers:
        pending_tags = paper.tags.filter(status='pending')
        papers_with_pending_tags.append({
            'paper': paper,
            'pending_tags': pending_tags
        })
    logger.info(f"Processed {len(papers_with_pending_tags)} papers with pending tags")
    return render(request, 'papers/moderate_papers.html', {'papers_with_pending_tags': papers_with_pending_tags})

@user_passes_test(lambda u: u.is_superuser)
def approve_paper(request, paper_id):
    # Підтверджує статтю та її теги, доступно лише суперкористувачам
    paper = get_object_or_404(Paper, id=paper_id)
    paper.status = 'approved'
    paper.save()
    pending_tags = paper.tags.filter(status='pending')
    for tag in pending_tags:
        tag.status = 'approved'
        tag.save()
    return redirect('moderate_papers')

@user_passes_test(lambda u: u.is_superuser)
def reject_paper(request, paper_id):
    # Відхиляє статтю та її теги, доступно лише суперкористувачам
    paper = get_object_or_404(Paper, id=paper_id)
    paper.status = 'rejected'
    paper.save()
    pending_tags = paper.tags.filter(status='pending')
    for tag in pending_tags:
        tag.status = 'rejected'
        tag.save()
    return redirect('moderate_papers')

def user_login(request):
    # Обробляє вхід користувача, перенаправляє залежно від статусу
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
    # Виконує вихід користувача та перенаправляє на головну
    logout(request)
    return redirect('home')

def tag_list(request, category):
    # Відображає список тегів у вибраній категорії
    tags = Tag.objects.filter(category=category, status='approved').annotate(num_papers=Count('papers', filter=Q(papers__status='approved'))).filter(num_papers__gt=0)
    top_tags = {
        'author': Tag.objects.filter(category='author', status='approved')
                            .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                            .filter(num_papers__gt=0)
                            .order_by('-num_papers')[:5],
        'field': Tag.objects.filter(category='field', status='approved')
                           .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                           .filter(num_papers__gt=0)
                           .order_by('-num_papers')[:5],
        'paper_type': Tag.objects.filter(category='paper_type', status='approved')
                                .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                                .filter(num_papers__gt=0)
                                .order_by('-num_papers')[:5],
        'year': Tag.objects.filter(category='year', status='approved')
                          .annotate(num_papers=Count('papers', filter=Q(papers__status='approved')))
                          .filter(num_papers__gt=0)
                          .order_by('-num_papers')[:5],
    }
    return render(request, 'papers/tag_list.html', {'tags': tags, 'category': category, 'top_tags': top_tags})

def get_current_language(request):
    # Повертає поточну мову у відповідь
    from django.utils.translation import get_language
    return HttpResponse(f"Current language: {get_language()}")