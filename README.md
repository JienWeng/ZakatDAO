# ZakatDAO: Decentralized Zakat Distribution Platform

*By Jien Weng*

ZakatDAO is a pioneering decentralized platform designed to modernize and automate the distribution of zakat, ensuring **transparency**, **Shariah-compliance**, and **community-driven governance**. By leveraging blockchain technology, decentralized autonomous organization (DAO) governance, AI-driven prioritization powered by xAI, and e-wallet disbursement, ZakatDAO delivers a secure, efficient, and inclusive system for zakat management. This README provides a comprehensive overview of the platform, its objectives, technical architecture, deployment instructions, and governance model, with a focus on state-by-state implementation and the integration of xAI for prioritization.

[![ZakatDAO Image](img/banner.png)](https://zakatdao.onrender.com)

---

## Table of Contents

1. [Introduction](#introduction)
2. [Concept and Vision](#concept-and-vision)
3. [Objectives](#objectives)
4. [State-by-State Implementation](#state-by-state-implementation)
5. [Features](#features)
6. [Technical Architecture](#technical-architecture)
7. [Governance Model](#governance-model)
8. [xAI Integration for Prioritization](#xai-integration-for-prioritization)
9. [Setup Instructions](#setup-instructions)
10. [Usage Guide](#usage-guide)
11. [API Endpoints](#api-endpoints)
12. [URL Guide](#url-guide)
13. [Tech Stack](#tech-stack)
14. [Deployment Instructions](#deployment-instructions)
15. [Security Considerations](#security-considerations)
16. [Testing](#testing)
17. [Monitoring](#monitoring)
18. [Future Improvements](#future-improvements)
19. [Contact and Support](#contact-and-support)
---

## Introduction

Zakat, one of the five pillars of Islam, mandates that Muslims donate a portion of their wealth to support those in need, categorized into eight asnaf (recipient groups) as defined by Islamic law. Traditional zakat distribution systems often face challenges such as lack of transparency, inefficiencies due to intermediaries, and limited accessibility for rural or underbanked communities. ZakatDAO addresses these issues by introducing a decentralized, blockchain-based platform that automates and democratizes zakat distribution while adhering to Shariah principles.

ZakatDAO integrates cutting-edge technologies:

- **Blockchain**: For immutable, transparent record-keeping.
- **DAO Governance**: For community-driven decision-making.
- **xAI**: For AI-powered recipient prioritization.
- **E-Wallets and Vouchers**: For accessible and inclusive disbursements.

The platform is designed to operate on a state-by-state basis, ensuring alignment with local Islamic councils while empowering donors and stakeholders to participate in governance.

---

## ZakatDAO Hub

Welcome to the ZakatDAO hub! Here you can find important resources to better understand the platform:

- [Solution Overview PDF](https://jienweng.netlify.app/assets/misc/report-ZakatDAO.pdf)
- [Pitch Deck PDF](https://github.com/JienWeng/ZakatDAO/blob/main/Documentations/ZakatDao-pitch.pdf)
- [Live Demo](https://zakatdao.onrender.com)
- [Explanation Video](link-to-video)

Else, please find it under the [Documentations Folder](https://github.com/JienWeng/ZakatDAO/tree/main/Documentations).

---

## Concept and Vision

ZakatDAO reimagines zakat distribution as a decentralized, community-driven process that leverages technology to uphold Islamic values. The platform aims to:

- **Ensure Transparency**: Every transaction, vote, and disbursement is recorded on an immutable blockchain ledger, publicly accessible to donors, recipients, and authorities.
- **Uphold Shariah Compliance**: The system adheres to Islamic principles, ensuring funds are distributed to the eight asnaf groups in a fair and compliant manner.
- **Empower Communities**: Through DAO governance, donors and state authorities collaborate to make decisions on fund allocation and policy changes.
- **Enhance Accessibility**: By integrating e-wallets (e.g., TNG, Boost, FPX) and QR code-enabled vouchers, ZakatDAO ensures that zakat reaches both urban and rural communities.
- **Maximize Efficiency**: AI-driven prioritization and smart contracts eliminate intermediaries, reducing costs and accelerating disbursements.

The vision is to create a global standard for zakat distribution that is transparent, inclusive, and technologically advanced, starting with a state-by-state rollout to align with local regulations and Islamic councils.

---

## Objectives

ZakatDAO is built with the following objectives:

1. **Transparency**: Provide a publicly accessible blockchain ledger to track all donations, votes, and disbursements.
2. **Shariah Compliance**: Ensure zakat funds are allocated to the eight asnaf groups as per Islamic law, with oversight from state Islamic councils.
3. **Decentralized Governance**: Enable donors and state authorities to participate in decision-making through a DAO, with state councils holding 51% voting weight and donors 49%.
4. **Inclusivity**: Support underbanked and rural communities through e-wallet integration and offline vouchers.
5. **Efficiency**: Use xAI for recipient prioritization and smart contracts for automated disbursements, minimizing operational costs.

---

## State-by-State Implementation

To ensure alignment with local regulations and Islamic governance, ZakatDAO will be implemented on a state-by-state basis, starting with a pilot in Malaysia. Each state will have its own instance of the platform, customized to integrate with local Islamic councils and e-wallet providers. Key aspects of the state-by-state approach include:

- **Local Islamic Council Oversight**: State Islamic councils will hold 51% of the voting weight in the DAO, ensuring Shariah compliance and regulatory alignment. Donors collectively hold 49%, empowering community participation while respecting authority.
- **Customized E-Wallet Integration**: Each state will integrate with locally popular e-wallets (e.g., TNG, Boost, FPX in Malaysia) to ensure accessibility.
- **Localized Asnaf Prioritization**: xAI models will be trained on state-specific data to prioritize recipients based on local socioeconomic conditions.
- **State-Specific Blockchain Ledger**: Each state will maintain its own blockchain ledger, ensuring data sovereignty and compliance with local laws.
- **Phased Rollout**: The pilot will begin in one state (e.g., Selangor, Malaysia), with learnings applied to subsequent states. Each state will have its own governance token (ZGT) and smart contracts.

This approach ensures scalability while respecting regional differences in governance and infrastructure.

---

## Features

### Donor Interface

- **Donation**: Contribute via e-wallets or FPX, with instant confirmation and voucher issuance.
- **Transparency**: View the live blockchain ledger of all transactions, including donations and disbursements.
- **Voting**: Participate in DAO governance by voting on fund allocation (e.g., education, healthcare) and policy proposals.
- **Vouchers**: Download digital or printable vouchers showing donation usage, redeemable at partner merchants.

### AI-Driven Disbursement

- **xAI Prioritization**: Uses xAI models to score recipients based on need, ensuring fair and data-driven fund allocation.
- **Hybrid Decision-Making**: Combines xAI scores with donor and authority votes for disbursement decisions.
- **Manual Override**: Large or sensitive disbursements require DAO voting for approval.

### DAO Governance

- **Smart Contracts**: Transparent, community-driven voting via Solidity-based smart contracts.
- **Multi-Signature**: Large fund releases require multiple signatures from authorities and donors.
- **Immutable Records**: All governance decisions are recorded on-chain for auditability.

### Real-World Integration

- **E-Wallet Support**: Integrates with TNG, Boost, FPX, and other local payment systems.
- **Offline Vouchers**: QR code-enabled vouchers for recipients without digital access, redeemable at partner merchants.
- **Tracking**: Donors and recipients can track disbursements and voucher usage in real-time.

---

## Technical Architecture

ZakatDAO's architecture is modular and scalable, integrating multiple technologies to deliver a seamless experience.

### Core Components

1. **Flask Backend**: Handles API requests, user authentication, and integration with smart contracts.
2. **Smart Contracts**: Written in Solidity, deployed on Ethereum or Polygon for governance and token management.
3. **Blockchain Ledger**: An immutable CSV-based ledger for transaction records, with block height and hash validation.
4. **DAO Governance System**: Manages proposals, voting, and token-based governance.
5. **xAI Disbursement Engine**: Uses xAI models to prioritize recipients based on socioeconomic data.

### Data Flow
```bash
[User Interface] → [Flask Backend] → [Smart Contracts]
↓
[Blockchain Ledger] ← [DAO Voting] → [ZGT Token System]
↓
[xAI Engine] → [Disbursement System] → [E-Wallet Integration]
```


### Key Systems

#### Governance Token (ZGT)

- **Type**: Non-transferable ERC-20 token.
- **Purpose**: Used for weighted voting in the DAO.
- **Minting Rules**:
  - 1 ZGT per 10 RM donated (max 100 ZGT per donation).
  - 50 ZGT bonus for first-time donors.
  - 5 ZGT for voting in a proposal.
  - 20 ZGT for approved proposals.
- **State-Specific**: Each state has its own ZGT instance.

#### DAO Voting System

- **Voting Weight**: State Islamic councils (51%) + Donors (49%).
- **Approval Threshold**: 60% weighted approval.
- **Minimum Votes**: 3 votes per proposal.
- **Voting Period**: 24 hours.
- **Proposal Types**:
  - Disbursement proposals (e.g., fund allocation to specific asnaf).
  - Allocation policy proposals (e.g., percentage changes for asnaf categories).

#### Blockchain Ledger

- **Structure**:

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

  Validation: Chain integrity is verified via `/api/verify-chain.`

# Governance Model


ZakatDAO's governance is designed to balance authority oversight with community participation, implemented through a DAO with the following rules:

-   **Voting Weight**:
    -   State Islamic councils: 51% (ensuring Shariah compliance and regulatory alignment).
    -   Donors: 49% (collective weight, proportional to ZGT holdings).
-   **Proposal Types**:
    -   **Disbursement Proposals**: For specific fund allocations (e.g., 100,000 RM for education).
    -   **Allocation Policy Proposals**: For changing asnaf percentages or usage priorities.
-   **Voting Process**:
    -   Proposals are created by admins at `/dao/allocations/propose` or `/proposal/<id>`.
    -   Voting is open for 24 hours, requiring a minimum of 3 votes and 60% weighted approval.
    -   Approved proposals are auto-executed via smart contracts.
-   **Multi-Signature**: Large disbursements require signatures from multiple validators (e.g., council members and top donors).
-   **Transparency**: All votes and outcomes are recorded on the blockchain ledger.

This model ensures that state authorities maintain control while donors have a meaningful voice, fostering trust and collaboration.

# xAI Integration for Prioritization

ZakatDAO leverages xAI's advanced AI models to prioritize recipients, ensuring fair and data-driven disbursements. The xAI engine is integrated as follows:

-   **Data Inputs**:
    -   Socioeconomic data (e.g., income, family size, location).
    -   Asnaf category (e.g., poor, needy, debtors).
    -   State-specific factors (e.g., cost of living, unemployment rates).
-   **Scoring Process**:
    -   xAI models assign a priority score to each recipient based on need and eligibility.
    -   Scores are normalized to ensure fairness across asnaf groups.
-   **Hybrid Decision-Making**:
    -   xAI scores are combined with DAO votes to determine final disbursements.
    -   For manual disbursements, xAI scores serve as recommendations, subject to DAO approval.
-   **State-Specific Customization**:
    -   xAI models are trained on state-specific datasets to reflect local conditions.
    -   Regular retraining ensures models remain accurate and relevant.
-   **Transparency**:
    -   Priority scores and AI decision logs are recorded on the blockchain for auditability.

By using xAI, ZakatDAO ensures that zakat funds are allocated to those who need them most, while maintaining transparency and community oversight.

Setup Instructions
------------------

To set up ZakatDAO locally, follow these steps:

1.  **Clone the Repository**:

    ```
    git clone https://github.com/JienWeng/ZakatDAO
    cd ZakatDAO
    ```

2.  **Set Up Virtual Environment**:

    ```
    python -m venv venv
    source venv/bin/activate  # For Unix/macOS
    venv\Scripts\activate     # For Windows
    ```

3.  **Install Dependencies**:

    ```
    chmod +x install_dependencies.sh
    ./install_dependencies.sh
    ```

4.  **Configure Environment Variables**: Create a `.env` file in the root directory with the following:

    ```
    FLASK_SECRET_KEY=your-secret-key
    ALCHEMY_API_KEY=your-alchemy-api-key
    POLYGONSCAN_API_KEY=your-polygonscan-api-key
    PRIVATE_KEY=your-wallet-private-key
    ```

5.  **Run the Application**:

    ```
    flask run
    ```

# Usage Guide

### Donation Flow

1.  Navigate to `/donate`.
2.  Fill in donation details (amount, payment method).
3.  Receive a unique voucher code.
4.  Track donation status in the public ledger at `/ledger`.

### Disbursement Flow

1.  Log in as admin at `/admin/login`.
2.  Review available funds at `/admin`.
3.  Choose disbursement method:
    -   Manual: `/disburse`.
    -   AI-Powered: `/admin/ai-disbursement`.
4.  Monitor transactions at `/ledger`.

### Voucher Usage

1.  Recipients receive a TNG voucher (digital or printable).
2.  Use the voucher at partner merchants via QR code.
3.  Transactions are logged in `usage.csv`.
4.  View usage history at `/voucher/<code>/usage`.

# API Endpoints

### Public APIs

```
GET /api/ledger.json
- Description: View all transactions.
- Query Params:
  - type: IN/OUT
  - user: Filter by user ID
  - voucher: Filter by voucher code
  - start_date: Filter from date (ISO-8601)
  - end_date: Filter to date (ISO-8601)
- Response: JSON array of transactions

GET /voucher/<code>
- Description: Get voucher details and usage history.
- Response: JSON with voucher details and usage log
```

### Admin APIs

```
POST /api/disburse
- Description: Disburse funds to a recipient.
- Headers: Authorization: Bearer <token>
- Body:
  - recipient_id: string
  - amount: float
  - zakat_type_id: int
- Response: JSON with transaction details

GET /api/verify-chain
- Description: Verify ledger integrity.
- Response: JSON with validation status and latest block
```

# URL Guide


### Public Pages

-   `/`: Home page.
-   `/donate`: Donation form.
-   `/ledger`: Public transaction ledger.
-   `/voucher/<code>`: View voucher details.
-   `/voucher/<code>/usage`: View voucher usage history.

### Admin Interface

-   `/admin`: Admin dashboard.
-   `/admin/login`: Admin login page.
-   `/admin/logout`: Admin logout.
-   `/admin/recipients`: Manage recipients.
-   `/admin/ai-disbursement`: AI-powered disbursement interface.

### DAO Voting System

-   `/proposal/<id>`: View proposal details.
-   `/proposal/<id>/vote`: Cast vote on a proposal (requires authentication).
-   `/dao`: DAO governance dashboard.
-   `/dao/proposals`: View all proposals.
-   `/dao/allocations`: View current allocation policies.
-   `/dao/allocations/propose`: Propose new allocation policy (admin only).
-   `/dao/vote/<id>`: Cast vote on a proposal.


# Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | React.js, Tailwind CSS |
| Backend | Node.js / Flask (Python) |
| Blockchain Layer | Ethereum / Polygon |
| Smart Contracts | Solidity |
| AI Models | Python (scikit-learn, TensorFlow, xAI) |
| Off-chain Storage | IPFS |
| E-Wallet Support | TNG, Boost, FPX |
| Deployment | AWS, Docker |

# Deployment Instructions

### Smart Contract Deployment

1.  **Install Dependencies**:

    ```
    npm install --save-dev hardhat @nomiclabs/hardhat-waffle @nomiclabs/hardhat-etherscan dotenv
    ```

2.  **Configure Network**: Update `hardhat.config.js`:

    ```
    networks: {
      mumbai: {
        url: `https://polygon-mumbai.g.alchemy.com/v2/${process.env.ALCHEMY_API_KEY}`,
        accounts: [process.env.PRIVATE_KEY]
      }
    }
    ```

3.  **Deploy Contract**:

    ```
    npx hardhat run scripts/deploy.js --network mumbai
    ```

4.  **Verify on Polygonscan**: The contract will be automatically verified. Check status at <https://mumbai.polygonscan.com/>.

### Backend Deployment

1.  **Install Dependencies**:

    ```
    pip install -r requirements.txt
    ```

2.  **Set Environment Variables**: Ensure `.env` includes:

    ```
    FLASK_SECRET_KEY=
    ALCHEMY_API_KEY=
    POLYGONSCAN_API_KEY=
    ```

3.  **Deploy with Docker**:

    ```
    docker build -t zakatdao .
    docker run -p 5000:5000 zakatdao
    ```

# Security Considerations

-   **Access Control**: Admin authentication, donor verification, and vote weight validation.
-   **Smart Contract Security**: Non-transferable tokens, owner-only minting, restricted transfers.
-   **Data Integrity**: Blockchain verification, multi-signature transactions, chain integrity checks.
-   **Privacy**: Recipient data is anonymized, and sensitive information is stored off-chain on IPFS.

# Testing

### Smart Contract Tests

```
npx hardhat test test/ZakatGovernanceToken.test.js
```


# Future Improvements


1.  **Layer 2 Scaling**: Transition to Optimism or Arbitrum for lower transaction costs.
2.  **Enhanced xAI Models**: Incorporate real-time data feeds for more accurate prioritization.
3.  **Mobile App**: Develop iOS and Android apps for donor and recipient access.
4.  **Additional E-Wallets**: Support international payment systems like PayPal or Alipay.
5.  **Advanced Analytics**: Provide donors with detailed impact reports and visualizations.
6. **Global Expansion**: Expand the platform to reach people globally.
7. **Sadaqah Application**: Apply to Sadaqah-based DAO for more general application.


# Contact and Support

-   **GitHub**: Report issues at <https://github.com/JienWeng/ZakatDAO>.
-   **Troubleshooting**: Refer to `TROUBLESHOOTING.md` in the repository.
-   **Email**: Contact <laijienweng@gmail.com> for inquiries.


*ZakatDAO is a community-driven initiative to revolutionize zakat distribution. Join us in building a transparent, inclusive, and Shariah-compliant future for zakat.*
