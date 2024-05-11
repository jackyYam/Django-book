from django.urls import path 
from .views import BookListCreateView, BookRetrieveUpdateDestroyView, UserFavouriteBooksView, FavouriteBook

urlpatterns = [
    path('books/', BookListCreateView.as_view(), name="get-books-list"),
    path('books/<int:pk>/', BookRetrieveUpdateDestroyView.as_view(), name="get-update-delete-book"),
    path('favourites/', UserFavouriteBooksView.as_view(), name="get-favourite-books"),
    path('favourites/<int:book_id>/', FavouriteBook.as_view(), name="favourite-book"),
]
