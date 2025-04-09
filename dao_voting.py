import json
import os
from datetime import datetime, timedelta
import hashlib

class DaoVoting:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.proposals_file = os.path.join(data_dir, 'proposals.json')
        self.allocation_file = os.path.join(data_dir, 'allocations.json')
        self.min_votes_required = 3  # Minimum votes needed
        self.voting_duration = timedelta(hours=24)  # 24-hour voting window
        self.authority_weight = 0.5  # 50% weight for authority votes
        self.donor_weight = 0.5  # 50% weight for donor votes
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize proposals file if it doesn't exist
        if not os.path.exists(self.proposals_file):
            self._save_proposals({})
        
        self._init_allocations()
    
    def _init_allocations(self):
        """Initialize default allocation policies."""
        if not os.path.exists(self.allocation_file):
            default_allocations = {
                'asnaf': {
                    'fakir': {'percentage': 25, 'categories': ['groceries', 'medical', 'education']},
                    'miskin': {'percentage': 25, 'categories': ['groceries', 'medical', 'education']},
                    'amil': {'percentage': 12.5, 'categories': ['operational']},
                    'muallaf': {'percentage': 12.5, 'categories': ['education', 'religious']},
                    'riqab': {'percentage': 6.25, 'categories': ['education', 'skills']},
                    'gharimin': {'percentage': 6.25, 'categories': ['debt_relief']},
                    'fisabilillah': {'percentage': 6.25, 'categories': ['religious', 'education']},
                    'ibnu_sabil': {'percentage': 6.25, 'categories': ['travel', 'emergency']}
                },
                'usage_categories': {
                    'groceries': {'priority': 1, 'description': 'Basic food and household items'},
                    'medical': {'priority': 2, 'description': 'Healthcare and medicine'},
                    'education': {'priority': 3, 'description': 'School fees and supplies'},
                    'skills': {'priority': 4, 'description': 'Vocational training'},
                    'religious': {'priority': 5, 'description': 'Religious education'},
                    'operational': {'priority': 6, 'description': 'Administrative costs'},
                    'debt_relief': {'priority': 7, 'description': 'Debt assistance'},
                    'travel': {'priority': 8, 'description': 'Travel assistance'},
                    'emergency': {'priority': 9, 'description': 'Emergency aid'}
                }
            }
            self._save_allocations(default_allocations)
    
    def create_proposal(self, disbursement_data, created_by):
        """Create a new disbursement proposal."""
        proposals = self._load_proposals()
        
        # Generate proposal ID
        proposal_id = hashlib.sha256(
            f"{disbursement_data['amount']}{disbursement_data['recipient_id']}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        proposal = {
            'id': proposal_id,
            'disbursement_data': disbursement_data,
            'created_by': created_by,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + self.voting_duration).isoformat(),
            'status': 'active',
            'votes': {
                'authorities': {},  # Admin votes
                'donors': {}       # Donor votes
            },
            'final_decision': None
        }
        
        proposals[proposal_id] = proposal
        self._save_proposals(proposals)
        return proposal_id
    
    def create_allocation_proposal(self, allocation_type, changes, created_by):
        """Create a proposal to change allocation percentages."""
        proposal_id = hashlib.sha256(
            f"allocation_{allocation_type}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        current_allocations = self._load_allocations()
        
        # Validate total = 100% for asnaf allocations
        if allocation_type == 'asnaf':
            total_percentage = sum(data['percentage'] for data in changes.values())
            if abs(total_percentage - 100) > 0.01:  # Allow small rounding errors
                raise ValueError(f"Asnaf allocations must total 100% (current: {total_percentage}%)")
        
        proposal = {
            'id': proposal_id,
            'type': 'allocation',
            'allocation_type': allocation_type,  # 'asnaf' or 'category'
            'current_state': current_allocations[allocation_type],
            'proposed_changes': changes,
            'created_by': created_by,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + self.voting_duration).isoformat(),
            'status': 'active',
            'votes': {
                'authorities': {},
                'donors': {}
            }
        }
        
        proposals = self._load_proposals()
        proposals[proposal_id] = proposal
        self._save_proposals(proposals)
        return proposal_id
    
    def vote(self, proposal_id, voter_id, vote, voter_type='donor', voter_weight=1.0):
        """Record a vote on a proposal."""
        proposals = self._load_proposals()
        if proposal_id not in proposals:
            raise ValueError("Proposal not found")
        
        proposal = proposals[proposal_id]
        if proposal['status'] != 'active':
            raise ValueError("Voting has ended for this proposal")
        
        if datetime.now() > datetime.fromisoformat(proposal['expires_at']):
            proposal['status'] = 'expired'
            self._save_proposals(proposals)
            raise ValueError("Voting period has expired")
        
        # Record vote
        vote_data = {
            'vote': vote,
            'timestamp': datetime.now().isoformat(),
            'weight': voter_weight
        }
        
        if voter_type == 'authority':
            proposal['votes']['authorities'][voter_id] = vote_data
        else:
            proposal['votes']['donors'][voter_id] = vote_data
        
        # Check if we have enough votes for a decision
        self._check_consensus(proposal)
        
        self._save_proposals(proposals)
        return proposal['status']
    
    def _check_consensus(self, proposal):
        """Check if consensus has been reached."""
        authority_votes = proposal['votes']['authorities']
        donor_votes = proposal['votes']['donors']
        
        total_votes = len(authority_votes) + len(donor_votes)
        if total_votes < self.min_votes_required:
            return
        
        # Calculate weighted votes
        authority_approve = sum(1 for v in authority_votes.values() if v['vote'] == 'approve')
        authority_reject = len(authority_votes) - authority_approve
        
        donor_approve = sum(1 for v in donor_votes.values() if v['vote'] == 'approve')
        donor_reject = len(donor_votes) - donor_approve
        
        # Calculate approval percentages
        authority_approval = authority_approve / max(len(authority_votes), 1)
        donor_approval = donor_approve / max(len(donor_votes), 1)
        
        # Calculate final weighted approval
        weighted_approval = (
            authority_approval * self.authority_weight +
            donor_approval * self.donor_weight
        )
        
        # Decision threshold is 60%
        if weighted_approval >= 0.6:
            proposal['status'] = 'approved'
            proposal['final_decision'] = 'approved'
        elif total_votes >= self.min_votes_required * 2:  # Double minimum for rejection
            proposal['status'] = 'rejected'
            proposal['final_decision'] = 'rejected'
        
        if proposal['status'] == 'approved' and proposal.get('type') == 'allocation':
            # Update allocation policies if approved
            current = self._load_allocations()
            allocation_type = proposal['allocation_type']
            if allocation_type in current:
                current[allocation_type].update(proposal['proposed_changes'])
                self._save_allocations(current)
    
    def get_proposal(self, proposal_id):
        """Get proposal details."""
        proposals = self._load_proposals()
        return proposals.get(proposal_id)
    
    def get_active_proposals(self):
        """Get all active proposals."""
        proposals = self._load_proposals()
        return {
            k: v for k, v in proposals.items() 
            if v['status'] == 'active' and
            datetime.now() < datetime.fromisoformat(v['expires_at'])
        }
    
    def get_all_proposals(self):
        """Get all proposals including expired and completed ones."""
        proposals = self._load_proposals()
        
        # Update status of expired proposals
        now = datetime.now()
        for proposal in proposals.values():
            if proposal['status'] == 'active' and now > datetime.fromisoformat(proposal['expires_at']):
                proposal['status'] = 'expired'
        
        self._save_proposals(proposals)
        return proposals
    
    def get_current_allocations(self):
        """Get current allocation policies."""
        return self._load_allocations()
    
    def _load_proposals(self):
        """Load proposals from file."""
        if not os.path.exists(self.proposals_file):
            return {}
        with open(self.proposals_file, 'r') as f:
            return json.load(f)
    
    def _save_proposals(self, proposals):
        """Save proposals to file."""
        with open(self.proposals_file, 'w') as f:
            json.dump(proposals, f, indent=2)
    
    def _load_allocations(self):
        """Load allocation policies from file."""
        if not os.path.exists(self.allocation_file):
            self._init_allocations()
        with open(self.allocation_file, 'r') as f:
            return json.load(f)
    
    def _save_allocations(self, allocations):
        """Save allocation policies to file."""
        with open(self.allocation_file, 'w') as f:
            json.dump(allocations, f, indent=2)
