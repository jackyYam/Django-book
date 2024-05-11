from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from .models import Book
from .serializers import BookSerializer

class BookListCreateViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        Book.objects.create(title='Test Book', author='Test Author', creator=self.user, publicationYear=2022,
            isbn='1234567890')
        Book.objects.create(title='Test Book 2', author='Test Author 2', creator=self.user, publicationYear=2022, isbn='1234567890')

    def test_get_book_list(self):
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        self.assertEqual(response.data["results"], serializer.data)

    def test_create_book(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'publicationYear': 2022,
            'isbn': '1234567890',
        }
        response = self.client.post('/api/books/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)
        book = Book.objects.last()
        self.assertEqual(book.title, data['title'])
        self.assertEqual(book.author, data['author'])
        self.assertEqual(book.creator, self.user)

    def test_create_book_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'description': 'Test Description'
        }
        response = self.client.post('/api/books/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Book.objects.count(), 2)

class BookRetrieveUpdateDestroyViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.book = Book.objects.create(title='Test Book', author='Test Author', creator=self.user, publicationYear=2022,
            isbn='1234567890')
        self.not_owner = User.objects.create_user(username='notowner', password='testpassword')

    def test_get_book(self):
        response = self.client.get(f'/api/books/{self.book.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book = Book.objects.get(pk=self.book.pk)
        serializer = BookSerializer(book)
        self.assertEqual(response.data, serializer.data)

    def test_update_book(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Updated Book',
            'author': 'Updated Author',
            'publicationYear': 2023,
            'isbn': '0987654321',
        }
        response = self.client.put(f'/api/books/{self.book.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book = Book.objects.get(pk=self.book.pk)
        self.assertEqual(book.title, data['title'])
        self.assertEqual(book.author, data['author'])
        self.assertEqual(book.publicationYear, data['publicationYear'])
        self.assertEqual(book.isbn, data['isbn'])

    def test_update_book_unauthenticated(self):
        data = {
            'title': 'Updated Book',
        }
        response = self.client.put(f'/api/books/{self.book.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        book = Book.objects.get(pk=self.book.pk)
        self.assertNotEqual(book.title, data['title'])
    
    def test_update_book_not_owner(self):
        self.client.force_authenticate(user=self.not_owner)
        data = {
            'title': 'Updated Book',
        }
        response = self.client.put(f'/api/books/{self.book.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        book = Book.objects.get(pk=self.book.pk)
        self.assertNotEqual(book.title, data['title'])

    def test_partial_update_book(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Updated Book Title 22',
        }
        response = self.client.patch(f'/api/books/{self.book.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book = Book.objects.get(pk=self.book.pk)
        self.assertEqual(book.title, data['title'])
    
    def test_partial_update_book_unauthenticated(self):
        data = {
            'title': 'Updated Book Title 22',
        }
        response = self.client.patch(f'/api/books/{self.book.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        book = Book.objects.get(pk=self.book.pk)
        self.assertNotEqual(book.title, data['title'])
    
    def test_partial_update_book_not_owner(self):
        self.client.force_authenticate(user=self.not_owner)
        data = {
            'title': 'Updated Book Title 22',
        }
        response = self.client.patch(f'/api/books/{self.book.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        book = Book.objects.get(pk=self.book.pk)
        self.assertNotEqual(book.title, data['title'])

    def test_delete_book(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/books/{self.book.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())
        self.assertEqual(response.data, {"message": "Book deleted successfully."})
    
    def test_delete_book_unauthenticated(self):
        response = self.client.delete(f'/api/books/{self.book.pk}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())
    
    def test_delete_book_not_owner(self):
        self.client.force_authenticate(user=self.not_owner)
        response = self.client.delete(f'/api/books/{self.book.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

class UserFavouriteBooksViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.book1 = Book.objects.create(title='Test Book 1', author='Test Author 1', creator=self.user, publicationYear=2022,
            isbn='1234567890')
        self.book2 = Book.objects.create(title='Test Book 2', author='Test Author 2', creator=self.user, publicationYear=2022,
            isbn='1234567890')
        self.book3 = Book.objects.create(title='Test Book 3', author='Test Author 3', creator=self.user, publicationYear=2022,
            isbn='1234567890')
        self.user.favourite_books.add(self.book1, self.book2)

    def test_get_user_favourite_books(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/favourite-books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        favourite_books = self.user.favourite_books.all()
        serializer = BookSerializer(favourite_books, many=True)
        self.assertEqual(response.data["results"], serializer.data)

    def test_get_user_favourite_books_unauthenticated(self):
        response = self.client.get('/api/favourite-books/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from .models import Book
from .serializers import BookSerializer

class BookListCreateViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        Book.objects.create(title='Test Book', author='Test Author', creator=self.user, publicationYear=2022,
            isbn='1234567890')
        Book.objects.create(title='Test Book 2', author='Test Author 2', creator=self.user, publicationYear=2022, isbn='1234567890')

    def test_get_book_list(self):
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        self.assertEqual(response.data["results"], serializer.data)

    def test_create_book(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'publicationYear': 2022,
            'isbn': '1234567890',
        }
        response = self.client.post('/api/books/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)
        book = Book.objects.last()
        self.assertEqual(book.title, data['title'])
        self.assertEqual(book.author, data['author'])
        self.assertEqual(book.creator, self.user)

    def test_create_book_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'description': 'Test Description'
        }
        response = self.client.post('/api/books/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Book.objects.count(), 2)

class BookRetrieveUpdateDestroyViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.book = Book.objects.create(title='Test Book', author='Test Author', creator=self.user, publicationYear=2022,
            isbn='1234567890')
        self.not_owner = User.objects.create_user(username='notowner', password='testpassword')

    def test_get_book(self):
        response = self.client.get(f'/api/books/{self.book.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book = Book.objects.get(pk=self.book.pk)
        serializer = BookSerializer(book)
        self.assertEqual(response.data, serializer.data)

    def test_update_book(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Updated Book',
            'author': 'Updated Author',
            'publicationYear': 2023,
            'isbn': '0987654321',
        }
        response = self.client.put(f'/api/books/{self.book.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book = Book.objects.get(pk=self.book.pk)
        self.assertEqual(book.title, data['title'])
        self.assertEqual(book.author, data['author'])
        self.assertEqual(book.publicationYear, data['publicationYear'])
        self.assertEqual(book.isbn, data['isbn'])

    def test_update_book_unauthenticated(self):
        data = {
            'title': 'Updated Book',
        }
        response = self.client.put(f'/api/books/{self.book.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        book = Book.objects.get(pk=self.book.pk)
        self.assertNotEqual(book.title, data['title'])
    
    def test_update_book_not_owner(self):
        self.client.force_authenticate(user=self.not_owner)
        data = {
            'title': 'Updated Book',
        }
        response = self.client.put(f'/api/books/{self.book.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        book = Book.objects.get(pk=self.book.pk)
        self.assertNotEqual(book.title, data['title'])

    def test_partial_update_book(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Updated Book Title 22',
        }
        response = self.client.patch(f'/api/books/{self.book.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book = Book.objects.get(pk=self.book.pk)
        self.assertEqual(book.title, data['title'])
    
    def test_partial_update_book_unauthenticated(self):
        data = {
            'title': 'Updated Book Title 22',
        }
        response = self.client.patch(f'/api/books/{self.book.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        book = Book.objects.get(pk=self.book.pk)
        self.assertNotEqual(book.title, data['title'])
    
    def test_partial_update_book_not_owner(self):
        self.client.force_authenticate(user=self.not_owner)
        data = {
            'title': 'Updated Book Title 22',
        }
        response = self.client.patch(f'/api/books/{self.book.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        book = Book.objects.get(pk=self.book.pk)
        self.assertNotEqual(book.title, data['title'])

    def test_delete_book(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/books/{self.book.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())
        self.assertEqual(response.data, {"message": "Book deleted successfully."})
    
    def test_delete_book_unauthenticated(self):
        response = self.client.delete(f'/api/books/{self.book.pk}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())
    
    def test_delete_book_not_owner(self):
        self.client.force_authenticate(user=self.not_owner)
        response = self.client.delete(f'/api/books/{self.book.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

class UserFavouriteBooksViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.book1 = Book.objects.create(title='Test Book 1', author='Test Author 1', creator=self.user, publicationYear=2022,
            isbn='1234567890')
        self.book2 = Book.objects.create(title='Test Book 2', author='Test Author 2', creator=self.user, publicationYear=2022,
            isbn='1234567890')
        self.book3 = Book.objects.create(title='Test Book 3', author='Test Author 3', creator=self.user, publicationYear=2022,
            isbn='1234567890')
        self.user.favourite_books.add(self.book1, self.book2)

    def test_get_user_favourite_books(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/favourites/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        favourite_books = self.user.favourite_books.all()
        serializer = BookSerializer(favourite_books, many=True)
        self.assertEqual(response.data["results"], serializer.data)

    def test_get_user_favourite_books_unauthenticated(self):
        response = self.client.get('/api/favourites/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class FavouriteBookTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.book = Book.objects.create(title='Test Book', author='Test Author', creator=self.user, publicationYear=2022,
            isbn='1234567890')

    def test_add_book_to_favourites(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/favourites/{self.book.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.favourite_books.filter(pk=self.book.pk).exists())

    def test_add_book_to_favourites_unauthenticated(self):
        response = self.client.post(f'/api/favourites/{self.book.pk}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(self.user.favourite_books.filter(pk=self.book.pk).exists())

    def test_add_nonexistent_book_to_favourites(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/favourites/999/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.user.favourite_books.filter(pk=999).exists())

    def test_remove_book_from_favourites(self):
        self.client.force_authenticate(user=self.user)
        self.user.favourite_books.add(self.book)
        response = self.client.delete(f'/api/favourites/{self.book.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.user.favourite_books.filter(pk=self.book.pk).exists())

    def test_remove_book_from_favourites_unauthenticated(self):
        self.user.favourite_books.add(self.book)
        response = self.client.delete(f'/api/favourites/{self.book.pk}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(self.user.favourite_books.filter(pk=self.book.pk).exists())

    def test_remove_nonexistent_book_from_favourites(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete('/api/favourites/999/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.user.favourite_books.filter(pk=999).exists())
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Book
from .serializers import BookSerializer

class BookListCreateViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        Book.objects.create(title='Test Book', author='Test Author', creator=self.user, publicationYear=2022,
            isbn='1234567890')
        Book.objects.create(title='Test Book 2', author='Test Author 2', creator=self.user, publicationYear=2022, isbn='1234567890')

    def test_get_book_list(self):
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        self.assertEqual(response.data["results"], serializer.data)

    def test_create_book(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'publicationYear': 2022,
            'isbn': '1234567890',
        }
        response = self.client.post('/api/books/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)
        book = Book.objects.last()
        self.assertEqual(book.title, data['title'])
        self.assertEqual(book.author, data['author'])
        self.assertEqual(book.creator, self.user)

    def test_create_book_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'description': 'Test Description'
        }
        response = self.client.post('/api/books/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Book.objects.count(), 2)

class BookRetrieveUpdateDestroyViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.book = Book.objects.create(title='Test Book', author='Test Author', creator=self.user, publicationYear=2022,
            isbn='1234567890')
        self.not_owner = User.objects.create_user(username='notowner', password='testpassword')

    def test_get_book(self):
        response = self.client.get(f'/api/books/{self.book.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book = Book.objects.get(pk=self.book.pk)
        serializer = BookSerializer(book)
        self.assertEqual(response.data, serializer.data)

    def test_update_book(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Updated Book',
            'author': 'Updated Author',
            'publicationYear': 2023,
            'isbn': '0987654321',
        }
        response = self.client.put(f'/api/books/{self.book.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book = Book.objects.get(pk=self.book.pk)
        self.assertEqual(book.title, data['title'])
        self.assertEqual(book.author, data['author'])
        self.assertEqual(book.publicationYear, data['publicationYear'])
        self.assertEqual(book.isbn, data['isbn'])

    def test_update_book_unauthenticated(self):
        data = {
            'title': 'Updated Book',
        }
        response = self.client.put(f'/api/books/{self.book.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        book = Book.objects.get(pk=self.book.pk)
        self.assertNotEqual(book.title, data['title'])
    
    def test_update_book_not_owner(self):
        self.client.force_authenticate(user=self.not_owner)
        data = {
            'title': 'Updated Book',
        }
        response = self.client.put(f'/api/books/{self.book.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        book = Book.objects.get(pk=self.book.pk)
        self.assertNotEqual(book.title, data['title'])

    def test_partial_update_book(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Updated Book Title 22',
        }
        response = self.client.patch(f'/api/books/{self.book.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book = Book.objects.get(pk=self.book.pk)
        self.assertEqual(book.title, data['title'])
    
    def test_partial_update_book_unauthenticated(self):
        data = {
            'title': 'Updated Book Title 22',
        }
        response = self.client.patch(f'/api/books/{self.book.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        book = Book.objects.get(pk=self.book.pk)
        self.assertNotEqual(book.title, data['title'])
    
    def test_partial_update_book_not_owner(self):
        self.client.force_authenticate(user=self.not_owner)
        data = {
            'title': 'Updated Book Title 22',
        }
        response = self.client.patch(f'/api/books/{self.book.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        book = Book.objects.get(pk=self.book.pk)
        self.assertNotEqual(book.title, data['title'])

    def test_delete_book(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/books/{self.book.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())
        self.assertEqual(response.data, {"message": "Book deleted successfully."})
    
    def test_delete_book_unauthenticated(self):
        response = self.client.delete(f'/api/books/{self.book.pk}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())
    
    def test_delete_book_not_owner(self):
        self.client.force_authenticate(user=self.not_owner)
        response = self.client.delete(f'/api/books/{self.book.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

class UserFavouriteBooksViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.book1 = Book.objects.create(title='Test Book 1', author='Test Author 1', creator=self.user, publicationYear=2022,
            isbn='1234567890')
        self.book2 = Book.objects.create(title='Test Book 2', author='Test Author 2', creator=self.user, publicationYear=2022,
            isbn='1234567890')
        self.book3 = Book.objects.create(title='Test Book 3', author='Test Author 3', creator=self.user, publicationYear=2022,
            isbn='1234567890')
        self.user.favourite_books.add(self.book1, self.book2)

    def test_get_user_favourite_books(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/favourites/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        favourite_books = self.user.favourite_books.all()
        serializer = BookSerializer(favourite_books, many=True)
        self.assertEqual(response.data["results"], serializer.data)

    def test_get_user_favourite_books_unauthenticated(self):
        response = self.client.get('/api/favourites/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
