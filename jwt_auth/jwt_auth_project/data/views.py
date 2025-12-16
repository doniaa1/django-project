from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from django.http import HttpResponse

from users.decorators import permit_if_role_in
from .models import UploadedFile, FileData
import pandas as pd 
from django.shortcuts import get_object_or_404

@permit_if_role_in('upload_file')
@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_file(request):

    
    if 'file' not in request.FILES:
        return Response({"error": "No file provided"}, status=400)

    uploaded_file = request.FILES['file']
    file_instance = UploadedFile.objects.create(file=uploaded_file)

    df = pd.read_excel(uploaded_file)

    for _, row in df.iterrows():
        FileData.objects.create(
            uploaded_file=file_instance,
            name=row.get('name'),
            contact=row.get('contact'),
            address=row.get('address')
        )

    return Response({
        "status": "success",
        "file_id": file_instance.id,
        "file_name": file_instance.file.name
    })


@permit_if_role_in('export_file_data')
@api_view(['GET'])
def export_file_data(request, file_id):
    file_instance = get_object_or_404(UploadedFile, id=file_id)
    data = FileData.objects.filter(uploaded_file=file_instance)

    rows = []
    for d in data:
        rows.append({
            'Name': d.name,
            'Contact': d.contact,
            'Address': d.address
        })

    df = pd.DataFrame(rows)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{file_instance.file.name}_data.xlsx"'
    df.to_excel(response, index=False)
    return response