import socket
import numpy as np
import soundfile as sf
from django.http import JsonResponse
from threading import Thread
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

# ====== Configuration ======
UDP_IP = "0.0.0.0"
UDP_PORT = 4210
SAMPLE_RATE = 16000
BUFFER_SIZE = 1024 * 4
OUTPUT_WAV = "audio.wav"

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

    print("🎤 Listening for UDP audio...")

    try:
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
    finally:
        # Save when recording stops
        if frames:
            audio_data = np.concatenate(frames)
            sf.write(OUTPUT_WAV, audio_data, SAMPLE_RATE)
            print(f"✅ Audio saved to {OUTPUT_WAV}")
        else:
            print("⚠️ No audio received.")
        
        if sock:
            sock.close()
            print("🔌 Socket closed")
@csrf_exempt
def start_recording(request):
    global is_recording
    if not is_recording:
        is_recording = True
        thread = Thread(target=start_udp_listener)
        thread.start()
        return JsonResponse({"status": "Recording started"})
    return JsonResponse({"status": "Already recording"})

@csrf_exempt
def stop_recording(request):
    global is_recording
    if is_recording:
        is_recording = False  # Will stop loop in thread
        return JsonResponse({"status": "Recording stopped, saving file..."})
    return JsonResponse({"status": "Was not recording"})
