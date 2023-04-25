from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import reverse
from django.core.cache import cache
from profanity.validators import validate_is_profane

Tanks = 'Tanks'
Heals = 'Heals'
Dd = 'Dd'
Tradesman = 'Tradesman'
Guildmaster = 'Guildmaster'
Questgiver = 'Questgiver'
Smith = 'Smith'
Skinner = 'Skinner'
Potionmaster = 'Potionmaster'
Spellmaster = 'Spellmaster'
CATEGORY_CHOICES = (
    (Tanks, 'Танки'),
    (Heals, 'Хилы'),
    (Dd, 'ДД'),
    (Tradesman, 'Торговцы'),
    (Guildmaster, 'Гилдмастеры'),
    (Questgiver, 'Квестгиверы'),
    (Smith, 'Кузнецы'),
    (Skinner, 'Кожевники'),
    (Potionmaster, 'Зельевары'),
    (Spellmaster, 'Мастера заклинаний'),
)
catdictionary = {k: v for (k, v) in CATEGORY_CHOICES}


class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.authorUser}'

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f'{self.name}'

    def namerus(self):
        return f'{catdictionary[self.name]}'


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    categoryType = models.CharField(max_length=16, choices=CATEGORY_CHOICES, default=Tanks)
    #postCategory = models.ManyToManyField(Category)
    dateCreation = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=128, validators=[validate_is_profane])
    text = models.TextField(validators=[validate_is_profane])

    def catname(self):
        return catdictionary[self.categoryType]

    def catnames(self):
        catnames = list(catdictionary.values())
        return catnames

    def datethis(self):
        return self.dateCreation.strftime("%Y-%m-%d %X")

    def datedmy(self):
        return self.dateCreation.strftime("%d-%m-%Y")

    def comm_count(self):
        comm_count = Comment.objects.filter(commentPost=self.id).count()
        return comm_count

    def get_absolute_url(self):
        return reverse('post_detail_show', kwargs={'id':self.id})

    def preview(self):
        return self.text[0:19] + '...'
        #return '{} ... {}'.format(self.text[0:123], str(self.rating))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'post-{self.pk}')  # затем удаляем его из кэша, чтобы сбросить его

    def __str__(self):
        return f'{self.title} :: {self.text[:20]}'


class Comment(models.Model):
    commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(validators=[validate_is_profane])
    dateCreation = models.DateTimeField(auto_now_add=True)

    def datethis(self):
        return self.dateCreation.strftime("%Y-%m-%d %X")

    def __str__(self):
        return f'{self.text[:30]}'

