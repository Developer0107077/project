# 🐍 Python.dev — Django Blog Loyihasi

> Backend blog platformasi — Django yordamida qurilgan. Maqolalar, kategoriyalar, teglar, like/dislike tizimi va live qidiruv bilan to'liq jihozlangan.

---

## 📁 Loyiha Strukturasi

```
project-main/
├── blog/                  ← Asosiy dastur (app)
│   ├── models.py          ← Ma'lumotlar bazasi modellari
│   ├── views.py           ← Sahifalar logikasi
│   ├── urls.py            ← Blog URL yo'llari
│   └── admin.py           ← Admin panel sozlamalari
├── config/                ← Loyiha sozlamalari
│   ├── settings.py        ← Asosiy konfiguratsiya
│   └── urls.py            ← Bosh URL marshrutlash
├── templates/blog/        ← HTML shablonlar (frontend)
│   ├── index.html         ← Bosh sahifa
│   ├── article_detail.html← Maqola sahifasi
│   ├── category.html      ← Kategoriya sahifasi
│   └── search.html        ← Qidiruv sahifasi
├── static/
│   ├── style.css          ← Barcha uslublar (CSS)
│   └── main.js            ← Interaktivlik (JavaScript)
├── media/                 ← Yuklanган rasmlar saqlanadi
├── manage.py              ← Django boshqaruv fayli
└── requirements.txt       ← Kerakli kutubxonalar
```

---

## ⚙️ O'rnatish va Ishga Tushurish

```bash
# 1. Virtual muhit yarating
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Kutubxonalarni o'rnating
pip install -r requirements.txt

# 3. Ma'lumotlar bazasini yarating
python manage.py migrate

# 4. Admin foydalanuvchi yarating
python manage.py createsuperuser

# 5. Serverni ishga tushiring
python manage.py runserver
```

Keyin brauzerda oching: **http://127.0.0.1:8000**  
Admin panel: **http://127.0.0.1:8000/admin**

---

## 🗄️ Backend — Models (models.py)

Ma'lumotlar bazasidagi jadvallarni belgilaydi. Har bir `class` — bitta jadval.

### `Category` — Kategoriya
```python
class Category(models.Model):
    name  = models.CharField(max_length=100)   # Kategoriya nomi 
    slug  = models.SlugField(unique=True)      # URL uchun qisqa nom
    color = models.CharField(max_length=20)    # CSS klassi
```
**Vazifasi:** Maqolalarni guruhlaydi. Har bir maqola bitta kategoriyaga tegishli.  
**`save()` metodi:** Agar `slug` bo'sh bo'lsa, nomdan avtomatik hosil qiladi

---

### `Tag` — Teg
```python
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Teg nomi
    slug = models.SlugField(unique=True)                  # URL uchun
```
**Vazifasi:** Maqolaga bir nechta kalit so'z qo'shish imkonini beradi. Bitta maqolada ko'p teg bo'lishi mumkin.

---

### `Author` — Muallif
```python
class Author(models.Model):
    user          = models.OneToOneField(User, ...)   # Django foydalanuvchisi bilan bog'liq
    bio           = models.TextField()                # Muallif haqida matn
    avatar_letter = models.CharField(max_length=1)    # Avatar harfi 
    role          = models.CharField(max_length=100)  # Lavozim
    instagram_url = models.URLField()                 # Instagram havolasi
    telegram_url  = models.URLField()                 # Telegram havolasi
```
**Vazifasi:** Django'ning standart `User` modelini kengaytiradi — har bir foydalanuvchiga blog profili qo'shadi.  
**`save()` metodi:** `avatar_letter` bo'sh bo'lsa, foydalanuvchi ismining birinchi harfini avtomatik oladi.

---

### `Article` — Maqola (asosiy model)
```python
class Article(models.Model):
    title        = models.CharField(max_length=250)                     # Sarlavha
    slug         = models.SlugField(unique=True)                        # URL
    subtitle     = models.CharField(max_length=350)                     # Qisqa tavsif
    image        = models.ImageField(upload_to='articles/%Y/%m/%d/')    # Rasm
    content      = models.TextField()                                   # Asosiy mazmun 
code_snippet = models.TextField()                                   # Kartada ko'rinadigan kod namunasi
    author       = models.ForeignKey(Author, ...)                       # Muallif 
    category     = models.ForeignKey(Category, ...)                     # Kategoriya 
    tags         = models.ManyToManyField(Tag, ...)                     # Teglar 
    status       = models.CharField(choices=STATUS_CHOICES)             # "draft" yoki "published"
    is_featured  = models.BooleanField(default=False)                   # Tanlangan maqolami?
read_time    = models.PositiveSmallIntegerField()                       # O'qish vaqti 
    views_count  = models.PositiveIntegerField(default=0)               # Ko'rishlar soni
    published_at = models.DateTimeField()                               # Nashr sanasi
```

**Muhim metodlar:**
- `increment_views()` — Ko'rishlar sonini +1 qiladi 
- `is_published` property — Maqola nashr etilganmi?
- `get_absolute_url()` — Maqola havolasini qaytaradi

**Indekslar (tezlashtirish uchun):**
```python
indexes = [
    models.Index(fields=["slug"]),                     # slug bo'yicha tez qidirish
    models.Index(fields=["status", "-published_at"]),  # Nashr etilganlarni saralash
    models.Index(fields=["category", "status"]),       # Kategoriya filtri
]
```

---

### `Vote` — Ovoz (Like/Dislike)
```python
class Vote(models.Model):
    article    = models.ForeignKey(Article, ...)                            # Qaysi maqola
ip_address = models.GenericIPAddressField()                                 # Foydalanuvchi IP manzili
    vote_type  = models.CharField(choices=[('like','Like'), ('dislike','Dislike')])
    
    class Meta:
        unique_together = ('article', 'ip_address')    # Bir IP — bitta ovoz
```
**Vazifasi:** Har bir foydalanuvchi  bitta maqolaga faqat bir marta ovoz bera oladi.

---

## 🔗 Backend — URL Marshrutlash (urls.py)

### `config/urls.py` — Bosh URL
```python
urlpatterns = [
    path("admin/", admin.site.urls),           # Admin panel
    path("", include("blog.urls")),            # Barcha blog URL'lari
]
```
**Vazifasi:** Kirgan so'rovni to'g'ri joyga yo'naltiradi. 

### `blog/urls.py` — Blog URL'lari
| URL | View | Nomi |
|-----|------|------|
| `/` | `index` | `blog:index` |
| `/article/<slug>/` | `article_detail` | `blog:article_detail` |
| `/category/<slug>/` | `category_articles` | `blog:category` |
| `/tag/<slug>/` | `tag_articles` | `blog:tag` |
| `/search/` | `search` | `blog:search` |
| `/newsletter/subscribe/` | `newsletter_subscribe` | `blog:newsletter_subscribe` |
| `/vote/<id>/` | `vote_article` | `blog:vote_article` |

---

## 👁️ Backend — Views (views.py)


### `_base_context()` — Yordamchi funksiya
```python
def _base_context():
    return {
        "categories": Category.objects.annotate(article_count=Count(...))
    }
```
**Vazifasi:** Barcha sahifalar uchun umumiy ma'lumot — kategoriyalar ro'yxati. Har safar qayta yozmaslik uchun alohida ajratilgan.

---

### `index(request)` — Bosh sahifa
**Nima qiladi:**
1. Nashr etilgan barcha maqolalarni oladi (`status=published`)
2. Filtr qo'llanadi: kategoriya, teg, yoki qidiruv so'zi bo'yicha
3. `is_featured=True` maqolalarni alohida ajratadi (tanlangan maqolalar)
4. Paginatsiya — sahifada 6 ta maqola ko'rsatadi
5. Hamma narsani shablon orqali HTML sifatida qaytaradi

```python
published = Article.objects.filter(status=Article.STATUS_PUBLISHED)\
    .annotate(
        annotated_likes=Count('votes', filter=Q(votes__vote_type='like')),
        annotated_dislikes=Count('votes', filter=Q(votes__vote_type='dislike'))
    )
```

---

### `article_detail(request, slug)` — Maqola sahifasi
**Nima qiladi:**
1. `slug` bo'yicha maqolani topadi (topilmasa 404 xato)
2. **Session orqali ko'rishlar sonini oshiradi** — bir foydalanuvchi bir marta sanash uchun:
   ```python
   session_key = f"viewed_article_{article.pk}"
   if not request.session.get(session_key):
       article.increment_views()
       request.session[session_key] = True
   ```
3. Like/Dislike sonlarini hisoblaydi
4. Foydalanuvchi IP'si bo'yicha uning ovozini aniqlaydi
5. O'xshash maqolalarni (shu kategoriyadan) topadi

---

### `search(request)` — Qidiruv
**Nima qiladi:**  
`Q` obyekti yordamida bir vaqtda sarlavha, tavsif, mazmun va teglarda qidiradi:
```python
Q(title__icontains=query) |
Q(subtitle__icontains=query) |
Q(content__icontains=query) |
Q(tags__name__icontains=query)
```

**AJAX (live-search) qo'llab-quvvatlaydi:**  
Agar so'rov `XMLHttpRequest` bo'lsa, HTML o'rniga JSON qaytaradi:
```json
{"results": [...], "count": 5}
```

---

### `vote_article(request, article_id)` — Like/Dislike API
**Faqat POST so'rovni qabul qiladi** (`@require_POST` dekorator).

**Mantiq:**
```
Ovoz berdi?
├── Yo'q → yangi ovoz yaratiladi
└── Ha →
    ├── Xuddi o'sha tugma → ovoz bekor qilinadi (toggle)
    └── Boshqa tugma → ovoz o'zgartiriladi
```

**JSON javob qaytaradi:**
```json
{"ok": true, "likes_count": 12, "dislikes_count": 3, "user_vote": "like"}
```

---

### `newsletter_subscribe(request)` — Obuna
**Nima qiladi:** Email manzilini tekshiradi (`@` belgisi bormi?), keyin "saqlaydi" (hozircha `print` bilan, real loyihada modelga yoziladi).

---

## 🎨 Frontend — HTML Shablonlar

### `index.html` — Bosh sahifa
**Tarkibi:**
- **HERO** bo'limi — terminal animatsiyasi bilan xush kelibsiz ekrani
- **Tanlangan maqolalar** (`is_featured=True`) — katta kartalar
- **Barcha maqolalar** — filtr tugmalari va karta ro'yxati
- **Kategoriyalar** bo'limi
- **Muallif haqida** bo'limi
- **Newsletter** (obuna) formasi

**Django template teglari:**
```html
{% for article in articles_page %}    ← maqolalar ro'yxatini chiqaradi
{% if article.image %}                ← rasm bor-yo'qligini tekshiradi
{{ article.title }}                   ← qiymatni HTML ga chiqaradi
{% url 'blog:article_detail' article.slug %}  ← havola yaratadi
```

---

### `article_detail.html` — Maqola sahifasi
**Tarkibi:**
- **Sarlavha + rasm** — yonma-yon joylashtirilgan (flex layout)
- **Maqola matni** — ichida scroll bor (max-height: 500px)
- **Kod snippet** — accordion (yashirin/ko'rinadigan)
- **Like/Dislike tugmalari** — AJAX bilan ishlaydi
- **O'xshash maqolalar** — shu kategoriyadan yana 3 ta

---

## 🛡️ Admin Panel (admin.py)

Django admin panelini sozlaydi — ma'lumotlarni qulay boshqarish uchun.

### `ArticleAdmin`
- **Ro'yxatda ko'rsatish:** sarlavha, muallif, kategoriya, holat, ko'rishlar soni
- **Holat badge:** "Nashr" (yashil) yoki "Qoralama" (kulrang) rangli ko'rinish
- **Rasm preview:** Admindan maqolaning rasmini oldindan ko'rish
- **Tezkor amallar:**
  - `make_published` — bir nechta maqolani bir vaqtda nashr etish
  - `make_draft` — qoralamaga qaytarish

---

## 🔧 Konfiguratsiya (settings.py)

| Sozlama | Qiymati | Tavsifi |
|---------|---------|---------|
| `DEBUG` | `True` | Ishlab chiqish rejimi |
| `LANGUAGE_CODE` | `"uz"` | O'zbek tili |
| `TIME_ZONE` | `"Asia/Tashkent"` | Toshkent vaqti |
| `DATABASES` | SQLite | Mahalliy fayl bazasi |
| `MEDIA_ROOT` | `media/` | Rasm fayllari papkasi |
| `SESSION_COOKIE_AGE` | 30 kun | Sessiya muddati |

**Jazzmin** — admin panelni go'zal qiluvchi kutubxona (`JAZZMIN_SETTINGS` orqali sozlanadi).

---

## 📦 Kutubxonalar (requirements.txt)

| Kutubxona | Versiya | Maqsadi |
|-----------|---------|---------|
| `Django` | 6.0.6 | Asosiy framework |
| `django-jazzmin` | 3.0.4 | Chiroyli admin panel |
| `Pillow` | 12.2.0 | Rasm yuklash va qayta ishlash |
| `sqlparse` | 0.5.5 | SQL so'rovlarini formatlash |

---

## 🌐 URL → Sahifa xaritasi

```
http://localhost:8000/                          → Bosh sahifa (maqolalar ro'yxati)
http://localhost:8000/article/django-orm-guide/ → Maqola sahifasi
http://localhost:8000/category/django/          → Kategoriya sahifasi
http://localhost:8000/tag/postgresql/           → Teg sahifasi
http://localhost:8000/search/?q=django          → Qidiruv natijalari
http://localhost:8000/admin/                    → Admin panel
```

---

## 🔄 Ma'lumot Oqimi (Request → Response)

```
Foydalanuvchi http://localhost:8000/ ochadi
        ↓
Django config/urls.py ga qaraydi
        ↓
blog/urls.py → index view chaqiriladi
        ↓
views.py::index() → ma'lumotlar bazasidan maqolalarni oladi
        ↓
templates/blog/index.html shablonga ma'lumotlar uzatiladi
        ↓
HTML sahifa foydalanuvchiga qaytariladi
        ↓
main.js ishlaydi — interaktivlik (filtr, AJAX, menyu)
```

---
