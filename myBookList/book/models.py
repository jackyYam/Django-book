from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
# Create your models here.

isbn_validator = RegexValidator(r"^(?=(?:\D*\d){10}(?:(?:\D*\d){3})?$)[\d-]+$", "Invalid ISBN. ISBN must be 10 or 13 digits long.")
class Book(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    publicationYear = models.IntegerField()
    isbn = models.CharField(validators=[isbn_validator])
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    favourites = models.ManyToManyField(User, related_name='favourite_books', blank=True)
    def __str__(self) -> str:
        return f"{self.title} by {self.author} - {self.publicationYear}"
    class Meta:
        ordering = ['id']  # or any other field
