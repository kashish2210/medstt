import socket
import numpy as np
import soundfile as sf
import os
import json
from django.http import JsonResponse, HttpResponse
from threading import Thread
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings
import whisper
import requests
import time
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import io

# ====== Configuration ======
UDP_IP = "0.0.0.0"
UDP_PORT = 4210
SAMPLE_RATE = 16000
BUFFER_SIZE = 1024 * 4
UPLOAD_FOLDER = os.path.join(settings.MEDIA_ROOT, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
OUTPUT_WAV_NAME = "audio.wav"
OUTPUT_WAV_PATH = os.path.join(UPLOAD_FOLDER, OUTPUT_WAV_NAME)

frames = []
is_recording = False
sock = None
latest_transcription_result = {}

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
        if frames:
            audio_data = np.concatenate(frames)
            sf.write(OUTPUT_WAV_PATH, audio_data, SAMPLE_RATE)
            print(f"✅ Audio saved to {OUTPUT_WAV_PATH}")
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
    global is_recording, latest_transcription_result
    if is_recording:
        is_recording = False

        def process_audio_and_llama():
            global latest_transcription_result
            time.sleep(1)

            # === Transcribe ===
            model = whisper.load_model("small")
            result = model.transcribe(OUTPUT_WAV_PATH)
            transcription_text = result["text"]
            print("📝 Transcription:", transcription_text)

            # === Enhanced LLaMA Prompt ===
            prompt = f"""You're a distinguished medical physician. Analyze this doctor's consultation transcription and create a structured medical report.

Create a JSON output with these exact fields (only include fields that have relevant information):
{{
  "patient_info": {{
    "consultation_date": "{datetime.now().strftime('%Y-%m-%d')}",
    "consultation_time": "{datetime.now().strftime('%H:%M:%S')}"
  }},
  "chief_complaint": "main reason for visit",
  "symptoms": "detailed symptoms reported",
  "physical_examination": "physical findings and observations",
  "vital_signs": "blood pressure, temperature, pulse, etc if mentioned",
  "diagnosis": "primary diagnosis or differential diagnoses",
  "treatment_plan": "medications, procedures, treatments",
  "advice_and_instructions": "lifestyle advice, follow-up instructions",
  "follow_up": "when to return, monitoring instructions",
  "doctor_notes": "additional clinical notes"
}}

TRANSCRIPTION: "{transcription_text}"

**Return only valid JSON, no explanation before or after**
**If transcription is unclear or gibberish, return: {{ "error": "transcription_unclear" }}**
"""

            try:
                payload = {
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False
                }
                
                response = requests.post("http://localhost:11434/api/generate", json=payload)
                json_data = response.json()
                llama_response = json_data['response']
                
                # Parse the JSON response
                try:
                    parsed_result = json.loads(llama_response)
                    latest_transcription_result = {
                        "transcription": transcription_text,
                        "structured_data": parsed_result,
                        "timestamp": datetime.now().isoformat()
                    }
                    print("💡 Structured Medical Data:", json.dumps(parsed_result, indent=2))
                except json.JSONDecodeError:
                    latest_transcription_result = {
                        "transcription": transcription_text,
                        "raw_response": llama_response,
                        "error": "Failed to parse JSON response",
                        "timestamp": datetime.now().isoformat()
                    }
                    
            except Exception as e:
                latest_transcription_result = {
                    "transcription": transcription_text,
                    "error": f"LLaMA processing error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
                print("❌ Error in LLaMA processing:", e)

        Thread(target=process_audio_and_llama).start()

        file_url = f"{settings.MEDIA_URL}uploads/{OUTPUT_WAV_NAME}"
        return JsonResponse({
            "status": "Recording stopped",
            "file_url": file_url,
            "message": "Audio is being processed. Check /get_transcription/ for results."
        })

    return JsonResponse({"status": "Was not recording"})

@csrf_exempt
def get_transcription(request):
    """Get the latest transcription result"""
    global latest_transcription_result
    if latest_transcription_result:
        return JsonResponse(latest_transcription_result)
    else:
        return JsonResponse({"message": "No transcription available yet"})

def generate_medical_report_pdf(data):
    """Generate a professional medical report PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                           topMargin=72, bottomMargin=18)
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue,
        borderWidth=1,
        borderColor=colors.lightgrey,
        borderPadding=5,
        backColor=colors.lightgrey
    )
    
    content_style = ParagraphStyle(
        'CustomContent',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=10,
        alignment=TA_JUSTIFY
    )
    
    story = []
    
    # Header
    story.append(Paragraph("MEDICAL CONSULTATION REPORT", title_style))
    story.append(Spacer(1, 20))
    
    # Patient Info Table
    if 'structured_data' in data and 'patient_info' in data['structured_data']:
        patient_info = data['structured_data']['patient_info']
        patient_data = [
            ['Consultation Date:', patient_info.get('consultation_date', 'N/A')],
            ['Consultation Time:', patient_info.get('consultation_time', 'N/A')],
            ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        patient_table = Table(patient_data, colWidths=[2*inch, 3*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(patient_table)
        story.append(Spacer(1, 20))
    
    # Medical sections
    if 'structured_data' in data and isinstance(data['structured_data'], dict):
        sections = [
            ('chief_complaint', 'Chief Complaint'),
            ('symptoms', 'Symptoms'),
            ('physical_examination', 'Physical Examination'),
            ('vital_signs', 'Vital Signs'),
            ('diagnosis', 'Diagnosis'),
            ('treatment_plan', 'Treatment Plan'),
            ('advice_and_instructions', 'Advice & Instructions'),
            ('follow_up', 'Follow-up'),
            ('doctor_notes', 'Doctor\'s Notes')
        ]
        
        for key, title in sections:
            if key in data['structured_data'] and data['structured_data'][key]:
                story.append(Paragraph(title, heading_style))
                story.append(Paragraph(str(data['structured_data'][key]), content_style))
                story.append(Spacer(1, 10))
    
    # Original Transcription
    if 'transcription' in data:
        story.append(Paragraph("Original Transcription", heading_style))
        story.append(Paragraph(data['transcription'], content_style))
        story.append(Spacer(1, 20))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("This report was generated automatically from audio transcription.", footer_style))
    story.append(Paragraph("Please verify all information for accuracy.", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

@csrf_exempt
def download_pdf_report(request):
    """Generate and download PDF report"""
    global latest_transcription_result
    
    if not latest_transcription_result:
        return JsonResponse({"error": "No transcription data available"}, status=404)
    
    try:
        pdf_buffer = generate_medical_report_pdf(latest_transcription_result)
        
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        filename = f"medical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return JsonResponse({"error": f"Failed to generate PDF: {str(e)}"}, status=500)

@csrf_exempt
def view_json_report(request):
    """View formatted JSON report in browser"""
    global latest_transcription_result
    
    if not latest_transcription_result:
        return JsonResponse({"error": "No transcription data available"}, status=404)
    
    # Pretty print JSON for web view
    formatted_json = json.dumps(latest_transcription_result, indent=2, ensure_ascii=False)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Medical Report - JSON View</title>
        <style>
            body {{ font-family: 'Courier New', monospace; margin: 20px; background: #f5f5f5; }}
            .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; color: #2c3e50; margin-bottom: 20px; }}
            .json-content {{ background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }}
            .download-btn {{ display: inline-block; margin: 10px 5px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
            .download-btn:hover {{ background: #0056b3; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Medical Consultation Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <a href="/esp32/download-pdf/" class="download-btn">📄 Download PDF</a>
                <a href="/esp32/get-transcription/" class="download-btn">📊 Raw JSON</a>
            </div>
            <div class="json-content">
                <pre>{formatted_json}</pre>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HttpResponse(html_content, content_type='text/html')