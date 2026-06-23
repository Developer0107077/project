from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Article, Category, Tag, Author, Vote


def author(request):
    context = {
        "social": Author.objects.first()
    }
    return render(request, "blog/author.html", context)


def _base_context():
    """Har bir view'ga kerak bo'ladigan umumiy ma'lumotlar."""
    return {
        "categories": Category.objects.annotate(
            article_count=Count(
                "articles",
                filter=Q(articles__status=Article.STATUS_PUBLISHED),
            )
        ).order_by("name"),
    }


def _get_client_ip(request):
    """Foydalanuvchi IP manzilini olish."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def index(request):
    published = Article.objects.filter(
        status=Article.STATUS_PUBLISHED
    ).select_related(
        "author__user", "category"
    ).prefetch_related("tags").annotate(
        annotated_likes=Count('votes', filter=Q(votes__vote_type='like')),
        annotated_dislikes=Count('votes', filter=Q(votes__vote_type='dislike'))
    ).order_by("-published_at")

    category_slug = request.GET.get("category")
    tag_slug      = request.GET.get("tag")
    search_query  = request.GET.get("q", "").strip()

    active_category = None
    active_tag      = None

    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        published = published.filter(category=active_category)

    if tag_slug:
        active_tag = get_object_or_404(Tag, slug=tag_slug)
        published  = published.filter(tags=active_tag)

    if search_query:
        published = published.filter(
            Q(title__icontains=search_query) |
            Q(subtitle__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    featured_articles = published.filter(is_featured=True)[:3]

    paginator = Paginator(published, per_page=6)
    page_num  = request.GET.get("page", 1)
    try:
        articles_page = paginator.page(page_num)
    except (PageNotAnInteger, EmptyPage):
        articles_page = paginator.page(1)

    ctx = _base_context()
    ctx.update({
        "title":             "Python.dev | Blog",
        "featured_articles": featured_articles,
        "articles_page":     articles_page,
        "active_category":   active_category,
        "active_tag":        active_tag,
        "search_query":      search_query,
        "tags":              Tag.objects.all(),
    })
    return render(request, "blog/index.html", ctx)


def article_detail(request, slug):
    article = get_object_or_404(
        Article.objects.select_related(
            "author__user", "category"
        ).prefetch_related("tags", "votes"),
        slug=slug,
        status=Article.STATUS_PUBLISHED,
    )

    # Ko'rishlar sonini oshirish (session orqali bir marta)
    session_key = f"viewed_article_{article.pk}"
    if not request.session.get(session_key):
        article.increment_views()
        request.session[session_key] = True

    # Like / Dislike hisoblash
    likes_count    = article.votes.filter(vote_type='like').count()
    dislikes_count = article.votes.filter(vote_type='dislike').count()

    # Foydalanuvchi ovozi (IP bo'yicha)
    ip = _get_client_ip(request)
    user_vote_obj = article.votes.filter(ip_address=ip).first()
    user_vote = user_vote_obj.vote_type if user_vote_obj else None

    # O'xshash maqolalar
    related_articles = Article.objects.filter(
        status=Article.STATUS_PUBLISHED,
        category=article.category,
    ).exclude(pk=article.pk).select_related("author__user", "category")[:3]

    ctx = _base_context()
    ctx.update({
        "article":          article,
        "likes_count":      likes_count,
        "dislikes_count":   dislikes_count,
        "user_vote":        user_vote,   # 'like' | 'dislike' | None
        "comment_count":    0,           # Izohlar modeli bo'lsa shu yerga qo'shing
        "related_articles": related_articles,
    })
    return render(request, "blog/article_detail.html", ctx)


def category_articles(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = Article.objects.filter(
        status=Article.STATUS_PUBLISHED,
        category=category,
    ).select_related("author__user", "category").prefetch_related("tags").annotate(
        annotated_likes=Count('votes', filter=Q(votes__vote_type='like')),
        annotated_dislikes=Count('votes', filter=Q(votes__vote_type='dislike'))
    ).order_by("-published_at")

    paginator     = Paginator(articles, per_page=6)
    articles_page = paginator.get_page(request.GET.get("page", 1))

    # Shu kategoriyaga tegishli teglar
    related_tags = Tag.objects.filter(
        articles__category=category,
        articles__status=Article.STATUS_PUBLISHED,
    ).distinct()

    ctx = _base_context()
    ctx.update({
        "category":      category,
        "articles_page": articles_page,
        "related_tags":  related_tags,
    })
    return render(request, "blog/category.html", ctx)


def tag_articles(request, slug):
    tag      = get_object_or_404(Tag, slug=slug)
    articles = Article.objects.filter(
        status=Article.STATUS_PUBLISHED,
        tags=tag,
    ).select_related("author__user", "category").prefetch_related("tags")

    paginator     = Paginator(articles, per_page=6)
    articles_page = paginator.get_page(request.GET.get("page", 1))

    ctx = _base_context()
    ctx.update({
        "tag":           tag,
        "articles_page": articles_page,
    })
    return render(request, "blog/tag.html", ctx)


def search(request):
    query   = request.GET.get("q", "").strip()
    results = []

    if query:
        results = Article.objects.filter(
            status=Article.STATUS_PUBLISHED,
        ).filter(
            Q(title__icontains=query) |
            Q(subtitle__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).select_related(
            "author__user", "category"
        ).prefetch_related("tags").distinct().order_by("-published_at")

    # AJAX (live-search) uchun JSON javob
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        data = [
            {
                "title":          a.title,
                "subtitle":       a.subtitle,
                "url":            a.get_absolute_url(),
                "category":       a.category.name if a.category else "",
                "category_color": a.category.color if a.category else "",
                "read_time":      a.read_time,
                "image_url":      a.image.url if a.image else "",
            }
            for a in results[:8]
        ]
        return JsonResponse({"results": data, "count": len(data)})

    paginator     = Paginator(results, per_page=6)
    articles_page = paginator.get_page(request.GET.get("page", 1))

    ctx = _base_context()
    ctx.update({
        "query":         query,
        "articles_page": articles_page,
        "result_count":  paginator.count,
        "tags":          Tag.objects.all(),
    })
    return render(request, "blog/search.html", ctx)


@require_POST
def newsletter_subscribe(request):
    email = request.POST.get("email", "").strip()
    if not email or "@" not in email:
        return JsonResponse({"ok": False, "message": "Email noto'g'ri."}, status=400)

    # Haqiqiy loyihada bu yerda Email modeliga saqlang
    print(f"[Newsletter] Yangi obunachi: {email}")
    return JsonResponse({
        "ok":      True,
        "message": f"{email} manzili qo'shildi! Rahmat 🎉",
    })


@require_POST
def vote_article(request, article_id):
    article   = get_object_or_404(Article, id=article_id)
    vote_type = request.POST.get('vote_type')
    ip        = _get_client_ip(request)

    if vote_type not in ['like', 'dislike']:
        return JsonResponse({'ok': False, 'error': "Noto'g'ri tur"}, status=400)

    vote, created = Vote.objects.get_or_create(
        article=article,
        ip_address=ip,
        defaults={'vote_type': vote_type}
    )

    current_vote = None  # Ovoz berib bo'lgandan keyingi holat

    if not created:
        if vote.vote_type == vote_type:
            # Ikkinchi marta bossa — ovozni bekor qiladi
            vote.delete()
            current_vote = None
        else:
            # Boshqa tugmaga o'tkazadi
            vote.vote_type = vote_type
            vote.save()
            current_vote = vote_type
    else:
        current_vote = vote_type

    likes    = article.votes.filter(vote_type='like').count()
    dislikes = article.votes.filter(vote_type='dislike').count()

    return JsonResponse({
        'ok':            True,
        'likes_count':   likes,
        'dislikes_count': dislikes,
        'user_vote':     current_vote,   # frontend .active klassi uchun
    })