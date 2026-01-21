from typing import Dict, Optional, List
import re
from datetime import datetime


class BookingFlow:
    """Manages conversational booking flow with slot filling"""

    def __init__(self):
        self.required_fields = [
            'name', 'email', 'phone', 'booking_type', 'date', 'time'
        ]
        self.booking_data: Dict[str, str] = {}
        self.confirmation_pending = False

    def reset(self):
        self.booking_data = {}
        self.confirmation_pending = False

    def extract_info_from_message(self, message: str) -> Dict[str, str]:
        extracted = {}
        msg = message.strip()
        msg_lower = msg.lower()

        # ----------------------
        # NAME (FIXED)
        # ----------------------
        if 'name' not in self.booking_data:
            # Handles:
            # "Harshini"
            # "My name is Harshini"
            # "I am Harshini"
            name_match = re.search(
                r'(?:my name is|i am|this is)?\s*([A-Za-z]{2,}(?:\s[A-Za-z]{2,})?)',
                msg,
                re.IGNORECASE
            )
            if name_match and msg.isalpha() or len(msg.split()) <= 2:
                extracted['name'] = name_match.group(1).title()
                return extracted

        # ----------------------
        # EMAIL
        # ----------------------
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, msg)
        if email_match:
            extracted['email'] = email_match.group()

        # ----------------------
        # PHONE
        # ----------------------
        phone_pattern = r'\b\d{10}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        phone_match = re.search(phone_pattern, msg)
        if phone_match:
            extracted['phone'] = re.sub(r'\D', '', phone_match.group())

        # ----------------------
        # DATE
        # ----------------------
        date_pattern = r'\b\d{4}-\d{2}-\d{2}\b'
        date_match = re.search(date_pattern, msg)
        if date_match:
            extracted['date'] = date_match.group()

        # ----------------------
        # TIME
        # ----------------------
        time_pattern = r'\b\d{1,2}:\d{2}\b'
        time_match = re.search(time_pattern, msg)
        if time_match:
            h, m = time_match.group().split(":")
            extracted['time'] = f"{int(h):02d}:{m}"

        # ----------------------
        # SERVICE
        # ----------------------
        services = {
            "bridal": "Bridal Makeup",
            "party": "Party Makeup",
            "color": "Hair Coloring",
            "haircut": "Haircut",
            "cut": "Haircut",
            "manicure": "Manicure",
            "pedicure": "Pedicure",
            "facial": "Facial",
            "massage": "Massage",
            "spa": "Hair Spa",
            "makeup": "Party Makeup"
        }

        for key, value in services.items():
            if key in msg_lower:
                extracted['booking_type'] = value
                break

        return extracted

    def update_booking_data(self, new_data: Dict[str, str]):
        self.booking_data.update(new_data)

    def get_missing_fields(self) -> List[str]:
        return [
            f for f in self.required_fields
            if f not in self.booking_data or not self.booking_data[f]
        ]

    def is_complete(self) -> bool:
        return len(self.get_missing_fields()) == 0

    def get_next_question(self) -> Optional[str]:
        missing = self.get_missing_fields()
        if not missing:
            return None

        questions = {
            'name': "What's your name?",
            'email': "What's your email address?",
            'phone': "What's your phone number? (10 digits)",
            'booking_type': (
                "Which service would you like? "
                "(Haircut, Hair Coloring, Manicure, Pedicure, Facial, Massage, Hair Spa, Bridal Makeup, Party Makeup)"
            ),
            'date': "What date would you prefer? (YYYY-MM-DD)",
            'time': "What time works for you? (HH:MM)"
        }

        return questions.get(missing[0])

    def get_confirmation_summary(self) -> str:
        if not self.is_complete():
            return "Cannot generate summary – missing information."

        return f"""
📋 **Booking Summary**

👤 **Name:** {self.booking_data['name']}
📧 **Email:** {self.booking_data['email']}
📱 **Phone:** {self.booking_data['phone']}
💅 **Service:** {self.booking_data['booking_type']}
📅 **Date:** {self.booking_data['date']}
⏰ **Time:** {self.booking_data['time']}

Is this information correct? Reply **yes** to confirm or **no** to edit.
"""
