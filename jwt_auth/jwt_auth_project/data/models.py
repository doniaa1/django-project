from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to="uploaded_files")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

class FileData(models.Model):
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='data')
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    address = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.name} - {self.contact}"