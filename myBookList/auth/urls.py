from django.urls import path
from .views import LoginView, CreateUserView, LogoutView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', CreateUserView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout')
]
