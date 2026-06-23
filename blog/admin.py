from django.contrib import admin
from django.utils.html import format_html
from .models import Article, Category, Tag, Author, Vote



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ("name", "slug", "color", "article_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def article_count(self, obj):
        return obj.articles.filter(status=Article.STATUS_PUBLISHED).count()
    article_count.short_description = "Nashr etilgan maqolalar"



@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)



@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display  = ("__str__", "user", "role", "avatar_letter")
    search_fields = ("user__username", "user__first_name", "user__last_name")
    raw_id_fields = ("user",)



@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display   = (
        "title", "author", "category",
        "status_badge", "is_featured",
        "views_count", "published_at",
    )
    list_filter    = ("status", "is_featured", "category", "tags")
    search_fields  = ("title", "subtitle", "content")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal   = ("tags",)
    readonly_fields     = ("views_count", "created_at", "updated_at", "image_preview")
    date_hierarchy = "published_at"

    fieldsets = (
        ("Asosiy", {
            "fields": ("title", "slug", "subtitle", "image", "image_preview", "author", "category", "tags"),
        }),
        ("Kontent", {
            "fields": ("content", "code_snippet", "code_snippet_lang"),
        }),
        ("Nashr sozlamalari", {
            "fields": ("status", "is_featured", "read_time", "published_at"),
        }),
        ("Statistika", {
            "fields": ("views_count", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def status_badge(self, obj):
        color = "#3FB950" if obj.is_published else "#8B949E"
        label = "Nashr" if obj.is_published else "Qoralama"
        return format_html(
            '<span style="color:{};font-weight:600">{}</span>', color, label
        )
    status_badge.short_description = "Holat"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:180px;border-radius:6px;border:1px solid #30363d;" />',
                obj.image.url,
            )
        return "Rasm yo'q"
    image_preview.short_description = "Rasm ko'rinishi"

    actions = ["make_published", "make_draft"]

    @admin.action(description="Tanlanganllarni nashr etish")
    def make_published(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status=Article.STATUS_PUBLISHED,
            published_at=timezone.now(),
        )
        self.message_user(request, f"{updated} ta maqola nashr etildi.")

    @admin.action(description="Tanlanganllarni qoralamaga qaytarish")
    def make_draft(self, request, queryset):
        updated = queryset.update(status=Article.STATUS_DRAFT)
        self.message_user(request, f"{updated} ta maqola qoralamaga qaytarildi.")


admin.site.register(Vote)