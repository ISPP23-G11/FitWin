import django_filters
from models import Announcement, Trainer, Category
from django import forms


def all_categories(request):
    if request is None:
        return Category.objects.none()
    categories = Category.objects.all().distinct('name')
    return categories

class AnnouncementFilter(django_filters.FilterSet):

    title = django_filters.CharFilter(field_name='title' ,lookup_expr='icontains')
    description = django_filters.CharFilter(field_name='description' ,lookup_expr='icontains')
    place = django_filters.CharFilter(field_name='place' ,lookup_expr='icontains')
    price = django_filters.NumberFilter()
    price__gt = django_filters.NumberFilter(field_name='price', lookup_expr='gt')
    price__lt = django_filters.NumberFilter(field_name='price', lookup_expr='lt')
    capacity = django_filters.NumberFilter()
    capacity__gt = django_filters.NumberFilter(field_name='capacity', lookup_expr='gt')
    capacity__lt = django_filters.NumberFilter(field_name='capacity', lookup_expr='lt')
    start_date = django_filters.DateFilter(field_name='start_date')
    start_date__gt = django_filters.DateFilter(field_name='start_date', lookup_expr='date__gt')
    finish_date = django_filters.DateFilter(field_name='finish_date')
    finish_date__lt = django_filters.DateFilter(field_name='finish_date', lookup_expr='date__lt')
    categories__name = django_filters.ModelMultipleChoiceField(all_categories,forms.CheckboxSelectMultiple())

    class Meta:
        model = Announcement
        fields = ['title','description','place','price','capacity','start_date','finish_date','categories']

class TrainerFilter(django_filters.FilterSet):

    class Meta:
        model = Trainer


