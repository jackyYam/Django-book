from rest_framework.decorators import api_view
from rest_framework.response import Response
# This is the model that we will use
from .models import Book
# This is the serializer that we will use
from .serializers import BookSerializer

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BookRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    partial = True
    lookup_field = 'pk'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK, data={"message": "Book deleted successfully."})
    
