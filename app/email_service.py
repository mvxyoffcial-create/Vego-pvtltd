import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from typing import List, Optional

class EmailService:
    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ):
        message = MIMEMultipart("alternative")
        message["From"] = f"{settings.FROM_NAME} <{settings.FROM_EMAIL}>"
        message["To"] = to_email
        message["Subject"] = subject
        
        if text_content:
            part1 = MIMEText(text_content, "plain")
            message.attach(part1)
        
        part2 = MIMEText(html_content, "html")
        message.attach(part2)
        
        try:
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=True
            )
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    @staticmethod
    async def send_verification_email(email: str, token: str, name: str):
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>Welcome to VegGo, {name}! 🥬</h2>
                <p>Thank you for signing up. Please verify your email address by clicking the button below:</p>
                <a href="{verification_link}" 
                   style="display: inline-block; padding: 12px 24px; background-color: #4CAF50; 
                          color: white; text-decoration: none; border-radius: 5px; margin: 20px 0;">
                    Verify Email
                </a>
                <p>Or copy this link: {verification_link}</p>
                <p>This link will expire in 24 hours.</p>
                <p>Best regards,<br>VegGo Team</p>
            </body>
        </html>
        """
        
        await EmailService.send_email(email, "Verify Your VegGo Account", html)
    
    @staticmethod
    async def send_order_confirmation_email(email: str, name: str, order_number: str, total: float):
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>Order Confirmed! 🎉</h2>
                <p>Hi {name},</p>
                <p>Your order has been confirmed successfully.</p>
                <h3>Order Details:</h3>
                <p><strong>Order Number:</strong> {order_number}</p>
                <p><strong>Total Amount:</strong> ₹{total:.2f}</p>
                <p>We'll notify you when your order is assigned to a delivery agent.</p>
                <p>Track your order in real-time from your dashboard.</p>
                <p>Best regards,<br>VegGo Team</p>
            </body>
        </html>
        """
        
        await EmailService.send_email(email, f"Order Confirmed - {order_number}", html)
    
    @staticmethod
    async def send_order_assigned_email(email: str, name: str, order_number: str, agent_name: str):
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>Order Assigned to Delivery Agent 🚴</h2>
                <p>Hi {name},</p>
                <p>Great news! Your order has been assigned to a delivery agent.</p>
                <h3>Order Details:</h3>
                <p><strong>Order Number:</strong> {order_number}</p>
                <p><strong>Delivery Agent:</strong> {agent_name}</p>
                <p>You can track your delivery agent's location in real-time from your dashboard.</p>
                <p>Best regards,<br>VegGo Team</p>
            </body>
        </html>
        """
        
        await EmailService.send_email(email, f"Order Assigned - {order_number}", html)
    
    @staticmethod
    async def send_order_status_email(email: str, name: str, order_number: str, status: str):
        status_messages = {
            "picked_up": "Your order has been picked up by the delivery agent! 📦",
            "in_transit": "Your order is on the way! 🚚",
            "delivered": "Your order has been delivered! ✅",
            "cancelled": "Your order has been cancelled. ❌"
        }
        
        message = status_messages.get(status, f"Your order status has been updated to: {status}")
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>Order Status Update</h2>
                <p>Hi {name},</p>
                <p>{message}</p>
                <p><strong>Order Number:</strong> {order_number}</p>
                <p>Best regards,<br>VegGo Team</p>
            </body>
        </html>
        """
        
        await EmailService.send_email(email, f"Order Update - {order_number}", html)
    
    @staticmethod
    async def send_order_cancelled_email(email: str, name: str, order_number: str, reason: str = "User request"):
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>Order Cancelled</h2>
                <p>Hi {name},</p>
                <p>Your order has been cancelled.</p>
                <p><strong>Order Number:</strong> {order_number}</p>
                <p><strong>Reason:</strong> {reason}</p>
                <p>If you didn't request this cancellation, please contact support.</p>
                <p>Best regards,<br>VegGo Team</p>
            </body>
        </html>
        """
        
        await EmailService.send_email(email, f"Order Cancelled - {order_number}", html)
    
    @staticmethod
    async def send_agent_approval_email(email: str, name: str, approved: bool):
        if approved:
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2>Congratulations! 🎉</h2>
                    <p>Hi {name},</p>
                    <p>Your agent account has been approved by the admin.</p>
                    <p>You can now log in and start accepting delivery orders.</p>
                    <p>Best regards,<br>VegGo Team</p>
                </body>
            </html>
            """
            subject = "Agent Account Approved"
        else:
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2>Account Status Update</h2>
                    <p>Hi {name},</p>
                    <p>Unfortunately, your agent account application was not approved at this time.</p>
                    <p>Please contact support for more information.</p>
                    <p>Best regards,<br>VegGo Team</p>
                </body>
            </html>
            """
            subject = "Agent Account Status"
        
        await EmailService.send_email(email, subject, html)
    
    @staticmethod
    async def send_password_reset_email(email: str, token: str, name: str):
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>Password Reset Request</h2>
                <p>Hi {name},</p>
                <p>You requested to reset your password. Click the button below to reset it:</p>
                <a href="{reset_link}" 
                   style="display: inline-block; padding: 12px 24px; background-color: #f44336; 
                          color: white; text-decoration: none; border-radius: 5px; margin: 20px 0;">
                    Reset Password
                </a>
                <p>Or copy this link: {reset_link}</p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <p>Best regards,<br>VegGo Team</p>
            </body>
        </html>
        """
        
        await EmailService.send_email(email, "Password Reset Request", html)

email_service = EmailService()
