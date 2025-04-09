import json
import csv
import os
from datetime import datetime, timedelta
import hashlib
import uuid
import logging
from ledger_utils import write_to_ledger
from config import ZAKAT_TYPES, ZAKAT_TYPES_BY_ID

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_recipients(filepath='data/recipients.json'):
    """Load recipient profiles with priority scores."""
    try:
        if not os.path.exists(filepath):
            # Create default recipients structure
            recipients = [
                {
                    "id": "RCP001",
                    "name": "Recipient 1 (Fakir)",
                    "category": "fakir",
                    "category_name": "Fakir",
                    "family_size": 4,
                    "monthly_income": 1200,
                    "priority_base": 8.5,
                    "last_disbursement": None
                },
                {
                    "id": "RCP002",
                    "name": "Recipient 2 (Miskin)",
                    "category": "miskin",
                    "category_name": "Miskin",
                    "family_size": 3,
                    "monthly_income": 1500,
                    "priority_base": 6.5,
                    "last_disbursement": None
                },
                {
                    "id": "RCP003",
                    "name": "Recipient 3 (Riqab)",
                    "category": "riqab",
                    "category_name": "Riqab",
                    "family_size": 2,
                    "monthly_income": 1800,
                    "priority_base": 4.5,
                    "last_disbursement": None
                }
            ]
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(recipients, f, indent=2)
            return recipients
        
        with open(filepath, 'r') as f:
            data = json.load(f)
            # Handle both array and object with recipients key
            if isinstance(data, dict):
                recipients = data.get('recipients', [])
            else:
                recipients = data
            
            # Validate each recipient has required fields
            validated = []
            for r in recipients:
                if isinstance(r, dict) and all(k in r for k in ['id', 'name', 'category_name']):
                    validated.append(r)
            
            return validated
            
    except Exception as e:
        logger.error(f"Error loading recipients: {e}")
        return []

def update_recipient_disbursement(recipient_id, amount, filepath='data/recipients.json'):
    """Update recipient's last disbursement record."""
    try:
        recipients = load_recipients()
        for recipient in recipients:
            if recipient['id'] == recipient_id:
                recipient['last_disbursement'] = datetime.now().isoformat()
                recipient['total_received'] = recipient.get('total_received', 0) + amount
                recipient['disbursement_count'] = recipient.get('disbursement_count', 0) + 1
                break
        
        # Save updated recipients
        with open(filepath, 'w') as f:
            json.dump(recipients, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error updating recipient disbursement: {e}")

def track_recipient_disbursement(recipient_id, amount, zakat_type_id, voucher_code, priority_score):
    """Track recipient disbursement and update eligibility."""
    filepath = 'data/disbursements.csv'
    fieldnames = ['recipient_id', 'timestamp', 'amount', 'zakat_type_id', 
                 'voucher_code', 'priority_score', 'next_eligible_date']
    
    # Create file if not exists
    if not os.path.exists(filepath):
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
    
    # Add new disbursement record
    now = datetime.now()
    next_eligible = now + timedelta(days=30)  # 30-day cooling period
    
    with open(filepath, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow({
            'recipient_id': recipient_id,
            'timestamp': now.strftime("%Y-%m-%d %H:%M:%S"),
            'amount': amount,
            'zakat_type_id': zakat_type_id,
            'voucher_code': voucher_code,
            'priority_score': priority_score,
            'next_eligible_date': next_eligible.strftime("%Y-%m-%d %H:%M:%S")
        })

def check_recipient_eligibility(recipient_id):
    """Check if recipient is eligible for new disbursement."""
    filepath = 'data/disbursements.csv'
    if not os.path.exists(filepath):
        return True, None
    
    try:
        with open(filepath, 'r', newline='') as f:
            reader = csv.DictReader(f)
            recipient_records = [
                row for row in reader 
                if row['recipient_id'] == recipient_id
            ]
            
            if not recipient_records:
                return True, None
            
            # Get latest disbursement
            latest = max(recipient_records, key=lambda x: x['timestamp'])
            next_eligible = datetime.strptime(
                latest['next_eligible_date'], 
                "%Y-%m-%d %H:%M:%S"
            )
            
            if datetime.now() < next_eligible:
                return False, next_eligible
            
            return True, None
            
    except Exception as e:
        logger.error(f"Error checking eligibility: {e}")
        return True, None  # Default to eligible if error

def calculate_priority_score(recipient, available_funds):
    """Calculate recipient priority score with more lenient rules."""
    try:
        # Base score (using higher default)
        base_score = float(recipient.get('priority_base', 6.0))  # Increased default
        
        # More generous category weights
        category_weights = {
            'fakir': 1.8,
            'miskin': 1.6,
            'riqab': 1.4,
            'gharimin': 1.3,
            'muallaf': 1.2,
            'fisabilillah': 1.1,
            'ibnu sabil': 1.3
        }
        
        # Apply category weight (default 1.0 if category not found)
        category = recipient.get('category', '').lower()
        score = base_score * category_weights.get(category, 1.0)
        
        # More generous family size bonus (0.8 points per dependent)
        family_size = int(recipient.get('family_size', 1))
        score += min(family_size * 0.8, 3.0)  # Increased cap to 3.0
        
        # More generous income consideration
        monthly_income = float(recipient.get('monthly_income', 0))
        if monthly_income < 2000:      # Increased threshold
            score *= 1.4               # Reduced multiplier
        elif monthly_income < 3000:
            score *= 1.2
        elif monthly_income < 4000:
            score *= 1.1
        
        # Eligibility check with reduced penalty
        eligible, next_date = check_recipient_eligibility(recipient['id'])
        if not eligible:
            score *= 0.3  # Reduced penalty (was 0.1)
        
        return min(round(score, 2), 10.0)
        
    except Exception as e:
        logger.error(f"Error calculating priority score: {e}")
        return 5.0  # Default score instead of 0

def read_available_funds(ledger_file='data/ledger.csv'):
    """Calculate available funds from ledger."""
    if not os.path.exists(ledger_file):
        return {'total_available': 0.0, 'by_type': {}}
    
    funds = {'total_available': 0.0, 'by_type': {}}
    
    with open(ledger_file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                amount = float(row.get('amount', 0))
                zakat_type_id = int(row.get('zakat_type_id', 0) or 0)
                
                if row['transaction_type'] == 'IN':
                    funds['total_available'] += amount
                    if zakat_type_id:
                        funds['by_type'][zakat_type_id] = funds['by_type'].get(zakat_type_id, 0) + amount
                elif row['transaction_type'] == 'OUT':
                    funds['total_available'] -= amount
                    if zakat_type_id:
                        funds['by_type'][zakat_type_id] = funds['by_type'].get(zakat_type_id, 0) - amount
            except (ValueError, TypeError):
                continue
    
    return funds

def select_voucher_for_disbursement(amount, zakat_type_id=None):
    """Select best voucher(s) to disburse from based on FIFO."""
    ledger_file = 'data/ledger.csv'
    vouchers = {}
    
    with open(ledger_file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            voucher_code = row.get('voucher_code')
            if not voucher_code:
                continue
                
            if voucher_code not in vouchers:
                vouchers[voucher_code] = {
                    'total_donated': 0,
                    'total_disbursed': 0,
                    'zakat_type_id': row.get('zakat_type_id'),
                    'block_hash': row.get('block_hash'),
                    'timestamp': row.get('timestamp')
                }
            
            try:
                tx_amount = float(row.get('amount', 0))
                if row['transaction_type'] == 'IN':
                    vouchers[voucher_code]['total_donated'] += tx_amount
                else:
                    vouchers[voucher_code]['total_disbursed'] += tx_amount
            except (ValueError, TypeError):
                continue
    
    # Filter available vouchers
    available_vouchers = []
    for code, data in vouchers.items():
        remaining = data['total_donated'] - data['total_disbursed']
        if remaining >= amount:
            if not zakat_type_id or str(data['zakat_type_id']) == str(zakat_type_id):
                available_vouchers.append({
                    'voucher_code': code,
                    'remaining': remaining,
                    'block_hash': data['block_hash'],
                    'timestamp': data['timestamp']
                })
    
    # Sort by timestamp (oldest first)
    available_vouchers.sort(key=lambda x: x['timestamp'])
    return available_vouchers[0] if available_vouchers else None

def ai_disburse_funds(max_disbursement=None, simulation=True):
    """AI-powered fund disbursement with voucher tracking."""
    try:
        # Load available funds
        available_funds = read_available_funds()
        total_available = available_funds['total_available']
        if total_available <= 0:
            return {'error': 'No funds available for disbursement'}

        # Set maximum disbursement
        if max_disbursement is None:
            max_disbursement = total_available * 0.9
        else:
            max_disbursement = min(float(max_disbursement), total_available)

        # Load and score recipients
        recipients = load_recipients()
        scored_recipients = []
        
        for recipient in recipients:
            score = calculate_priority_score(recipient, available_funds)
            scored_recipients.append({
                **recipient,
                'priority_score': score
            })
        
        # Sort by priority score
        scored_recipients.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Allocate funds
        disbursements = []
        total_allocated = 0
        min_amount = 30.0
        
        for recipient in scored_recipients:
            if total_allocated >= max_disbursement:
                break
            
            # Calculate disbursement amount
            score_ratio = recipient['priority_score'] / 10.0
            base_amount = min(
                1500 * score_ratio,
                max_disbursement - total_allocated,
                3000
            )
            
            if base_amount >= min_amount:
                amount = round(base_amount, 2)
                
                # Find suitable voucher for disbursement
                voucher = select_voucher_for_disbursement(amount)
                if not voucher:
                    continue
                
                disbursement = {
                    'recipient_id': recipient['id'],
                    'name': recipient['name'],
                    'amount': amount,
                    'priority_score': recipient['priority_score'],
                    'category': recipient['category_name'],
                    'voucher_code': voucher['voucher_code'],
                    'block_hash': voucher['block_hash']
                }
                
                disbursements.append(disbursement)
                total_allocated += amount
                
                # Record disbursement if not simulation
                if not simulation:
                    # Create ledger transaction
                    transaction_data = {
                        'transaction_id': f"tx{uuid.uuid4().hex[:8]}",
                        'transaction_type': 'OUT',
                        'amount': amount,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'user': recipient['name'],
                        'email': '',
                        'notes': f"AI Disbursement to {recipient['category_name']}",
                        'voucher_code': voucher['voucher_code'],
                        'zakat_type_id': 1,  # Default to general fund
                        'zakat_type_name': 'Zakat Pendapatan',
                        'recipient_id': recipient['id'],
                        'disbursement_type': 'AI',
                        'prev_block_hash': voucher['block_hash']
                    }
                    
                    # Write to ledger
                    write_to_ledger(transaction_data)
                    
                    # Update recipient record and track disbursement
                    update_recipient_disbursement(
                        recipient_id=recipient['id'],
                        amount=amount
                    )
                    
                    track_recipient_disbursement(
                        recipient_id=recipient['id'],
                        amount=amount,
                        zakat_type_id=1,
                        voucher_code=voucher['voucher_code'],
                        priority_score=recipient['priority_score']
                    )
        
        result = {
            'success': True,
            'disbursements': disbursements,
            'total_amount': total_allocated,
            'recipient_count': len(disbursements)
        }
        
        logger.info(f"AI Disbursement {'simulation' if simulation else 'completed'}: "
                   f"{len(disbursements)} disbursements totaling RM{total_allocated:.2f}")
        
        return result

    except Exception as e:
        logger.error(f"Error in AI disbursement: {e}")
        return {'error': str(e)}
