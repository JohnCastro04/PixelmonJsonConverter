from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
import json
import zipfile
import io
import traceback
from .conversion_logic import convert_json_file_content

def index(request):
    """Main page view"""
    return render(request, 'converter/index.html')

@csrf_exempt
@require_http_methods(["POST"])
def convert_single_file(request):
    """Convert a single JSON file"""
    try:
        if 'json_file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        uploaded_file = request.FILES['json_file']
        
        # Validate file type
        if not uploaded_file.name.endswith('.json'):
            return JsonResponse({'error': 'File must be a JSON file'}, status=400)
        
        # Read file content
        try:
            file_content = uploaded_file.read().decode('utf-8')
        except UnicodeDecodeError:
            return JsonResponse({'error': 'File must be UTF-8 encoded'}, status=400)
        
        # Convert the JSON
        try:
            converted_content = convert_json_file_content(file_content, uploaded_file.name)
        except Exception as e:
            return JsonResponse({'error': f'Conversion error: {str(e)}'}, status=400)
        
        # Generate new filename
        original_name = uploaded_file.name
        if original_name.endswith('.json'):
            original_name = original_name[:-5]  # Remove .json
        new_filename = f"{original_name}_new.json"
        
        # Return the converted file as download
        response = HttpResponse(converted_content, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{new_filename}"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def convert_zip_file(request):
    """Convert multiple JSON files from a ZIP archive"""
    try:
        if 'zip_file' not in request.FILES:
            return JsonResponse({'error': 'No ZIP file provided'}, status=400)
        
        uploaded_file = request.FILES['zip_file']
        
        # Validate file type
        if not uploaded_file.name.endswith('.zip'):
            return JsonResponse({'error': 'File must be a ZIP archive'}, status=400)
        
        results = []
        converted_files = {}
        
        try:
            # Read the ZIP file
            with zipfile.ZipFile(uploaded_file, 'r') as zip_file:
                json_files = [name for name in zip_file.namelist() if name.endswith('.json') and not name.endswith('_new.json')]
                
                if not json_files:
                    return JsonResponse({'error': 'No JSON files found in ZIP archive'}, status=400)
                
                for json_filename in json_files:
                    try:
                        # Read JSON file from ZIP
                        with zip_file.open(json_filename) as json_file:
                            file_content = json_file.read().decode('utf-8')
                        
                        # Convert the JSON
                        converted_content = convert_json_file_content(file_content, json_filename)
                        
                        # Generate new filename
                        original_name = json_filename
                        if original_name.endswith('.json'):
                            original_name = original_name[:-5]  # Remove .json
                        new_filename = f"{original_name}_new.json"
                        
                        converted_files[new_filename] = converted_content
                        results.append({
                            'original': json_filename,
                            'converted': new_filename,
                            'status': 'success'
                        })
                        
                    except Exception as e:
                        results.append({
                            'original': json_filename,
                            'converted': None,
                            'status': 'error',
                            'error': str(e)
                        })
                
        except zipfile.BadZipFile:
            return JsonResponse({'error': 'Invalid ZIP file'}, status=400)
        
        # Create a new ZIP with converted files
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in converted_files.items():
                zip_file.writestr(filename, content)
        
        zip_buffer.seek(0)
        
        # Return the ZIP file as download
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        original_zip_name = uploaded_file.name
        if original_zip_name.endswith('.zip'):
            original_zip_name = original_zip_name[:-4]  # Remove .zip
        response['Content-Disposition'] = f'attachment; filename="{original_zip_name}_converted.zip"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def convert_text_input(request):
    """Convert JSON from text input"""
    try:
        data = json.loads(request.body)
        json_text = data.get('json_text', '').strip()
        
        if not json_text:
            return JsonResponse({'error': 'No JSON text provided'}, status=400)
        
        # Convert the JSON
        try:
            converted_content = convert_json_file_content(json_text, "text_input")
        except Exception as e:
            return JsonResponse({'error': f'Conversion error: {str(e)}'}, status=400)
        
        return JsonResponse({
            'success': True,
            'converted_json': converted_content
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

def help_view(request):
    """Help page view"""
    return render(request, 'converter/help.html')