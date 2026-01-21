class EmailService:
    """Mock email service for demo purposes"""

    def send_booking_confirmation(
        self,
        to_email: str,
        customer_name: str,
        booking_id: int,
        booking_type: str,
        date: str,
        time: str
    ) -> dict:
        return {
            "success": True,
            "message": "📧 Email notification simulated (email service disabled for demo)."
        }
