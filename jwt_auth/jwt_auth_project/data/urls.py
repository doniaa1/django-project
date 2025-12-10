from django.urls import path
from .views import upload_file, export_file_data

urlpatterns = [
    path('upload', upload_file, name='upload_file'),
    path('export/<int:file_id>', export_file_data, name='export_file_data'),
]