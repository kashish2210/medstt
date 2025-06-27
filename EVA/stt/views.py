from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings
import threading
from .utils import transcribe
from .models import Transcription
from google import genai

client = genai.Client(api_key=os.environ['Gemini_API'])

# Create your views here.
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
        # Save the file to MEDIA_ROOT/uploads/ folder
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, str(identifier) + audio_file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)
        
        threading.Thread(target=transcribe, args=(iter, file_path, identifier, isFinal)).start()
        return JsonResponse({'status': 'success', 'message': 'Audio uploaded successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    

def result_json(request, identifier):
    # transcript = get_object_or_404(Transcription, identifier =identifier)
    # transcript = transcript.data
    transcript = """The patient appears to be a 27-year-old female presenting with symptoms consistent with a mild upper respiratory tract infection. Upon examination, her throat is slightly inflamed with no signs of tonsillar exudate. Lungs are clear on auscultation. Temperature is 99.4°F. No shortness of breath or chest pain reported. It’s likely viral in origin. Patient is otherwise healthy, no significant medical history. I’ve advised supportive care and symptomatic relief."""
    patient_problem = """I’ve had a sore throat and a stuffy nose for the past 3 days. I feel a bit tired, and my body aches a little, but I haven’t had any major fever or cough. Just a general feeling of being unwell."""
    prompt = f"""You’re a distinguished and experienced medical physician. Here's a transcription of what a doctor thinks after consultation with a patient along with the problem faced by the patient. 
Create a JSON output like:
{{“Symptoms”: “symptoms from the transcription”,
  “Observation”: “basically some observational tests done by the doctor and what they observed like looking at throat and observation might be slight inflammation”
 “Diagnosis”: “Diagnosis of the doctor that fits the symptoms.”,
 “Prescription”: “Given by the doctor”,
 “Guidelines/Advices”: “Advices or restrictions that doctor tell the patient to follow”,
}}

TRANSCRIPTION: "{transcript}"
PROBLEM/SYMPTOMS OF PATIENT (told by the patient before consultation): “{patient_problem}”

**Return only json, no text before or after it**
**No need to describe and elaborate what doctor said, just write what the doctor said in essence. And also if some things like guidelines is absent then leave it empty.**
**If doctor uses some medical term or complex terms in prescription  other than medicines then explain it in simple terms in a bracket in a manner of action like what the patient should do in short**
**Return the json as text, no need to add markup like ```json***
"""
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    print(response.text)