from django.shortcuts import render, get_object_or_404,redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings
import threading
from .utils import transcribe, result_json
from .models import Transcription
import json
import requests
import time


def index(request):
    return render(request, 'stt/stt.html')



@csrf_exempt
def upload_audio(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        identifier = request.POST['identifier']
        isFinal = True if request.POST['final'] == 'true' else False
        iter = audio_file.name.split(".")[0]
        print(type(request.POST['final']), request.POST['final'])
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, str(identifier) + audio_file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)
        
        threading.Thread(target=transcribe, args=(iter, file_path, identifier, isFinal)).start()
        if isFinal:
            print('this occurs')
            response = result_json(identifier)
            print('got the response')
            print(response)
            if response.ok:
                result = response.json()
                data = json.loads(result['response'])
                print(data)
                return JsonResponse(data, safe=True)
            else:
                return JsonResponse({'status':'error'}, safe=False)
        return JsonResponse({'status': 'success', 'message': 'Audio uploaded successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    
