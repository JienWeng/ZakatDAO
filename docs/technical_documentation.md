# ZakatDAO Technical Documentation

## System Architecture

### 1. Core Components
- Flask Backend (app.py)
- Smart Contracts (ZakatGovernanceToken.sol)
- Blockchain Ledger
- DAO Governance System
- AI Disbursement Engine

### 2. Data Flow
```
[User Interface] → [Flask Backend] → [Smart Contracts]
                                 ↓
[Blockchain Ledger] ← [DAO Voting] → [Token System]
                                 ↓
[AI Engine] → [Disbursement System] → [eWallet Integration]
```

### 3. Key Systems

#### 3.1 Governance Token (ZGT)
- Non-transferable ERC-20 token
- Minted on donation/participation
- Used for weighted voting
- Reward structure:
  - Donation: 1 ZGT per 10 RM (max 100)
  - First donation: 50 ZGT bonus
  - Voting: 5 ZGT
  - Approved proposals: 20 ZGT

#### 3.2 DAO Voting System
```python
Voting Weight = (Authority Votes × 0.5) + (Donor Votes × 0.5)
Approval Threshold = 60%
Minimum Votes = 3
Voting Period = 24 hours
```

#### 3.3 Blockchain Ledger
- CSV-based immutable ledger
- Block structure:
  ```json
  {
    "transaction_id": "tx{uuid}",
    "block_height": "n",
    "block_hash": "{hash}",
    "prev_block_hash": "{hash}",
    "transaction_type": "IN/OUT",
    "amount": "float",
    "timestamp": "ISO-8601",
    "signatures": ["validator1", "validator2"]
  }
  ```

### 4. API Reference

#### 4.1 Public Endpoints
```
GET /api/ledger.json
  Query params:
    - type: IN/OUT
    - user: string
    - voucher: string
    - start_date: ISO-8601
    - end_date: ISO-8601
  Returns:
    - transactions[]
    - summary{}
    - timestamp
```

#### 4.2 Protected Endpoints
```
POST /api/disburse
  Headers:
    - Authorization: Bearer {token}
  Body:
    - recipient_id: string
    - amount: float
    - zakat_type_id: int
```

### 5. Database Schemas

#### 5.1 Donor Storage (donors.json)
```json
{
  "email": {
    "password_hash": "string",
    "vouchers": ["string"],
    "created_at": "ISO-8601",
    "donor_id": "DONOR-{uuid}"
  }
}
```

#### 5.2 Token Storage (tokens.json)
```json
{
  "total_supply": "int",
  "balances": {
    "donor_id": "int"
  },
  "transactions": [{
    "type": "string",
    "recipient": "string",
    "amount": "int",
    "reason": "string",
    "timestamp": "ISO-8601"
  }]
}
```

### 6. Deployment

#### 6.1 Smart Contract Deployment
1. Environment setup:
   ```bash
   npm install --save-dev hardhat @nomiclabs/hardhat-waffle
   npm install --save-dev @nomiclabs/hardhat-etherscan dotenv
   ```

2. Configure network:
   ```javascript
   networks: {
     mumbai: {
       url: `https://polygon-mumbai.g.alchemy.com/v2/${KEY}`,
       accounts: [PRIVATE_KEY]
     }
   }
   ```

3. Deploy command:
   ```bash
   npx hardhat run scripts/deploy.js --network mumbai
   ```

#### 6.2 Backend Deployment
1. Dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Environment variables:
   ```
   FLASK_SECRET_KEY=
   ALCHEMY_API_KEY=
   POLYGONSCAN_API_KEY=
   ```

### 7. Security Considerations

#### 7.1 Access Control
- Admin authentication
- Donor verification
- Vote weight validation
- Transaction signing

#### 7.2 Smart Contract Security
- Non-transferable tokens
- Owner-only minting
- Restricted transfers
- Vote delegation controls

#### 7.3 Data Integrity
- Blockchain verification
- Multi-signature transactions
- Chain integrity checks
- Immutable ledger

### 8. Testing

#### 8.1 Smart Contract Tests
```bash
npx hardhat test test/ZakatGovernanceToken.test.js
```

#### 8.2 Backend Tests
```bash
python -m pytest tests/
```

### 9. Monitoring

#### 9.1 Blockchain Metrics
- Block height
- Transaction count
- Validator status
- Chain integrity

#### 9.2 Application Metrics
- Active proposals
- Voting participation
- Token distribution
- Disbursement success rate

### 10. Future Improvements
1. Layer 2 scaling
2. Enhanced AI models
3. Mobile app integration
4. Additional eWallet support
5. Advanced analytics
