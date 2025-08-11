from django.db import models
from accounts.models import User

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    verified = models.BooleanField(default=True)
    pricing_plan = models.CharField(max_length=100, default='Free', null=True, blank=True)
    email = models.CharField(max_length=1000,  null=True, blank=True)
    user_name = models.CharField(max_length=1000, null=True, blank=True)
    comments = models.IntegerField(default=0, null=True, blank=True)
    reviews = models.IntegerField(default=0, null=True, blank=True)
    creation_date = models.DateField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.user)

class Category(models.Model):
    cat = models.CharField(max_length=1000)

    def __str__(self):
        return self.cat

class rate(models.Model):
    rate_value = models.CharField(max_length=1000)

class year(models.Model):
    year_value = models.CharField(max_length=200)

    def __str__(self):
        return self.year_value

class movie(models.Model):
    name = models.CharField(max_length=20000)
    info = models.TextField()
    video = models.CharField(max_length=10000, null=True, blank=True)

    sub_title_lang = models.CharField(max_length=225, null=True, blank=True)
    srclang = models.CharField(max_length=225, blank=True, null=True)
    sub_title_file = models.CharField(max_length=1000, null=True, blank=True)

    sub_title_lang2 = models.CharField(max_length=225, null=True, blank=True)
    srclang2 = models.CharField(max_length=225, blank=True, null=True)
    sub_title_file2 = models.CharField(max_length=1000, null=True, blank=True)

    thumbnail = models.FileField(upload_to='thumb/')
    age = models.CharField(default=13, max_length=20)
    cat = models.CharField(default='cartoon', max_length=200)
    premier = models.BooleanField(default=False)
    genre1 = models.ForeignKey(Category, related_name='category1', on_delete=models.CASCADE, null=True, blank=True)
    genre2 = models.ForeignKey(Category, related_name='category2', on_delete=models.CASCADE, null=True, blank=True)
    rating = models.CharField(max_length=100)
    year = models.CharField(max_length=100)
    year_range = models.CharField(max_length=200, null=True, blank=True)
    new = models.BooleanField(default=False)
    duration = models.CharField(max_length=100)
    country = models.CharField(max_length=200)
    draft = models.BooleanField(default=False)
    date_added = models.DateField(auto_now_add=True, null=True, blank=True)
    clicks = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return self.name