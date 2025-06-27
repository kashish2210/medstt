import whisper
from .models import Transcription
import json
import requests
import time

def transcribe(iter, path, identifier, isFinal):
    transcription_record = Transcription.objects.filter(identifier = identifier)
    model = whisper.load_model("tiny")
    result = model.transcribe(path)["text"]
    result = [iter, result]
    if not transcription_record:
        transcription_record = Transcription.objects.create(identifier=str(identifier), data = [result] )
        transcription_record.save()
    else:
        transcription_record = transcription_record[0]
        data = transcription_record.data
        data.append(result)
        transcription_record.data = data
        transcription_record.save()

    if isFinal:
        data = transcription_record.data
        data = sorted(data, key = lambda item: item[0])
        data = map(lambda x: x[1], data)
        data = " ".join(data)
        transcription_record.data = data
        transcription_record.save()


    print('done')
    

def result_json(identifier):
    # transcript = get_object_or_404(Transcription, identifier =identifier)
    # transcript = transcript.data
    url = "http://localhost:11434/api/generate"
    # transcript = """The patient appears to be a 27-year-old female presenting with symptoms consistent with a mild upper respiratory tract infection. Upon examination, her throat is slightly inflamed with no signs of tonsillar exudate. Lungs are clear on auscultation. Temperature is 99.4°F. No shortness of breath or chest pain reported. It’s likely viral in origin. Patient is otherwise healthy, no significant medical history. I’ve advised supportive care and symptomatic relief."""
    patient_problem = """I’ve had a sore throat and a stuffy nose for the past 3 days. I feel a bit tired, and my body aches a little, but I haven’t had any major fever or cough. Just a general feeling of being unwell."""
    
    
    transcript = Transcription.objects.filter(identifier=identifier)
    print('arrived in redirect')
    while not transcript.exists():
        time.sleep(0.25)
        transcript = Transcription.objects.filter(identifier=identifier)
    
    transcript = transcript[0]
    while type(transcript.data) != type("abc"):
        time.sleep(0.25)
        transcript = Transcription.objects.filter(identifier=identifier)[0]
    
    transcript = transcript.data
    print("reached here as well.", transcript)
    prompt = f"""You’re a distinguished and experienced medical physician. Here's a transcription of what a doctor thinks after consultation with a patient along with the problem faced by the patient. 
Create a JSON output like:
{{"Symptoms": "symptoms from the transcription",
  "Observation": "basically some observational tests done by the doctor and what they observed like looking at throat and observation might be slight inflammation",
 "Diagnosis": "Diagnosis of the doctor that fits the symptoms.",
 "Prescription": "Given by the doctor",
 "Guidelines/Advices": "Advices or restrictions that doctor tell the patient to follow",
}}

TRANSCRIPTION: "{transcript}"
PROBLEM/SYMPTOMS OF PATIENT (told by the patient before consultation): "{patient_problem}"

**Return only json, no text before or after it**
**No need to describe and elaborate what doctor said, just write what the doctor said in essence. And also if some things like guidelines is absent then leave it empty.**
**If doctor uses some medical term or complex terms in prescription  other than medicines then explain it in simple terms in a bracket in a manner of action like what the patient should do in short**
**Return the json as text, no need to add markup like ```json***
**Don't use semicolon i.e ; instead of comma i.e ,**
**If the transcript is empty or gibberish, just return {{'response': 'gibberish'}}**
"""

    payload = {
    "model": "llama3.2",  
    "prompt": prompt,
    "stream": False  # Set True to get streaming tokens
}
    response = requests.post(url, json=payload)
    return response
    
    
