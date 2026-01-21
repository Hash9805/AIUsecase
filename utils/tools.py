from typing import Dict, Any
from models import Customer, Booking, get_session
from utils.email_service import EmailService
from utils.rag_pipeline import RAGPipeline
from sqlalchemy.exc import IntegrityError
import re

class BookingTools:
    """Tools for handling RAG, booking persistence, and email"""
    
    def __init__(self, rag_pipeline: RAGPipeline):
        self.rag_pipeline = rag_pipeline
        self.email_service = EmailService()
    
    def rag_tool(self, query: str) -> Dict[str, Any]:
        """
        RAG Tool: Retrieve information from uploaded documents
        Input: query string
        Output: retrieved answer
        """
        try:
            context = self.rag_pipeline.query(query)
            
            return {
                "success": True,
                "answer": context,
                "message": "Successfully retrieved information"
            }
        except Exception as e:
            return {
                "success": False,
                "answer": "",
                "message": f"Error retrieving information: {str(e)}"
            }
    
    def booking_persistence_tool(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Booking Persistence Tool: Save booking to database
        Input: structured booking payload (name, email, phone, booking_type, date, time)
        Output: success status and booking ID
        """
        session = get_session()
        
        try:
            # Validate required fields
            required_fields = ['name', 'email', 'phone', 'booking_type', 'date', 'time']
            for field in required_fields:
                if field not in booking_data or not booking_data[field]:
                    return {
                        "success": False,
                        "booking_id": None,
                        "message": f"Missing required field: {field}"
                    }
            
            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, booking_data['email']):
                return {
                    "success": False,
                    "booking_id": None,
                    "message": "Invalid email format. Please provide a valid email address."
                }
            
            # Validate phone format (basic validation)
            phone = booking_data['phone'].replace(' ', '').replace('-', '')
            if not phone.isdigit() or len(phone) < 10:
                return {
                    "success": False,
                    "booking_id": None,
                    "message": "Invalid phone number. Please provide a valid 10-digit phone number."
                }
            
            # Validate date format (YYYY-MM-DD)
            date_pattern = r'^\d{4}-\d{2}-\d{2}$'
            if not re.match(date_pattern, booking_data['date']):
                return {
                    "success": False,
                    "booking_id": None,
                    "message": "Invalid date format. Please enter date as YYYY-MM-DD."
                }
            
            # Check if customer exists
            customer = session.query(Customer).filter_by(email=booking_data['email']).first()
            
            if not customer:
                # Create new customer
                customer = Customer(
                    name=booking_data['name'],
                    email=booking_data['email'],
                    phone=booking_data['phone']
                )
                session.add(customer)
                session.flush()
            
            # Create booking
            booking = Booking(
                customer_id=customer.customer_id,
                booking_type=booking_data['booking_type'],
                date=booking_data['date'],
                time=booking_data['time'],
                status='confirmed'
            )
            session.add(booking)
            session.commit()
            
            booking_id = booking.id
            session.close()
            
            return {
                "success": True,
                "booking_id": booking_id,
                "message": "Booking saved successfully!"
            }
            
        except IntegrityError as e:
            session.rollback()
            session.close()
            return {
                "success": False,
                "booking_id": None,
                "message": "Database integrity error. This booking may already exist."
            }
        except Exception as e:
            session.rollback()
            session.close()
            return {
                "success": False,
                "booking_id": None,
                "message": f"Error saving booking: {str(e)}"
            }
    
    def email_tool(
        self,
        to_email: str,
        customer_name: str,
        booking_id: int,
        booking_type: str,
        date: str,
        time: str
    ) -> Dict[str, Any]:
        """
        Email Tool: Send booking confirmation email
        Input: email details
        Output: success/failure status
        """
        try:
            result = self.email_service.send_booking_confirmation(
                to_email=to_email,
                customer_name=customer_name,
                booking_id=booking_id,
                booking_type=booking_type,
                date=date,
                time=time
            )
            return result
        except Exception as e:
            return {
                "success": False,
                "message": f"Email tool error: {str(e)}"
            }

def validate_booking_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """Validate booking data format"""
    
    # Check required fields
    required = ['name', 'email', 'phone', 'booking_type', 'date', 'time']
    for field in required:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    
    # Validate email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, data['email']):
        return False, "Invalid email format"
    
    # Validate date
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(date_pattern, data['date']):
        return False, "Invalid date format. Please use YYYY-MM-DD"
    
    # Validate time
    time_pattern = r'^\d{2}:\d{2}$'
    if not re.match(time_pattern, data['time']):
        return False, "Invalid time format. Please use HH:MM"
    
    return True, "Valid"