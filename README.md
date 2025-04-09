# Zakat DAO Platform

A blockchain-inspired platform for managing and distributing Zakat funds with transparency and efficiency.

## Project Overview

This platform implements a transparent Zakat management system with:
- Blockchain-style immutable ledger
- TNG eWallet integration for disbursements
- AI-powered fund distribution
- QR code enabled vouchers
- Real-time usage tracking

## Project Structure

```
GiveNGo/
├── app.py                 # Main Flask application
├── ai_disbursement.py    # AI-powered fund distribution logic
├── tng_integration.py    # Touch 'n Go eWallet integration
├── data/                 # Data storage directory
│   ├── ledger.csv       # Blockchain-style transaction ledger
│   ├── usage.csv        # Voucher usage tracking
│   └── recipients.json  # Recipient information database
├── static/              # Static assets
│   └── mosque.png      # Hero image for landing page
├── templates/           # HTML templates
│   ├── admin_dashboard.html
│   ├── admin_ai_disbursement.html
│   ├── admin_login.html
│   ├── admin_recipients.html
│   ├── confirmation.html
│   ├── disburse_form.html
│   ├── donate_form.html
│   ├── index.html
│   ├── ledger.html
│   ├── voucher_details.html
│   └── voucher_not_found.html
├── requirements.txt     # Python dependencies
└── TROUBLESHOOTING.md  # Troubleshooting guide
```

## Features

### 1. Blockchain-Style Ledger
- Immutable transaction history
- Cryptographic hash linking
- Multi-signature validation
- Real-time integrity verification

### 2. TNG eWallet Integration
- Direct disbursement to recipient wallets
- Grocery-specific vouchers
- Real-time transaction tracking
- Usage monitoring at partner merchants

### 3. AI-Powered Distribution
- Need-based allocation
- Priority scoring system
- Multi-factor analysis
- Automated disbursement recommendations

### 4. Security Features
- Hash-based integrity checks
- Multi-signature validation
- Role-based access control
- Audit trail for all actions

## Setup Instructions

1. Clone and setup environment:
```bash
git clone https://github.com/yourusername/GiveNGo.git
cd GiveNGo
python -m venv venv
source venv/bin/activate  # For Unix/macOS
venv\Scripts\activate     # For Windows
```

2. Install dependencies:
```bash
chmod +x install_dependencies.sh
./install_dependencies.sh
```

3. Initialize data directory:
```bash
mkdir -p data static
touch data/ledger.csv data/usage.csv
```

## Usage Guide

### Donation Flow
1. Access donation form: `/donate`
2. Fill required details
3. Receive unique voucher
4. Track status in ledger

### Disbursement Flow
1. Admin login: `/admin`
2. Review available funds
3. Choose disbursement method:
   - Manual: `/disburse`
   - AI-powered: `/admin/ai-disbursement`
4. Monitor transactions

### Voucher Usage
1. Recipient receives TNG voucher
2. Uses at partner merchants
3. Transactions logged in `usage.csv`
4. View usage history: `/voucher/<code>/usage`

## API Endpoints

### Public APIs
```
GET /api/ledger.json
- View all transactions
- Filter by type, date, user

GET /voucher/<code>
- Get voucher details
- View usage history
```

### Admin APIs
```
POST /api/disburse
- Disburse funds
- Requires admin auth
- Accepts: recipient_id, amount, zakat_type_id

GET /api/verify-chain
- Verify ledger integrity
- Returns validation status
```

## URL Guide

### Public Pages
```
/ - Home page
/donate - Donation form
/ledger - Public transaction ledger
/voucher/<code> - View specific voucher details
/voucher/<code>/usage - View voucher usage at merchants
```

### Admin Interface
```
/admin - Admin dashboard
/admin/login - Admin login page
/admin/logout - Admin logout
/admin/recipients - Manage recipients
/admin/ai-disbursement - AI-powered disbursement interface
```

### DAO Voting System
```
/proposal/<id> - View disbursement proposal details
/proposal/<id>/vote - Cast vote on proposal (requires auth)
/dao - DAO governance dashboard
/dao/proposals - View all proposals
/dao/allocations - View current allocation policies
/dao/allocations/propose - Propose new allocation policy (admin only)
/dao/vote/<id> - Cast vote on proposal
```

### Allocation Policies
```
Asnaf Distribution:
- Fakir: 25% (groceries, medical, education)
- Miskin: 25% (groceries, medical, education) 
- Amil: 12.5% (operational)
- Muallaf: 12.5% (education, religious)
- Riqab: 6.25% (education, skills)
- Gharimin: 6.25% (debt_relief)
- Fisabilillah: 6.25% (religious, education)
- Ibnu Sabil: 6.25% (travel, emergency)

Usage Categories:
- Groceries (Priority 1)
- Medical (Priority 2)
- Education (Priority 3)
- Skills Training (Priority 4)
- Religious Education (Priority 5)
- Operational Costs (Priority 6)
- Debt Relief (Priority 7)
- Travel Assistance (Priority 8)
- Emergency Aid (Priority 9)
```

### DAO Governance
- Proposal creation (admin)
- Two types of proposals:
  1. Disbursement proposals
  2. Allocation policy proposals
- Voting rights:
  - Authorities: 50% weight
  - Donors: 50% collective weight
  - Minimum 3 votes required
  - 24-hour voting window
  - 60% approval threshold

### Allocation Voting
1. Admin creates proposal at `/dao/allocations/propose`
2. Proposal includes:
   - Asnaf percentage changes
   - Category assignments
   - Usage priorities
3. Voting process:
   - 24-hour window
   - Both donors and authorities vote
   - Requires 60% weighted approval
4. Implementation:
   - Auto-executes on approval
   - Updates allocation policy
   - Affects future disbursements

### Disbursement Flow
```
/disburse - Manual disbursement form (requires admin)
/disbursement-confirmation - Confirmation page after disbursement
```

### API Endpoints
```
GET /api/ledger.json
    - View all transactions
    - Query params:
        - type: IN/OUT
        - user: filter by user
        - voucher: filter by voucher code
        - start_date: filter from date
        - end_date: filter to date

POST /api/disburse (requires admin)
    - Disburse funds
    - Payload:
        - recipient_id: string
        - amount: float
        - zakat_type_id: int

GET /api/verify-chain
    - Verify ledger integrity
    - Returns validation status and latest block
```

### File Downloads
```
/download-voucher/<code> - Download voucher QR code image
```

## URL Access Control

### Public Access
- Home page (/)
- Donation form (/donate)
- Public ledger (/ledger)
- Voucher details (/voucher/*)

### Donor Access
- Proposal voting (/proposal/*/vote)
- Usage tracking (/voucher/*/usage)

### Admin Access
- Admin dashboard (/admin)
- Recipient management (/admin/recipients)
- Manual disbursement (/disburse)
- AI disbursement (/admin/ai-disbursement)
- API endpoints (/api/disburse)

### DAO Governance
- Proposal creation (admin)
- Voting rights:
  - Authorities: 50% weight
  - Donors: 50% collective weight
  - Minimum 3 votes required
  - 24-hour voting window
  - 60% approval threshold

## Troubleshooting

### Common Issues

1. Ledger Integrity:
   - Run `/api/verify-chain`
   - Check hash linkages
   - Verify signatures

2. TNG Integration:
   - Check `tng_transactions.json`
   - Verify merchant IDs
   - Monitor usage tracking

3. AI Disbursement:
   - Review priority scores
   - Check recipient data
   - Validate allocation logic

## Security Considerations

1. Production Deployment:
   - Change default credentials
   - Enable HTTPS
   - Use secure session management
   - Implement proper DAO governance

2. Data Protection:
   - Regular backups
   - Encrypted storage
   - Access logging
   - Audit trails

## License

MIT License - See LICENSE file for details

## Contact

- Report issues on GitHub
- Check TROUBLESHOOTING.md
- Contact support team at support@example.com