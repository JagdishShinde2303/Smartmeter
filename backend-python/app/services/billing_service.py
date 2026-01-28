"""
Billing Service - tariff calculations and invoice generation
"""
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz

logger = logging.getLogger(__name__)

class BillingService:
    """Handles billing calculations and invoice generation"""
    
    def __init__(self, db, config):
        self.db = db
        self.config = config
    
    def compute_bill(self, device_id, year_month):
        """
        Compute monthly bill for a device
        Args:
            device_id: Meter device ID
            year_month: String in format 'YYYY-MM'
        Returns:
            Bill dictionary with charges breakdown
        """
        try:
            # Parse month
            year, month = year_month.split('-')
            year, month = int(year), int(month)
            
            # Get date range for the month
            start_date = datetime(year, month, 1, tzinfo=pytz.UTC)
            if month == 12:
                end_date = datetime(year + 1, 1, 1, tzinfo=pytz.UTC)
            else:
                end_date = datetime(year, month + 1, 1, tzinfo=pytz.UTC)
            
            # Query energy readings for the month
            readings = list(self.db.meter_readings.find({
                'device_id': device_id,
                'timestamp': {'$gte': start_date, '$lt': end_date}
            }).sort('timestamp', 1))
            
            if not readings:
                logger.warning(f'No readings found for {device_id} in {year_month}')
                return None
            
            # Calculate total energy (use last reading's accumulated kWh)
            total_energy = readings[-1].get('energy_kwh', 0) - readings[0].get('energy_kwh', 0)
            total_energy = max(total_energy, 0)  # Avoid negative values
            
            # Get tariff config
            tariff = self.db.tariffs.find_one({'name': 'default'})
            if not tariff:
                logger.error('Default tariff not found')
                return None
            
            # Calculate charges by slab
            slabs_breakdown = []
            remaining_units = total_energy
            subtotal = 0
            
            for slab in tariff['slabs']:
                slab_range = slab['range']
                rate = slab['rate']
                
                # Parse slab range
                if '+' in slab_range:
                    slab_start = int(slab_range.replace('+', ''))
                    slab_end = float('inf')
                else:
                    slab_start, slab_end = map(int, slab_range.split('-'))
                
                # Calculate units in this slab
                if remaining_units > 0:
                    slab_size = slab_end - slab_start if slab_end != float('inf') else remaining_units
                    units_in_slab = min(remaining_units, slab_size)
                    charge = units_in_slab * rate
                    
                    slabs_breakdown.append({
                        'slab': slab_range,
                        'units': round(units_in_slab, 2),
                        'rate': rate,
                        'charge': round(charge, 2)
                    })
                    
                    subtotal += charge
                    remaining_units -= units_in_slab
            
            # Apply fixed charge and tax
            fixed_charge = tariff.get('fixed_charge', 0)
            tax_rate = tariff.get('tax_rate', 0)
            
            total_before_tax = subtotal + fixed_charge
            tax_amount = total_before_tax * tax_rate
            total_bill = total_before_tax + tax_amount
            
            # Ensure minimum bill
            minimum_bill = tariff.get('minimum_bill', fixed_charge)
            total_bill = max(total_bill, minimum_bill)
            
            bill = {
                'device_id': device_id,
                'month': year_month,
                'energy_kwh': round(total_energy, 2),
                'slabs': slabs_breakdown,
                'subtotal': round(subtotal, 2),
                'fixed_charge': round(fixed_charge, 2),
                'tax': round(tax_amount, 2),
                'total': round(total_bill, 2),
                'currency': tariff.get('currency', 'INR'),
                'status': 'issued',
                'created_at': datetime.utcnow()
            }
            
            return bill
        
        except Exception as e:
            logger.error(f'Error computing bill: {e}')
            return None
    
    def generate_invoice(self, bill_data, user_info):
        """
        Generate and save invoice to database
        Args:
            bill_data: Bill dictionary from compute_bill()
            user_info: User details (email, name, etc.)
        Returns:
            Invoice ID
        """
        try:
            invoice = {
                'device_id': bill_data['device_id'],
                'month': bill_data['month'],
                'energy_kwh': bill_data['energy_kwh'],
                'slabs': bill_data['slabs'],
                'subtotal': bill_data['subtotal'],
                'fixed_charge': bill_data['fixed_charge'],
                'tax': bill_data['tax'],
                'total': bill_data['total'],
                'currency': bill_data['currency'],
                'status': 'issued',
                'email_sent': False,
                'created_at': datetime.utcnow(),
                'due_date': datetime.utcnow() + timedelta(days=15),
                'paid_date': None
            }
            
            result = self.db.invoices.insert_one(invoice)
            logger.info(f'Invoice created: {result.inserted_id}')
            return str(result.inserted_id)
        
        except Exception as e:
            logger.error(f'Error generating invoice: {e}')
            return None
    
    def get_invoices(self, device_id, limit=12):
        """Get list of invoices for a device"""
        try:
            invoices = list(self.db.invoices.find(
                {'device_id': device_id}
            ).sort('month', -1).limit(limit))
            
            return invoices
        except Exception as e:
            logger.error(f'Error fetching invoices: {e}')
            return []
