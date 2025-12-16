from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from library.serializers import BookListSerializer
from .models import Book


from django.utils.decorators import method_decorator
from users.decorators import permit_if_role_in



#@api_view(['GET'])
#def all_books(request):
#    books = Book.objects.select_related('author', 'publisher')
#    data = [{"title": b.title, "author": b.author.name, "publisher": b.publisher.name} for b in books]
#    return Response(data)

@api_view(['GET'])
def books_by_author(request, author_name):
    books = Book.objects.filter(author__name=author_name)
    data = [{"title": b.title, "publisher": b.publisher.name} for b in books]
    return Response(data)

@api_view(['GET'])
def books_by_publisher(request, publisher_name):
    books = Book.objects.filter(publisher__name=publisher_name)
    data = [{"title": b.title, "author": b.author.name} for b in books]
    return Response(data)

@api_view(['GET'])
def books_by_author_and_publisher(request, author_name, publisher_name):
    books = Book.objects.filter(author__name=author_name, publisher__name=publisher_name)
    data = [{"title": b.title} for b in books]
    return Response(data)
#-------------------------------------------
@api_view(['GET'])
def books_list_serialized(request):
    qs = Book.objects.select_related('author', 'publisher').all()
    serializer = BookListSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def books_list(request):
    qs = Book.objects.select_related('author', 'publisher').all()

    result = []
    for b in qs:
        item = {
            "id": b.id,
            "title": b.title,
            "author_name": b.author.name,
            "publisher_name": b.publisher.name,
            "published_date": b.published_date.isoformat() if b.published_date else None,
            "title_with_author": f"{b.title} — {b.author.name}"
        }
        result.append(item)

    return Response(result)

@permit_if_role_in('view_book')
@api_view(['GET'])
def BookListView(request):
    qs = Book.objects.select_related('author', 'publisher').all()

    result = []
    for b in qs:
        item = {
            "id": b.id,
            "title": b.title,
            "author_name": b.author.name,
            "publisher_name": b.publisher.name,
            "published_date": b.published_date.isoformat() if b.published_date else None,
            "title_with_author": f"{b.title} — {b.author.name}"
        }
        result.append(item)

    return Response(result)