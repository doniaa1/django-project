from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Publisher(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='books')
    published_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads')
    uploaded_at = models.DateTimeField(auto_now_add=True)