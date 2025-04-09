import csv
import os
import hashlib
import json
from datetime import datetime

def write_to_ledger(transaction_data):
    """Write a transaction to the blockchain-style ledger."""
    ledger_file = 'data/ledger.csv'
    file_exists = os.path.isfile(ledger_file)
    
    fieldnames = [
        'transaction_id', 'block_height', 'block_hash', 'prev_block_hash',
        'transaction_type', 'timestamp', 'amount', 'user', 'email',
        'notes', 'voucher_code', 'zakat_type_id', 'zakat_type_name',
        'recipient_id', 'disbursement_type', 'signatures'
    ]
    
    # Initialize transaction data
    transaction_data = {k: (transaction_data.get(k) or '') for k in fieldnames}
    
    # Get current block height
    current_height = 0
    prev_hash = hashlib.sha256("genesis".encode()).hexdigest()
    
    if file_exists:
        with open(ledger_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    height = int(row.get('block_height', '0') or '0')
                    current_height = max(current_height, height)
                    if row.get('block_hash'):
                        prev_hash = row['block_hash']
                except (ValueError, TypeError):
                    continue
    
    # Add blockchain metadata
    transaction_data['block_height'] = str(current_height + 1)
    transaction_data['prev_block_hash'] = prev_hash
    
    # Generate block hash
    block_data = f"{transaction_data['block_height']}{transaction_data['transaction_id']}{transaction_data['timestamp']}{transaction_data['amount']}{prev_hash}"
    transaction_data['block_hash'] = hashlib.sha256(block_data.encode()).hexdigest()
    
    # Add signatures
    transaction_data['signatures'] = json.dumps({
        'validator_1': hashlib.sha256(f"validator1{block_data}".encode()).hexdigest()[:16],
        'validator_2': hashlib.sha256(f"validator2{block_data}".encode()).hexdigest()[:16],
        'timestamp': datetime.now().isoformat()
    })
    
    # Write transaction
    with open(ledger_file, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(transaction_data)
