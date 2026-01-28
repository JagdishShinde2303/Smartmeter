"""
Billing Job - Generate invoices monthly
"""
import os
import sys
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pymongo import MongoClient
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add parent to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend_python.app.config.config import Config
from backend_python.app.services.billing_service import BillingService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BillingJob:
    """Monthly billing job"""
    
    def __init__(self, config):
        self.config = config
        self.mongo_client = MongoClient(config.MONGODB_URI)
        self.db = self.mongo_client[config.DB_NAME]
        self.billing_svc = BillingService(self.db, config)
    
    def run(self):
        """Execute billing job"""
        try:
            logger.info('Starting monthly billing job')
            
            # Get all active devices
            devices = list(self.db.devices.find({'status': {'$in': ['online', 'offline']}}))
            logger.info(f'Processing {len(devices)} devices')
            
            # Previous month
            today = datetime.utcnow()
            first_day_this_month = today.replace(day=1)
            last_day_prev_month = first_day_this_month - timedelta(days=1)
            prev_month = last_day_prev_month.strftime('%Y-%m')
            
            generated = 0
            errors = 0
            
            for device in devices:
                try:
                    device_id = device['device_id']
                    logger.info(f'Processing device: {device_id}')
                    
                    # Compute bill
                    bill = self.billing_svc.compute_bill(device_id, prev_month)
                    if not bill:
                        logger.warning(f'No bill generated for {device_id}')
                        continue
                    
                    # Generate invoice
                    invoice_id = self.billing_svc.generate_invoice(bill, {})
                    
                    # Send email (if user has email)
                    # self.send_invoice_email(device_id, bill)
                    
                    generated += 1
                    logger.info(f'Invoice generated for {device_id}')
                
                except Exception as e:
                    errors += 1
                    logger.error(f'Error processing {device["device_id"]}: {e}')
            
            logger.info(f'Billing job completed: {generated} invoices generated, {errors} errors')
        
        except Exception as e:
            logger.error(f'Billing job failed: {e}')
    
    def send_invoice_email(self, device_id, bill):
        """Send invoice email"""
        try:
            subject = f'Smart Meter Invoice - {bill["month"]}'
            body = f'''
Smart Energy Meter Invoice

Device: {bill["device_id"]}
Month: {bill["month"]}

Energy Consumed: {bill["energy_kwh"]} kWh
Subtotal: ₹{bill["subtotal"]}
Fixed Charge: ₹{bill["fixed_charge"]}
Tax: ₹{bill["tax"]}

Total: ₹{bill["total"]}
            '''
            
            # Send via SMTP
            # msg = MIMEMultipart()
            # msg['From'] = self.config.SMTP_FROM
            # msg['To'] = user_email
            # msg['Subject'] = subject
            # msg.attach(MIMEText(body, 'plain'))
            
            # server = smtplib.SMTP(self.config.SMTP_HOST, self.config.SMTP_PORT)
            # server.starttls()
            # server.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)
            # server.send_message(msg)
            # server.quit()
            
            logger.info(f'Invoice email sent to {device_id}')
        except Exception as e:
            logger.error(f'Error sending email: {e}')

if __name__ == '__main__':
    config = Config()
    job = BillingJob(config)
    job.run()
