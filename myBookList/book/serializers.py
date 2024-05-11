from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'creator', 'publicationYear', 'isbn' ]  # include other fields as needed
        read_only_fields = ['creator']
