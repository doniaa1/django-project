from django.urls import path
from . import views
from django.urls import path


urlpatterns = [
    #path('books', views.all_books),
    path('books/author/<str:author_name>', views.books_by_author),
    path('books/publisher/<str:publisher_name>', views.books_by_publisher),
    path('books/author/<str:author_name>/publisher/<str:publisher_name>', views.books_by_author_and_publisher),
    path('books/serialized', views.books_list_serialized, name='books-serialized'),
    path('books/list', views.books_list, name='books-list'),
    path('books', views.BookListView.as_view(), name='books-list'),
    



]
