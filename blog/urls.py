from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.index, name="index"),
    path("article/<slug:slug>/", views.article_detail, name="article_detail"),
    path("category/<slug:slug>/", views.category_articles, name="category"),
    path("tag/<slug:slug>/", views.tag_articles, name="tag"),
    path("search/", views.search, name="search"),
    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),
    path('vote/<int:article_id>/', views.vote_article, name='vote_article'),
    
]