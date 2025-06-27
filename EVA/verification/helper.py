from django.conf import settings
from twilio.rest import Client


class MessageHandler:
    def __init__(self, phone_number, otp) -> None:
        # Clean the phone number to prevent +91 duplication
        self.phone_number = self._sanitize_number(phone_number)
        self.otp = otp

    def _sanitize_number(self, number):
        """
        Sanitize the number by removing +91 or leading 0 if present.
        """
        number = number.strip()
        if number.startswith('+91'):
            return number[3:]
        elif number.startswith('0'):
            return number[1:]
        return number

    def send_otp_via_message(self):
        try:
            client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
            message = client.messages.create(
                body=f'Your OTP is: {self.otp}',
                from_=settings.TWILIO_PHONE_NUMBER,
                to=f'{settings.COUNTRY_CODE}{self.phone_number}'
            )
            return message.sid  # Useful to confirm
        except Exception as e:
            print(f"SMS Error: {e}")
            raise

    def send_otp_via_whatsapp(self):
        try:
            client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
            message = client.messages.create(
                body=f'Your OTP is: {self.otp}',
                from_=f'whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}',
                to=f'whatsapp:{settings.COUNTRY_CODE}{self.phone_number}'
            )
            return message.sid
        except Exception as e:
            print(f"WhatsApp Error: {e}")
            raise
