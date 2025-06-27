import socket
import numpy as np
import soundfile as sf
from django.http import JsonResponse
from threading import Thread
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

# Constants
UDP_IP = "0.0.0.0"
UDP_PORT = 4210
SAMPLE_RATE = 16000
BUFFER_SIZE = 1024 * 4
OUTPUT_WAV = "audio.wav"

# State
frames = []
is_recording = False
sock = None


def esp32(request):
    return render(request, 'esp32.html')

def start_udp_listener():
    global frames, is_recording, sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.settimeout(2.0)
    frames = []
    print("🎤 Listening on UDP...")

    while is_recording:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            if data:
                samples = np.frombuffer(data, dtype=np.int32)
                float_samples = samples.astype(np.float32) / (2**31)
                frames.append(float_samples)
                print(f"📥 Received {len(data)} bytes from {addr}")
        except socket.timeout:
            continue

    # Save when stopped
    if frames:
        audio_data = np.concatenate(frames)
        sf.write(OUTPUT_WAV, audio_data, SAMPLE_RATE)
        print(f"✅ Saved to {OUTPUT_WAV}")
    else:
        print("⚠️ No audio received.")

@csrf_exempt
def start_recording(request):
    global is_recording
    if not is_recording:
        is_recording = True
        thread = Thread(target=start_udp_listener)
        thread.start()
        return JsonResponse({"status": "recording started"})
    return JsonResponse({"status": "already recording"})

@csrf_exempt
def stop_recording(request):
    global is_recording, sock
    if is_recording:
        is_recording = False
        if sock:
            sock.close()
        return JsonResponse({"status": "recording stopped and saved"})
    return JsonResponse({"status": "was not recording"})
