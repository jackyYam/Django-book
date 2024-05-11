from rest_framework.decorators import api_view
from rest_framework.response import Response
# This is the model that we will use
from .models import Book
# This is the serializer that we will use
from .serializers import BookSerializer

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from django.contrib.auth.models import User

from rest_framework.views import APIView
class IsCreator(permissions.BasePermission):
    """
    Custom permission to only allow creators of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Write permissions are only allowed to the creator of the book.
        print(obj.creator, request.user)
        return obj.creator == request.user
    
class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(creator=self.request.user)

    
class BookRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    partial = True
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method == 'PUT' or self.request.method == 'DELETE' or self.request.method == 'PATCH':
            return [IsAuthenticated(), IsCreator()]
        return super().get_permissions()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK, data={"message": "Book deleted successfully."})
    

class UserFavouriteBooksView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return self.request.user.favourite_books.all()
    
class FavouriteBook(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)
            request.user.favourite_books.add(book)
            return Response({"sueccess": True}, status=status.HTTP_200_OK)
        except Book.DoesNotExist:
            return Response({"sueccess": False, "error": "The book Requested does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"sueccess": False}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)
            request.user.favourite_books.remove(book)
            return Response({"sueccess": True}, status=status.HTTP_200_OK)
        except Book.DoesNotExist:
            return Response({"sueccess": False, "error": "The book Requested does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"sueccess": False}, status=status.HTTP_400_BAD_REQUEST)
