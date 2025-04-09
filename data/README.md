# Zakat DAO - Decentralized Zakat Management System

This directory contains the core data for the Zakat DAO platform, implementing a blockchain-style ledger with DAO governance.

## Core Components

### 1. Ledger System (ledger.csv)
- Immutable, append-only transaction record
- Each transaction includes:
  - Unique transaction ID and block metadata
  - Transaction type (IN/OUT)
  - Amount and timestamp
  - Zakat type classification
  - Voucher tracking
  - Blockchain validation hashes
  - DAO consensus signatures

### 2. Recipient Management (recipients.json)
- Comprehensive recipient profiles including:
  - Unique ID and basic information
  - Zakat eligibility category (Fakir, Miskin, etc.)
  - Need assessment metrics
  - Disbursement history
  - Priority scoring factors

### 3. Disbursement System
#### Manual Disbursements
- Requires DAO voting approval
- Weighted voting system:
  - 50% Authority weight
  - 50% Donor weight
  - Minimum 3 votes required
  - 24-hour voting window
  - 60% approval threshold

#### AI-Powered Disbursements
- Automated priority scoring based on:
  - Recipient category weights
  - Family size and dependents
  - Monthly income thresholds
  - Previous assistance received
  - Special circumstances

### 4. Voucher Tracking
- Each donation generates a unique voucher
- Vouchers maintain:
  - Total donated amount
  - Disbursement history
  - Usage tracking at authorized merchants
  - TNG eWallet integration

## Data File Structure

```
data/
├── ledger.csv          # Main transaction ledger
├── recipients.json     # Recipient profiles
├── proposals.json      # DAO voting proposals
├── disbursements.csv   # Detailed disbursement records
└── usage.csv          # Voucher usage tracking
```

## Voting System Details

### Proposal Creation
1. Admin initiates disbursement
2. System creates proposal
3. 24-hour voting period starts
4. Both authorities and donors can vote
5. Weighted consensus required

### Vote Weights
- Authority votes: 50% of total weight
- Donor votes: 50% of total weight collectively
- Minimum requirements:
  - At least 3 total votes
  - 60% weighted approval for passing
  - Both donor and authority participation

### Execution
- Approved proposals auto-execute
- Failed proposals are archived
- All voting activity recorded in blockchain

## Security and Verification

- Each transaction has unique hash
- Blockchain-style validation
- Multi-signature requirements
- Complete audit trail
- Immutable transaction history

## Integration Points

### Touch 'n Go Integration
- Direct disbursement to TNG wallets
- Merchant purchase tracking
- Usage restrictions and monitoring
- Transaction verification

## Technical Notes

- All monetary values in MYR (RM)
- Timestamps in UTC+8
- SHA-256 for block hashing
- JSON for complex data structures
- CSV for transaction records
