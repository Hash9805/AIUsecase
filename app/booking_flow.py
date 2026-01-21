from typing import Dict, Optional, List
import re
from datetime import datetime

class BookingFlow:
    """Manages conversational booking flow with slot filling"""
    
    def __init__(self):
        self.required_fields = ['name', 'email', 'phone', 'booking_type', 'date', 'time']
        self.booking_data = {}
        self.confirmation_pending = False
    
    def reset(self):
        """Reset booking data"""
        self.booking_data = {}
        self.confirmation_pending = False
    
    def extract_info_from_message(self, message: str) -> Dict[str, str]:
        """Extract booking information from user message"""
        extracted = {}
        message_lower = message.lower()
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, message)
        if email_match:
            extracted['email'] = email_match.group()
        
        # Extract phone (10 digits)
        phone_pattern = r'\b\d{10}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        phone_match = re.search(phone_pattern, message)
        if phone_match:
            extracted['phone'] = phone_match.group().replace('-', '').replace('.', '').replace(' ', '')
        
        # Extract date (YYYY-MM-DD format)
        date_pattern = r'\b\d{4}-\d{2}-\d{2}\b'
        date_match = re.search(date_pattern, message)
        if date_match:
            extracted['date'] = date_match.group()
        
        # Extract time (HH:MM format)
        time_pattern = r'\b\d{1,2}:\d{2}\b'
        time_match = re.search(time_pattern, message)
        if time_match:
            time_str = time_match.group()
            # Ensure HH:MM format
            parts = time_str.split(':')
            extracted['time'] = f"{int(parts[0]):02d}:{parts[1]}"
        
        # Check for service mentions
        services = [
            "haircut", "hair cut", "cut",
            "coloring", "color", "hair color",
            "manicure", "mani",
            "pedicure", "pedi",
            "facial", "face",
            "massage",
            "hair spa", "spa",
            "bridal makeup", "bridal",
            "party makeup", "makeup"
        ]
        
        for service in services:
            if service in message_lower:
                if "bridal" in message_lower:
                    extracted['booking_type'] = "Bridal Makeup"
                elif "party" in message_lower or ("makeup" in message_lower and "bridal" not in message_lower):
                    extracted['booking_type'] = "Party Makeup"
                elif "coloring" in message_lower or "color" in message_lower:
                    extracted['booking_type'] = "Hair Coloring"
                elif "haircut" in message_lower or "hair cut" in message_lower or "cut" in message_lower:
                    extracted['booking_type'] = "Haircut"
                elif "manicure" in message_lower or "mani" in message_lower:
                    extracted['booking_type'] = "Manicure"
                elif "pedicure" in message_lower or "pedi" in message_lower:
                    extracted['booking_type'] = "Pedicure"
                elif "facial" in message_lower:
                    extracted['booking_type'] = "Facial"
                elif "massage" in message_lower:
                    extracted['booking_type'] = "Massage"
                elif "spa" in message_lower:
                    extracted['booking_type'] = "Hair Spa"
                break
        
        return extracted
    
    def update_booking_data(self, new_data: Dict[str, str]):
        """Update booking data with new information"""
        self.booking_data.update(new_data)
    
    def get_missing_fields(self) -> List[str]:
        """Get list of missing required fields"""
        return [field for field in self.required_fields if field not in self.booking_data or not self.booking_data[field]]
    
    def is_complete(self) -> bool:
        """Check if all required fields are collected"""
        return len(self.get_missing_fields()) == 0
    
    def get_next_question(self) -> Optional[str]:
        """Get next question to ask user"""
        missing = self.get_missing_fields()
        
        if not missing:
            return None
        
        field = missing[0]
        
        questions = {
            'name': "What's your name?",
            'email': "What's your email address?",
            'phone': "What's your phone number? (10 digits)",
            'booking_type': "Which service would you like? (Haircut, Hair Coloring, Manicure, Pedicure, Facial, Massage, Hair Spa, Bridal Makeup, Party Makeup)",
            'date': "What date would you prefer? (Please use format: YYYY-MM-DD, e.g., 2026-01-25)",
            'time': "What time works for you? (Please use format: HH:MM, e.g., 14:30)"
        }
        
        return questions.get(field, f"Please provide your {field}")
    
    def get_confirmation_summary(self) -> str:
        """Generate booking summary for confirmation"""
        if not self.is_complete():
            return "Cannot generate summary - missing required information"
        
        summary = f"""
📋 **Booking Summary**

👤 **Name:** {self.booking_data['name']}
📧 **Email:** {self.booking_data['email']}
📱 **Phone:** {self.booking_data['phone']}
💅 **Service:** {self.booking_data['booking_type']}
📅 **Date:** {self.booking_data['date']}
⏰ **Time:** {self.booking_data['time']}

Is this information correct? Please reply with **"yes"** to confirm or **"no"** to make changes.
"""
        return summary
    
    def validate_field(self, field: str, value: str) -> tuple[bool, str]:
        """Validate individual field"""
        if field == 'email':
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, value):
                return False, "Please provide a valid email address (e.g., user@example.com)"
        
        elif field == 'phone':
            clean_phone = value.replace('-', '').replace('.', '').replace(' ', '')
            if not clean_phone.isdigit() or len(clean_phone) != 10:
                return False, "Please provide a valid 10-digit phone number"
        
        elif field == 'date':
            pattern = r'^\d{4}-\d{2}-\d{2}$'
            if not re.match(pattern, value):
                return False, "Please enter date in YYYY-MM-DD format (e.g., 2026-01-25)"
            try:
                date_obj = datetime.strptime(value, '%Y-%m-%d')
                if date_obj.date() < datetime.now().date():
                    return False, "Please select a future date"
            except ValueError:
                return False, "Invalid date. Please use YYYY-MM-DD format"
        
        elif field == 'time':
            pattern = r'^\d{1,2}:\d{2}$'
            if not re.match(pattern, value):
                return False, "Please enter time in HH:MM format (e.g., 14:30)"
            try:
                time_obj = datetime.strptime(value, '%H:%M')
                hour = time_obj.hour
                if hour < 9 or hour >= 20:
                    return False, "Please select a time between 09:00 and 20:00"
            except ValueError:
                return False, "Invalid time. Please use HH:MM format"
        
        return True, "Valid"