from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse

class Category(models.Model):
    name  = models.CharField(max_length=100, verbose_name="Nomi")
    slug  = models.SlugField(max_length=100, unique=True, blank=True)
    color = models.CharField(
        max_length=20,
        default="tag-django",
        verbose_name="CSS klassi",
        help_text="tag-django | tag-python | tag-drf | tag-pg | tag-docker",
    )

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:category", kwargs={"slug": self.slug})


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Teg")
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    class Meta:
        verbose_name = "Teg"
        verbose_name_plural = "Teglar"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Author(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name="author_profile")
    bio        = models.TextField(blank=True, verbose_name="Haqida")
    avatar_letter = models.CharField(max_length=1, blank=True, verbose_name="Avatar harfi", help_text="Frontendda doirachaga chiqadigan harf (avtomatik to'ldiriladi)",)
    role       = models.CharField(max_length=100, blank=True, verbose_name="Lavozim", help_text="Masalan: Senior Django Developer")
    instagram_url   = models.URLField(blank=True, verbose_name="Instagram")
    telegram_url = models.URLField(blank=True, verbose_name="Telegram")

    class Meta:
        verbose_name = "Muallif"
        verbose_name_plural = "Mualliflar"

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    def save(self, *args, **kwargs):
        if not self.avatar_letter:
            name = self.user.get_full_name() or self.user.username
            self.avatar_letter = name[0].upper()
        super().save(*args, **kwargs)


class Article(models.Model):

    STATUS_DRAFT     = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT,     "Qoralama"),
        (STATUS_PUBLISHED, "Nashr etilgan"),
    ]

    title       = models.CharField(max_length=250, verbose_name="Sarlavha")
    slug        = models.SlugField(max_length=250, unique=True, blank=True)
    subtitle    = models.CharField(max_length=350, blank=True, verbose_name="Qisqa tavsif")
    # YANGI MAYDON QO'SHILDI
    image       = models.ImageField(upload_to='articles/%Y/%m/%d/', blank=True, null=True, verbose_name="Maqola rasmi")
    content     = models.TextField(verbose_name="Mazmun (HTML yoki Markdown)")
    code_snippet = models.TextField(blank=True, verbose_name="Kod snippet (karta uchun)", help_text="Blog ro'yxatidagi kartada chiqadigan qisqa kod namunasi",)
    code_snippet_lang = models.CharField(max_length=30, default="python", blank=True,verbose_name="Kod tili",)
    author   = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name="articles", verbose_name="Muallif",)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="articles", verbose_name="Kategoriya")
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles", verbose_name="Teglar")
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT, verbose_name="Holati")
    is_featured  = models.BooleanField(default=False, verbose_name="Tanlangan (featured)?")
    read_time    = models.PositiveSmallIntegerField(default=5, verbose_name="O'qish vaqti (daqiqa)", help_text="Avtomatik hisoblanmaydi — qo'lda kiriting")
    views_count  = models.PositiveIntegerField(default=0, verbose_name="Ko'rishlar soni", editable=False)
    created_at   = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan")
    updated_at   = models.DateTimeField(auto_now=True, verbose_name="Yangilangan")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Nashr sanasi")

    class Meta:
        verbose_name = "Maqola"
        verbose_name_plural = "Maqolalar"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["status", "-published_at"]),
            models.Index(fields=["category", "status"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:article_detail", kwargs={"slug": self.slug})

    @property
    def is_published(self):
        return self.status == self.STATUS_PUBLISHED

    def increment_views(self):
        Article.objects.filter(pk=self.pk).update(
            views_count=models.F("views_count") + 1
        )


class Vote(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    VOTE_CHOICES = [(LIKE, 'Like'), (DISLIKE, 'Dislike')]

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="votes")
    ip_address = models.GenericIPAddressField()
    vote_type = models.CharField(max_length=10, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('article', 'ip_address')