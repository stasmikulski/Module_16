from django_filters import FilterSet, DateTimeFilter, ModelChoiceFilter
from django.forms import DateTimeInput
from .models import Post, Author, Category

class PostFilter(FilterSet):
    added_after = DateTimeFilter(
        field_name='dateCreation',
        lookup_expr='gt',
        widget=DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'},
        ),
    )
    author = ModelChoiceFilter(
        queryset = Author.objects.all(),
        label = 'Authors',
        empty_label = 'All'
    )
    categoryType = ModelChoiceFilter(
        queryset = Category.objects.all(),
        label = 'Category',
        empty_label = 'Any'
    )
    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],
            #'categoryType': ['exact'],
            #'author': ['exact'],
        }