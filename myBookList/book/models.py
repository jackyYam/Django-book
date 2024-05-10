from django.db import models
from django.core.validators import RegexValidator
# Create your models here.

isbn_validator = RegexValidator(r"^(?=(?:\D*\d){10}(?:(?:\D*\d){3})?$)[\d-]+$", "Your string should contain letter A in it.")
class Book(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    publicationYear = models.IntegerField()
    isbn = models.CharField(validators=[isbn_validator])

    def __str__(self) -> str:
        return f"{self.title} by {self.author} - {self.publicationYear}"
    
