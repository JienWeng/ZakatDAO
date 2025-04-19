from typing import Dict, Any
import json
from pathlib import Path
from datetime import datetime

TOKEN_DATA_FILE = Path('data/tokens.json')

def load_token_data() -> Dict[str, Any]:
    if not TOKEN_DATA_FILE.exists():
        return {'total_supply': 0, 'balances': {}, 'transactions': []}
    return json.loads(TOKEN_DATA_FILE.read_text())

def save_token_data(data: Dict[str, Any]) -> None:
    TOKEN_DATA_FILE.write_text(json.dumps(data, indent=2))

def award_tokens(donor_id: str, amount: int, reason: str) -> None:
    """Award ZGT tokens to a donor for various actions"""
    if not donor_id:
        return
        
    data = load_token_data()
    data['balances'][donor_id] = data['balances'].get(donor_id, 0) + amount
    data['total_supply'] += amount
    
    data['transactions'].append({
        'type': 'mint',
        'recipient': donor_id,
        'amount': amount,
        'reason': reason,
        'timestamp': datetime.now().isoformat()
    })
    
    save_token_data(data)

def get_reward_amount(action: str, amount: float = 0) -> int:
    """Calculate reward amount based on action"""
    rewards = {
        'donation': lambda x: min(int(x / 10), 100),  # 1 ZGT per 10 RM, max 100
        'vote': lambda x: 5,  # 5 ZGT per vote
        'proposal_approved': lambda x: 20,  # 20 ZGT for approved proposal
        'first_donation': lambda x: 50,  # 50 ZGT for first donation
    }
    
    calculator = rewards.get(action, lambda x: 0)
    return calculator(amount)
