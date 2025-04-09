import json
import csv
import os
from datetime import datetime

# Mock TNG merchant database
MOCK_TNG_MERCHANTS = {
    "M001": {"name": "Fresh Mart Grocery", "category": "Groceries"},
    "M002": {"name": "Family Store", "category": "Groceries"},
    "M003": {"name": "Daily Essentials", "category": "Groceries"}
}

def send_to_tng_wallet(recipient_id, amount, voucher_code):
    """Simulate sending money to TNG eWallet."""
    transaction = {
        'recipient_id': recipient_id,
        'amount': amount,
        'voucher_code': voucher_code,
        'timestamp': datetime.now().isoformat(),
        'status': 'SUCCESS',
        'tng_reference': f"TNG{datetime.now().strftime('%Y%m%d%H%M%S')}"
    }
    
    # Log TNG transaction
    log_file = 'data/tng_transactions.json'
    transactions = []
    
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            transactions = json.load(f)
    
    transactions.append(transaction)
    
    with open(log_file, 'w') as f:
        json.dump(transactions, f, indent=2)
    
    return transaction

def track_voucher_usage(voucher_code, recipient_id, merchant_id, amount_used, remarks=None):
    """Track how the voucher is used at merchants."""
    usage_file = 'data/usage.csv'
    file_exists = os.path.isfile(usage_file)
    
    usage_data = {
        'voucher_code': voucher_code,
        'recipient_id': recipient_id,
        'usage_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'merchant_id': merchant_id,
        'merchant_name': MOCK_TNG_MERCHANTS.get(merchant_id, {}).get('name', 'Unknown'),
        'merchant_category': MOCK_TNG_MERCHANTS.get(merchant_id, {}).get('category', 'Unknown'),
        'amount_used': amount_used,
        'remarks': remarks or 'Grocery purchase'
    }
    
    with open(usage_file, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=usage_data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(usage_data)
    
    return usage_data

def get_voucher_usage(voucher_code):
    """Get usage history for a specific voucher."""
    usage_file = 'data/usage.csv'
    if not os.path.exists(usage_file):
        return []
    
    usage_history = []
    with open(usage_file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['voucher_code'] == voucher_code:
                usage_history.append(row)
    
    return usage_history
