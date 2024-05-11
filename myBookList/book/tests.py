from django.test import TestCase
from django.contrib.auth.models import User
from .models import Book
from django.core.exceptions import ValidationError

class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user for testing
        cls.user = User.objects.create_user(username='testuser', password='testpassword')

        # Create a book for testing
        cls.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            publicationYear=2022,
            isbn='1234567890',
            creator=cls.user
        )
    
    def test_book_creation(self):
        book = Book.objects.get(id=self.book.id)
        self.assertEqual(book.title, 'Test Book')
        self.assertEqual(book.author, 'Test Author')
        self.assertEqual(book.publicationYear, 2022)
        self.assertEqual(book.isbn, '1234567890')
        self.assertEqual(book.creator, self.user)
    
    def test_book_creation_invalid_isbn(self):
        book = Book(
                title='Test Book',
                author='Test Author',
                publicationYear=2022,
                isbn='22',
                creator=self.user
            )
        with self.assertRaises(ValidationError):
            # This will run the field validators and raise a ValidationError if any of them fail
            book.full_clean()


    def test_book_str_representation(self):
        book = Book.objects.get(id=self.book.id)
        expected_str = f"Test Book by Test Author - 2022"
        self.assertEqual(str(book), expected_str)

    def test_book_favourites(self):
        user1 = User.objects.create_user(username='user1', password='password1')
        user2 = User.objects.create_user(username='user2', password='password2')

        # Add user1 as a favourite for the book
        self.book.favourites.add(user1)

        # Check if user1 is in the book's favourites
        self.assertIn(user1, self.book.favourites.all())
        self.assertNotIn(user2, self.book.favourites.all())
