import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD

class EmailService:
    """Email service for sending booking confirmations"""
    
    def __init__(self):
        self.host = EMAIL_HOST
        self.port = EMAIL_PORT
        self.user = EMAIL_USER
        self.password = EMAIL_PASSWORD
    
    def send_booking_confirmation(
        self,
        to_email: str,
        customer_name: str,
        booking_id: int,
        booking_type: str,
        date: str,
        time: str
    ) -> dict:
        """Send booking confirmation email"""
        
        if not self.user or not self.password:
            return {
                "success": False,
                "message": "Email configuration not set up. Booking saved but email not sent."
            }
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Booking Confirmation - {booking_type}"
            msg['From'] = self.user
            msg['To'] = to_email
            
            # Email body
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                        <h2 style="color: #4CAF50; text-align: center;">Booking Confirmed! ✓</h2>
                        
                        <p>Dear <strong>{customer_name}</strong>,</p>
                        
                        <p>Your booking has been successfully confirmed. Here are your booking details:</p>
                        
                        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <p><strong>Booking ID:</strong> #{booking_id}</p>
                            <p><strong>Service:</strong> {booking_type}</p>
                            <p><strong>Date:</strong> {date}</p>
                            <p><strong>Time:</strong> {time}</p>
                            <p><strong>Status:</strong> <span style="color: #4CAF50;">Confirmed</span></p>
                        </div>
                        
                        <p><strong>Important Notes:</strong></p>
                        <ul>
                            <li>Please arrive 10 minutes before your scheduled time</li>
                            <li>Bring a valid ID for verification</li>
                            <li>For cancellations, please contact us 24 hours in advance</li>
                        </ul>
                        
                        <p>We look forward to serving you!</p>
                        
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                        
                        <p style="font-size: 12px; color: #777; text-align: center;">
                            This is an automated message. Please do not reply to this email.<br>
                            © 2026 Glamour Salon. All rights reserved.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            # Attach HTML body
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
            
            return {
                "success": True,
                "message": "Confirmation email sent successfully!"
            }
            
        except smtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "message": "Email authentication failed. Booking saved but email not sent."
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Email could not be sent: {str(e)}. Booking was saved."
            }