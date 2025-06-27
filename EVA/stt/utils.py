import whisper
from .models import Transcription
import json

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
