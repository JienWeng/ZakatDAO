import csv
import os
import uuid
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
import io
import base64
import json
from functools import wraps
import ai_disbursement
from tng_integration import send_to_tng_wallet, track_voucher_usage, get_voucher_usage, MOCK_TNG_MERCHANTS
from config import ZAKAT_TYPES, ZAKAT_TYPES_BY_ID
from ledger_utils import write_to_ledger
from dao_voting import DaoVoting
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Initialize DAO voting
dao = DaoVoting()

# Try to import qrcode, but handle the case where it's not installed
try:
    import qrcode
    from PIL import Image, ImageDraw, ImageFont
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False
    print("Warning: qrcode or Pillow module not found. QR code generation will be disabled.")
    print("To enable QR code generation, run: pip install qrcode[pil]")

# Ensure the data directory exists
os.makedirs('data', exist_ok=True)

# List of approved NGOs for disbursement
NGOS = [
    {"id": 1, "name": "Amanah Foundation", "description": "Working on poverty alleviation and education"},
    {"id": 2, "name": "Ihsan Medical Trust", "description": "Providing healthcare services to underprivileged communities"},
    {"id": 3, "name": "Khidmat Relief", "description": "Disaster response and refugee support organization"},
    {"id": 4, "name": "Taleem for All", "description": "Education-focused charity working in underserved areas"},
]

# Add Zakat types to app context
app.config['ZAKAT_TYPES'] = ZAKAT_TYPES
app.config['ZAKAT_TYPES_BY_ID'] = ZAKAT_TYPES_BY_ID

# Simple admin auth
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # For demo only, use better auth in production

# Admin auth decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('admin_logged_in') != True:
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    """Display the landing page with info and donate button."""
    return render_template('index.html')

@app.route('/donate', methods=['GET'])
def donate_form():
    """Display donation form."""
    return render_template('donate_form.html')

@app.route('/donate', methods=['POST'])
def process_donation():
    """Process donation form submission."""
    # Get form data
    amount = float(request.form.get('amount', 0))
    donor_name = request.form.get('donor_name', 'Anonymous')
    donor_email = request.form.get('donor_email', '')
    
    # Get Zakat type (required)
    zakat_type_id = request.form.get('zakat_type_id', '')
    zakat_type_name = ''
    if zakat_type_id and zakat_type_id.isdigit():
        zakat_type_id = int(zakat_type_id)
        zakat_type = app.config['ZAKAT_TYPES_BY_ID'].get(zakat_type_id, {})
        zakat_type_name = zakat_type.get('name', '')
    else:
        # Redirect back to form if no zakat type selected
        return render_template('donate_form.html', 
                              error="Please select a Zakat type")
    
    # Format amount display in RM
    formatted_amount = format_amount(amount)
    
    # Create donation data with simplified structure (no cause)
    donation_data = {
        'transaction_id': f"tx{uuid.uuid4().hex[:8]}",
        'transaction_type': 'IN',
        'amount': amount,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'user': donor_name,
        'email': donor_email,
        'voucher_code': str(uuid.uuid4()),
        'zakat_type_id': zakat_type_id,
        'zakat_type_name': zakat_type_name,
        'recipient_id': '',
        'disbursement_type': ''
    }
    
    # Write to blockchain ledger
    write_to_ledger(donation_data)
    
    # Store in session for confirmation page
    session['donation'] = donation_data
    
    return redirect(url_for('confirmation'))

@app.route('/confirmation')
def confirmation():
    """Display donation confirmation with voucher code."""
    # Get donation data from session
    donation = session.get('donation')
    if not donation:
        return redirect(url_for('home'))
    
    # Generate QR code for the voucher if the module is available
    qr_encoded = None
    if HAS_QRCODE:
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(donation['voucher_code'])
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert QR code to base64 for embedding in HTML
            buffered = io.BytesIO()
            qr_img.save(buffered)
            qr_encoded = base64.b64encode(buffered.getvalue()).decode()
        except Exception as e:
            print(f"Error generating QR code: {e}")
    
    # Clear from session after retrieving
    session.pop('donation', None)
    
    return render_template('confirmation.html', donation=donation, qr_code=qr_encoded)

@app.route('/api/qrcode/<voucher_code>')
def generate_qrcode(voucher_code):
    """Generate a QR code for a voucher."""
    try:
        # Create a simple QR code with PIL even if qrcode module is not available
        img_size = 200
        img = Image.new('RGB', (img_size, img_size), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        try:
            # Try to import and use qrcode library
            import qrcode
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            verify_url = f"{request.host_url}voucher/{voucher_code}"
            qr.add_data(verify_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
        except ImportError:
            # If qrcode not available, draw a placeholder square with text
            draw.rectangle([(0, 0), (img_size - 1, img_size - 1)], outline=(0, 0, 0), width=2)
            draw.rectangle([(20, 20), (img_size - 21, img_size - 21)], outline=(0, 0, 0), width=2)
            
            # Try to add text
            try:
                font = ImageFont.load_default()
                draw.text((40, 90), "QR Placeholder", fill=(0, 0, 0), font=font)
                # Add voucher code (truncated if needed)
                code_display = voucher_code[:10] + "..." if len(voucher_code) > 10 else voucher_code
                draw.text((40, 110), code_display, fill=(0, 0, 0), font=font)
            except Exception as e:
                print(f"Error adding text to placeholder: {e}")
        
        # Convert to bytes and return
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # Set cache headers to prevent caching issues
        response = send_file(img_io, mimetype='image/png')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
        
    except Exception as e:
        print(f"QR Code generation error: {e}")
        # Return a simple error image
        img = Image.new('RGB', (200, 200), color=(255, 200, 200))
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 0), (199, 199)], outline=(255, 0, 0), width=2)
        draw.line([(0, 0), (199, 199)], fill=(255, 0, 0), width=2)
        draw.line([(199, 0), (0, 199)], fill=(255, 0, 0), width=2)
        
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')

def safe_float(value, default=0.0):
    """Safely convert a value to float, returning default if conversion fails."""
    try:
        if isinstance(value, str):
            # Remove any currency symbols and commas
            value = value.replace('RM', '').replace(',', '').strip()
        return float(value)
    except (ValueError, TypeError):
        return default

@app.route('/ledger')
def view_ledger():
    """Display the public transaction ledger."""
    # Get filter parameters from query string
    filters = {
        'transaction_type': request.args.get('type'),
        'user': request.args.get('user'),
        'voucher_code': request.args.get('voucher'),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
    }
    
    # Read transactions with optional filters
    transactions = read_ledger(filters)
    
    # Calculate statistics by Zakat type
    zakat_stats = {}
    for zakat_type in app.config['ZAKAT_TYPES']:
        zakat_stats[zakat_type['id']] = {
            'name': zakat_type['name'],
            'collected': 0,
            'disbursed': 0,
            'available': 0
        }
    
    # Calculate totals
    total_donated = 0
    total_disbursed = 0
    
    for tx in transactions:
        amount = safe_float(tx.get('amount', 0))
        if tx.get('transaction_type') == 'IN':
            total_donated += amount
            zakat_type_id = int(tx.get('zakat_type_id', 0) or 0)
            if zakat_type_id in zakat_stats:
                zakat_stats[zakat_type_id]['collected'] += amount
        elif tx.get('transaction_type') == 'OUT':
            total_disbursed += amount
    
    # Calculate available balances
    for stats in zakat_stats.values():
        stats['available'] = stats['collected'] - stats['disbursed']
    
    return render_template('ledger.html', 
                          transactions=transactions,
                          total_donated=total_donated,
                          total_disbursed=total_disbursed,
                          zakat_stats=zakat_stats,
                          filters=filters)

@app.route('/voucher/<voucher_code>')
def view_voucher(voucher_code):
    """View details and status of a specific voucher."""
    try:
        # Get all transactions for this voucher
        transactions = read_ledger({'voucher_code': voucher_code})
        if not transactions:
            return render_template('voucher_not_found.html', voucher_code=voucher_code)
        
        # Group by type and calculate totals
        donations = []
        disbursements = []
        total_donated = 0
        total_disbursed = 0
        
        for tx in transactions:
            if tx['transaction_type'] == 'IN':
                donations.append(tx)
                total_donated += safe_float(tx['amount'])
            else:
                disbursements.append(tx)
                total_disbursed += safe_float(tx['amount'])
        
        # Get status
        if total_disbursed >= total_donated:
            status = 'fully_disbursed'
        elif total_disbursed > 0:
            status = 'partially_disbursed'
        else:
            status = 'pending'
        
        # Group disbursements by recipient
        recipient_summary = {}
        for tx in disbursements:
            recipient_id = tx['recipient_id']
            if recipient_id not in recipient_summary:
                recipient_summary[recipient_id] = {
                    'name': tx['user'],
                    'total_received': 0,
                    'disbursements': []
                }
            recipient_summary[recipient_id]['total_received'] += safe_float(tx['amount'])
            recipient_summary[recipient_id]['disbursements'].append(tx)
        
        return render_template(
            'voucher_details.html',
            voucher={
                'voucher_code': voucher_code,
                'donations': donations,
                'disbursements': disbursements,
                'total_donated': total_donated,
                'total_disbursed': total_disbursed,
                'remaining_balance': total_donated - total_disbursed,
                'status': status,
                'recipient_summary': recipient_summary
            }
        )
    except Exception as e:
        print(f"Error viewing voucher: {e}")
        return render_template('error.html', message="Error retrieving voucher details")

@app.route('/voucher/<voucher_code>/usage')
def view_voucher_usage(voucher_code):
    """View how a voucher has been used."""
    usage_history = get_voucher_usage(voucher_code)
    return render_template('voucher_usage.html', 
                         voucher_code=voucher_code,
                         usage_history=usage_history)

@app.route('/download-voucher/<voucher_code>')
def download_voucher(voucher_code):
    """Generate and download a voucher."""
    # Find transactions with this voucher
    filters = {'voucher_code': voucher_code}
    transactions = read_ledger(filters)
    
    if not transactions:
        return render_template('voucher_not_found.html', voucher_code=voucher_code)
    
    # Find the donation (IN transaction)
    donation = next((t for t in transactions if t['transaction_type'] == 'IN'), None)
    if not donation:
        return render_template('voucher_not_found.html', voucher_code=voucher_code)
    
    # Get requested format
    format = request.args.get('format', 'png').lower()
    
    try:
        # Create voucher image first (needed for both PNG and PDF)
        img_width, img_height = 800, 600
        img = Image.new('RGB', (img_width, img_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Try to load fonts, use default if not available
        try:
            title_font = ImageFont.truetype("Arial Bold.ttf", 30)
            normal_font = ImageFont.truetype("Arial.ttf", 16)
            small_font = ImageFont.truetype("Arial.ttf", 12)
        except:
            # Fallback to default font
            title_font = ImageFont.load_default()
            normal_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Draw voucher content
        draw.text((50, 40), "ZAKAT DONATION VOUCHER", fill=(0, 128, 0), font=title_font)
        draw.text((50, 100), f"Voucher ID:", fill=(0, 0, 0), font=normal_font)
        draw.text((50, 125), f"{voucher_code}", fill=(0, 0, 0), font=small_font)
        
        # Format amount nicely
        amount = format_amount(donation.get('amount', 0))
        draw.text((50, 160), f"Amount: {amount}", fill=(0, 0, 0), font=normal_font)
        
        # Format date nicely
        date_str = donation.get('timestamp', 'N/A')
        draw.text((50, 190), f"Date: {date_str}", fill=(0, 0, 0), font=normal_font)
        
        # Add donor information
        donor_name = donation.get('user', 'Anonymous')
        draw.text((50, 220), f"Donor: {donor_name}", fill=(0, 0, 0), font=normal_font)
        
        # Add transaction ID
        tx_id = donation.get('transaction_id', 'Unknown')
        draw.text((50, 250), f"Transaction ID: {tx_id}", fill=(0, 0, 0), font=small_font)
        
        # Draw decorative border
        draw.rectangle([(20, 20), (img_width-20, img_height-20)], outline=(0, 128, 0), width=2)
        
        # Generate QR code
        try:
            import qrcode
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            verify_url = f"{request.host_url}voucher/{voucher_code}"
            qr.add_data(verify_url)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.resize((200, 200))
            
            # Convert PIL Image to bytes for pasting
            img.paste(qr_img, (550, 100))
            
            # Add text explaining QR code
            draw.text((550, 310), "Scan to verify", fill=(0, 0, 0), font=small_font)
        except ImportError:
            # Draw placeholder if qrcode module not available
            draw.rectangle([(550, 100), (750, 300)], outline=(0, 0, 0), width=2)
            draw.line([(550, 100), (750, 300)], fill=(0, 0, 0), width=2)
            draw.line([(750, 100), (550, 300)], fill=(0, 0, 0), width=2)
            draw.text((600, 200), "QR Placeholder", fill=(0, 0, 0), font=normal_font)
        
        # Add footer with verification instructions
        draw.text((50, img_height-50), "Verify this voucher online at:", fill=(0, 0, 0), font=small_font)
        draw.text((50, img_height-30), f"{request.host_url}voucher/{voucher_code}", fill=(0, 0, 0), font=small_font)
            
        # Handle different formats
        if format == 'pdf':
            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter
                from reportlab.lib.utils import ImageReader
                
                # Create PDF in memory
                pdf_buffer = io.BytesIO()
                
                # Convert PIL image to bytes for PDF embedding
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                # Create PDF with embedded image
                c = canvas.Canvas(pdf_buffer, pagesize=(img_width, img_height))
                c.drawImage(ImageReader(img_buffer), 0, 0, width=img_width, height=img_height)
                c.save()
                
                pdf_buffer.seek(0)
                return send_file(
                    pdf_buffer, 
                    mimetype='application/pdf',
                    download_name=f'zakat_voucher_{voucher_code[:8]}.pdf',
                    as_attachment=True
                )
                
            except ImportError:
                # Fallback to PNG if reportlab not installed
                format = 'png'
        
        # Default to PNG format
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return send_file(
            img_buffer, 
            mimetype='image/png',
            download_name=f'zakat_voucher_{voucher_code[:8]}.png',
            as_attachment=True
        )
        
    except Exception as e:
        app.logger.error(f"Error generating voucher: {e}")
        return render_template('error.html', message=f"Error generating voucher: {str(e)}")

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard for managing disbursements."""
    # Get total donations
    transactions = read_ledger()
    
    # Calculate statistics by Zakat type
    zakat_stats = {}
    for zakat_type in app.config['ZAKAT_TYPES']:
        zakat_stats[zakat_type['id']] = {
            'name': zakat_type['name'],
            'collected': 0,
            'disbursed': 0,
            'available': 0
        }
    
    # Calculate totals and zakat type stats
    total_donations = 0
    total_disbursements = 0
    
    for tx in transactions:
        amount = safe_float(tx.get('amount', 0))
        if tx.get('transaction_type') == 'IN':
            total_donations += amount
            zakat_type_id = int(tx.get('zakat_type_id', 0) or 0)
            if zakat_type_id in zakat_stats:
                zakat_stats[zakat_type_id]['collected'] += amount
        elif tx.get('transaction_type') == 'OUT':
            total_disbursements += amount
            # For disbursements, we don't track by zakat type
            
    # Calculate available balances for each zakat type
    for stats in zakat_stats.values():
        stats['available'] = stats['collected'] - stats['disbursed']
    
    return render_template('admin_dashboard.html', 
                         total_donations=format_amount(total_donations),
                         total_disbursements=format_amount(total_disbursements),
                         available_balance=format_amount(total_donations - total_disbursements),
                         zakat_stats=zakat_stats,
                         zakat_types=app.config['ZAKAT_TYPES'],
                         ngos=NGOS,
                         latest_block_height=get_latest_block_height(),
                         latest_validation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Add new helper function
def get_latest_block_height():
    """Get the latest block height from the ledger."""
    transactions = read_ledger()
    if not transactions:
        return 0
    return max(int(tx.get('block_height', 0) or 0) for tx in transactions)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            next_url = request.args.get('next', url_for('admin_dashboard'))
            return redirect(next_url)
        else:
            error = 'Invalid credentials. Please try again.'
    
    return render_template('admin_login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    """Admin logout."""
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))

@app.route('/disburse', methods=['GET', 'POST'])
@admin_required
def disburse_funds():
    """Handle disbursement of funds to recipients."""
    if request.method == 'POST':
        # Get form data
        amount = float(request.form.get('amount', 0))
        recipient = request.form.get('recipient', '')
        notes = request.form.get('notes', '')
        voucher_code = request.form.get('voucher_code', '')
        
        # Validate available balance
        available_balance = get_available_balance()
        if amount > available_balance:
            return render_template('error.html', 
                                message=f"Insufficient funds. Available balance: {format_amount(available_balance)}")
        
        # Create disbursement proposal
        disbursement_data = {
            'transaction_id': f"tx{uuid.uuid4().hex[:8]}",
            'transaction_type': 'OUT',
            'amount': amount,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'user': recipient,
            'notes': notes,
            'voucher_code': voucher_code if voucher_code else '',
            'zakat_type_id': request.form.get('zakat_type_id', '1'),
            'recipient_id': recipient
        }
        
        # Create proposal
        proposal_id = dao.create_proposal(
            disbursement_data=disbursement_data,
            created_by=session.get('admin_username', 'admin')
        )
        
        # Automatically add admin vote
        dao.vote(
            proposal_id=proposal_id,
            voter_id=session.get('admin_username', 'admin'),
            vote='approve',
            voter_type='authority',
            voter_weight=1.0
        )
        
        return redirect(url_for('view_proposal', proposal_id=proposal_id))
    
    # GET request - show disbursement form
    voucher_code = request.args.get('voucher_code')
    
    # Load recipients for the form
    recipients = ai_disbursement.load_recipients()
    recipients_by_category = {}
    for recipient in recipients:
        category = recipient.get('category_name', 'Uncategorized')
        if category not in recipients_by_category:
            recipients_by_category[category] = []
        recipients_by_category[category].append(recipient)
    
    return render_template('disburse_form.html', 
                         recipients_by_category=recipients_by_category,
                         voucher_code=voucher_code,
                         zakat_types=app.config['ZAKAT_TYPES'])

# Add new DAO governance routes
@app.route('/dao')
def dao_dashboard():
    """DAO governance dashboard."""
    active_proposals = dao.get_active_proposals()
    is_donor = session.get('donor_logged_in', False)
    is_admin = session.get('admin_logged_in', False)
    
    return render_template('dao_dashboard.html',
                         proposals=active_proposals,
                         is_donor=is_donor,
                         is_admin=is_admin)

@app.route('/dao/proposals')
def list_proposals():
    """List all proposals with their status."""
    proposals = dao.get_all_proposals()
    return render_template('dao_proposals.html', proposals=proposals)

@app.route('/dao/vote/<proposal_id>', methods=['GET', 'POST'])
def dao_vote(proposal_id):
    """Cast vote on proposal."""
    if not (session.get('admin_logged_in') or session.get('donor_logged_in')):
        return redirect(url_for('login'))
    
    proposal = dao.get_proposal(proposal_id)
    if not proposal:
        return render_template('error.html', message="Proposal not found")
    
    if request.method == 'POST':
        vote = request.form.get('vote')
        if vote not in ['approve', 'reject']:
            return render_template('error.html', message="Invalid vote")
        
        voter_type = 'authority' if session.get('admin_logged_in') else 'donor'
        voter_id = session.get('admin_username' if voter_type == 'authority' else 'donor_id')
        
        try:
            status = dao.vote(
                proposal_id=proposal_id,
                voter_id=voter_id,
                vote=vote,
                voter_type=voter_type
            )
            return redirect(url_for('view_proposal', proposal_id=proposal_id))
        except ValueError as e:
            return render_template('error.html', message=str(e))
    
    return render_template('dao_vote.html', proposal=proposal)

@app.route('/donor/login', methods=['GET', 'POST'])
def donor_login():
    """Donor login page."""
    if request.method == 'POST':
        # Simplified donor auth for demo
        voucher_code = request.form.get('voucher_code')
        if voucher_code:
            session['donor_logged_in'] = True
            session['donor_id'] = f"DONOR-{voucher_code[:8]}"
            return redirect(url_for('dao_dashboard'))
        
    return render_template('donor_login.html')

@app.route('/proposal/<proposal_id>')
def view_proposal(proposal_id):
    """View disbursement proposal details and voting."""
    proposal = dao.get_proposal(proposal_id)
    if not proposal:
        return render_template('error.html', message="Proposal not found")
    
    return render_template(
        'proposal_details.html',
        proposal=proposal,
        is_admin=session.get('admin_logged_in', False),
        is_donor=session.get('donor_logged_in', False)
    )

@app.route('/proposal/<proposal_id>/vote', methods=['POST'])
def vote_on_proposal(proposal_id):
    """Handle votes on disbursement proposals."""
    if not (session.get('admin_logged_in') or session.get('donor_logged_in')):
        return redirect(url_for('login'))
    
    vote = request.form.get('vote')
    if vote not in ['approve', 'reject']:
        return render_template('error.html', message="Invalid vote")
    
    voter_type = 'authority' if session.get('admin_logged_in') else 'donor'
    voter_id = session.get('admin_username' if voter_type == 'authority' else 'donor_id')
    
    try:
        status = dao.vote(
            proposal_id=proposal_id,
            voter_id=voter_id,
            vote=vote,
            voter_type=voter_type
        )
        
        if status == 'approved':
            # Execute the disbursement
            proposal = dao.get_proposal(proposal_id)
            disbursement_data = proposal['disbursement_data']
            write_to_ledger(disbursement_data)
            
            if proposal['disbursement_data'].get('recipient_id'):
                # Update recipient's disbursement history
                update_recipient_disbursement(
                    recipient_id=disbursement_data['recipient_id'],
                    amount=disbursement_data['amount']
                )
        
        return redirect(url_for('view_proposal', proposal_id=proposal_id))
        
    except ValueError as e:
        return render_template('error.html', message=str(e))

@app.route('/disbursement-confirmation')
@admin_required
def disbursement_confirmation():
    """Confirmation page for disbursements."""
    disbursement = session.get('disbursement')
    if not disbursement:
        return redirect(url_for('admin_dashboard'))
    
    session.pop('disbursement', None)
    
    return render_template('disbursement_confirmation.html', disbursement=disbursement)

@app.route('/dao/allocations')
def view_allocations():
    """View current allocation policies."""
    allocations = dao.get_current_allocations()
    return render_template('dao_allocations.html',
                         allocations=allocations,
                         is_admin=session.get('admin_logged_in', False))

@app.route('/dao/allocations/propose', methods=['GET', 'POST'])
@admin_required
def propose_allocation():
    """Propose changes to allocation policies."""
    if request.method == 'POST':
        allocation_type = request.form.get('type')
        changes = {}
        
        if allocation_type == 'asnaf':
            # Get percentage changes for each asnaf
            for asnaf in ['fakir', 'miskin', 'amil', 'muallaf', 
                         'riqab', 'gharimin', 'fisabilillah', 'ibnu_sabil']:
                percentage = float(request.form.get(f'{asnaf}_percentage', 0))
                categories = request.form.getlist(f'{asnaf}_categories')
                
                changes[asnaf] = {
                    'percentage': percentage,
                    'categories': categories
                }
        
        try:
            proposal_id = dao.create_allocation_proposal(
                allocation_type=allocation_type,
                changes=changes,
                created_by=session.get('admin_username', 'admin')
            )
            return redirect(url_for('view_proposal', proposal_id=proposal_id))
        except ValueError as e:
            return render_template('propose_allocation.html',
                                current_allocations=dao.get_current_allocations(),
                                error=str(e))
    
    return render_template('propose_allocation.html',
                         current_allocations=dao.get_current_allocations())

def get_available_balance():
    """Calculate total available balance for disbursement."""
    transactions = read_ledger()
    total_in = sum(safe_float(tx['amount']) for tx in transactions if tx['transaction_type'] == 'IN')
    total_out = sum(safe_float(tx['amount']) for tx in transactions if tx['transaction_type'] == 'OUT')
    return total_in - total_out

def get_voucher_balance(voucher_code):
    """Calculate remaining balance for a voucher."""
    transactions = read_ledger({'voucher_code': voucher_code})
    
    total_donated = sum(
        safe_float(tx['amount']) 
        for tx in transactions 
        if tx['transaction_type'] == 'IN'
    )
    
    total_disbursed = sum(
        safe_float(tx['amount']) 
        for tx in transactions 
        if tx['transaction_type'] == 'OUT'
    )
    
    return total_donated - total_disbursed

def get_available_vouchers():
    """Get list of vouchers with remaining balance."""
    transactions = read_ledger()
    vouchers = {}
    
    for tx in transactions:
        if not tx.get('voucher_code'):
            continue
            
        voucher_code = tx['voucher_code']
        if voucher_code not in vouchers:
            vouchers[voucher_code] = {
                'total_donated': 0,
                'total_disbursed': 0,
                'zakat_type_id': tx.get('zakat_type_id'),
                'donor': tx.get('user') if tx['transaction_type'] == 'IN' else None,
                'timestamp': tx.get('timestamp'),
                'block_hash': tx.get('block_hash')
            }
        
        amount = safe_float(tx['amount'])
        if tx['transaction_type'] == 'IN':
            vouchers[voucher_code]['total_donated'] += amount
        else:
            vouchers[voucher_code]['total_disbursed'] += amount
    
    # Filter to only vouchers with remaining balance
    available_vouchers = {
        code: data for code, data in vouchers.items()
        if data['total_donated'] > data['total_disbursed']
    }
    
    return available_vouchers

def select_voucher_for_disbursement(amount, zakat_type_id=None):
    """Select best voucher(s) to disburse from based on FIFO."""
    available = get_available_vouchers()
    
    # Filter by zakat type if specified
    if zakat_type_id:
        available = {
            code: data for code, data in available.items()
            if str(data['zakat_type_id']) == str(zakat_type_id)
        }
    
    # Sort by timestamp (oldest first)
    sorted_vouchers = sorted(
        available.items(),
        key=lambda x: x[1]['timestamp']
    )
    
    for voucher_code, data in sorted_vouchers:
        remaining = data['total_donated'] - data['total_disbursed']
        if remaining >= amount:
            return {
                'voucher_code': voucher_code,
                'remaining': remaining,
                'block_hash': data['block_hash']
            }
    
    return None

def disburse_zakat(recipient_id, amount, zakat_type_id, is_ai_disbursement=False):
    """Disburse zakat funds to recipient."""
    try:
        # Validate amount and balance
        amount = safe_float(amount)
        available = get_available_balance()
        if amount <= 0 or amount > available:
            raise ValueError(f"Invalid amount or insufficient funds. Available: {format_amount(available)}")
        
        # Select source voucher(s)
        source_voucher = select_voucher_for_disbursement(amount, zakat_type_id)
        if not source_voucher:
            raise ValueError("No suitable voucher found for disbursement")
        
        # Get recipient info
        recipient_name = f"Recipient-{recipient_id}"
        notes = "Regular disbursement"
        
        if is_ai_disbursement:
            try:
                recipients = ai_disbursement.load_recipients()
                recipient = next((r for r in recipients if r['id'] == recipient_id), None)
                if recipient:
                    recipient_name = recipient.get('name', recipient_name)
                    category = recipient.get('category_name', '')
                    notes = f"AI Disbursement to {category}"
            except Exception as e:
                print(f"Error loading recipient info: {e}")
        
        # Create linked disbursement transaction
        disbursement_data = {
            'transaction_id': f"tx{uuid.uuid4().hex[:8]}",
            'transaction_type': 'OUT',
            'amount': amount,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'user': recipient_name,
            'email': '',
            'notes': notes,
            'voucher_code': source_voucher['voucher_code'],  # Link to source donation
            'zakat_type_id': zakat_type_id,
            'zakat_type_name': app.config['ZAKAT_TYPES_BY_ID'].get(zakat_type_id, {}).get('name', ''),
            'recipient_id': recipient_id,
            'disbursement_type': 'AI_TNG' if is_ai_disbursement else 'MANUAL_TNG',
            'prev_block_hash': source_voucher['block_hash']  # Link to donation block
        }
        
        # Write to ledger
        write_to_ledger(disbursement_data)
        
        # Update recipient's disbursement history
        if is_ai_disbursement:
            ai_disbursement.update_recipient_disbursement(recipient_id, amount)
        
        # Process TNG transfer
        tng_result = send_to_tng_wallet(recipient_id, amount, disbursement_data['voucher_code'])
        disbursement_data['tng_reference'] = tng_result['tng_reference']
        
        return disbursement_data
        
    except Exception as e:
        print(f"Error in disburse_zakat: {e}")
        raise

@app.route('/admin/ai-disbursement', methods=['GET', 'POST'])
@admin_required
def admin_ai_disbursement():
    """Admin interface for AI-powered fund disbursement"""
    try:
        # Get available balance
        available_funds = {'total_available': get_available_balance()}
        recipients_count = len(ai_disbursement.load_recipients())
        
        simulation_results = None
        disbursement_results = None
        
        if request.method == 'POST':
            action = request.form.get('action', '')
            max_amount = safe_float(request.form.get('max_amount', ''))
            
            if not max_amount:
                max_amount = available_funds['total_available'] * 0.8  # Default to 80% of available funds
            
            if action == 'simulate':
                # Run simulation
                recommendations = ai_disbursement.ai_disburse_funds(
                    max_disbursement=max_amount, 
                    simulation=True
                )
                
                total_disbursed = sum(r['amount'] for r in recommendations.get('disbursements', []))
                simulation_results = {
                    **recommendations,
                    'total_disbursed': total_disbursed,
                    'remaining_funds': available_funds['total_available'] - total_disbursed
                }
                
            elif action == 'disburse':
                disbursements = []
                total_disbursed = 0
                
                # Get recommendations
                recommendations = ai_disbursement.ai_disburse_funds(
                    max_disbursement=max_amount,
                    simulation=False
                )
                
                # Process each disbursement
                for rec in recommendations.get('disbursements', []):
                    try:
                        result = disburse_zakat(
                            recipient_id=rec['recipient_id'],
                            amount=rec['amount'],
                            zakat_type_id=1,  # Default to general fund
                            is_ai_disbursement=True
                        )
                        disbursements.append(result)
                        total_disbursed += rec['amount']
                    except Exception as e:
                        print(f"Error processing disbursement: {e}")
                
                disbursement_results = {
                    'success': True,
                    'total_disbursed': total_disbursed,
                    'remaining_funds': available_funds['total_available'] - total_disbursed,
                    'count': len(disbursements),
                    'disbursements': disbursements
                }
        
        return render_template(
            'admin_ai_disbursement.html',
            available_funds=available_funds,
            recipients_count=recipients_count,
            simulation_results=simulation_results,
            disbursement_results=disbursement_results
        )
    except Exception as e:
        print(f"Error in admin_ai_disbursement: {e}")
        return render_template('error.html', message=str(e))

@app.route('/admin/recipients')
@admin_required
def admin_recipients():
    """Admin interface to view and manage recipients."""
    try:
        # Load recipients from JSON file
        recipients = ai_disbursement.load_recipients()
        
        # Group recipients by category
        recipients_by_category = {}
        for recipient in recipients:
            category = recipient.get('category_name', 'Uncategorized')
            if category not in recipients_by_category:
                recipients_by_category[category] = []
            recipients_by_category[category].append(recipient)
        
        return render_template(
            'admin_recipients.html',
            recipients=recipients,
            recipients_by_category=recipients_by_category
        )
    except Exception as e:
        print(f"Error loading recipients: {e}")
        return render_template('error.html', message="Error loading recipients data")

@app.route('/api/ledger.json')
def api_ledger():
    """Provide public JSON API for the ledger data."""
    try:
        # Get filter parameters from query string
        filters = {
            'transaction_type': request.args.get('type'),
            'user': request.args.get('user'),
            'voucher_code': request.args.get('voucher'),
            'start_date': request.args.get('start_date'),
            'end_date': request.args.get('end_date'),
        }
        
        # Read transactions with optional filters
        transactions = read_ledger(filters)
        
        # Clean transactions for JSON serialization
        cleaned_transactions = []
        for tx in transactions:
            # Convert any None values to empty strings
            cleaned_tx = {k: (v if v is not None else '') for k, v in tx.items()}
            # Ensure numeric fields are properly typed
            cleaned_tx['amount'] = safe_float(cleaned_tx['amount'])
            cleaned_tx['block_height'] = int(cleaned_tx['block_height'])
            cleaned_transactions.append(cleaned_tx)
        
        # Calculate summary statistics
        summary = {
            'total_transactions': len(cleaned_transactions),
            'total_donated': sum(safe_float(t['amount']) for t in cleaned_transactions if t['transaction_type'] == 'IN'),
            'total_disbursed': sum(safe_float(t['amount']) for t in cleaned_transactions if t['transaction_type'] == 'OUT'),
            'unique_donors': len(set(t['user'] for t in cleaned_transactions if t['transaction_type'] == 'IN')),
            'unique_recipients': len(set(t['user'] for t in cleaned_transactions if t['transaction_type'] == 'OUT')),
        }
        
        response = {
            'success': True,
            'summary': summary,
            'transactions': cleaned_transactions,
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/disburse', methods=['POST'])
@admin_required
def api_disburse():
    """API endpoint for disbursement."""
    data = request.get_json()
    try:
        result = disburse_zakat(
            recipient_id=data['recipient_id'],
            amount=float(data['amount']),
            zakat_type_id=int(data['zakat_type_id'])
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/verify-chain')
def api_verify_chain():
    """API endpoint to verify blockchain integrity."""
    try:
        is_valid = verify_chain_integrity()
        latest_height = get_latest_block_height()
        return jsonify({
            'valid': is_valid,
            'latest_block': latest_height,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/voucher/<voucher_code>.json')
def api_voucher_json(voucher_code):
    """Return voucher details as JSON."""
    # Get voucher transactions
    filters = {'voucher_code': voucher_code}
    transactions = read_ledger(filters)
    
    if not transactions:
        return jsonify({
            'success': False,
            'error': 'Voucher not found',
        }), 404
    
    # Group by type and calculate totals
    donations = []
    disbursements = []
    total_donated = 0
    total_disbursed = 0
    
    for tx in transactions:
        if tx['transaction_type'] == 'IN':
            donations.append(tx)
            total_donated += safe_float(tx['amount'])
        else:
            disbursements.append(tx)
            total_disbursed += safe_float(tx['amount'])
    
    # Determine status
    if total_disbursed >= total_donated:
        status = 'fully_disbursed'
    elif total_disbursed > 0:
        status = 'partially_disbursed'
    else:
        status = 'pending'
    
    return jsonify({
        'success': True,
        'voucher_code': voucher_code,
        'status': status,
        'total_donated': total_donated,
        'total_disbursed': total_disbursed,
        'remaining': total_donated - total_disbursed,
        'donations': donations,
        'disbursements': disbursements,
        'timestamp': datetime.now().isoformat()
    })

# Helper functions for blockchain-style ledger
def write_to_ledger(transaction_data):
    """Write a transaction to the blockchain-style ledger."""
    ledger_file = 'data/ledger.csv'
    file_exists = os.path.isfile(ledger_file)
    
    # Updated fieldnames for blockchain-style ledger
    fieldnames = [
        'transaction_id', 'block_height', 'block_hash', 'prev_block_hash',
        'transaction_type', 'timestamp', 'amount', 'user', 'email',
        'notes', 'voucher_code', 'zakat_type_id', 'zakat_type_name',
        'recipient_id', 'disbursement_type', 'signatures'
    ]
    
    # Initialize transaction data if needed
    transaction_data = {k: (transaction_data.get(k) or '') for k in fieldnames}
    
    # Get current block height
    current_height = 0
    if file_exists:
        try:
            with open(ledger_file, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        height = int(row.get('block_height', '0') or '0')
                        current_height = max(current_height, height)
                    except (ValueError, TypeError):
                        continue
        except Exception as e:
            print(f"Error reading block height: {e}")
            current_height = 0
    
    # Add blockchain metadata
    transaction_data['block_height'] = str(current_height + 1)  # Store as string for CSV
    transaction_data['signatures'] = json.dumps({
        'validator_1': hashlib.sha256(f"validator1{transaction_data}".encode()).hexdigest()[:16],
        'validator_2': hashlib.sha256(f"validator2{transaction_data}".encode()).hexdigest()[:16],
        'timestamp': datetime.now().isoformat()
    })
    
    # Generate block hash (includes previous hash for chain)
    block_data = f"{transaction_data['block_height']}{transaction_data['transaction_id']}{transaction_data['timestamp']}{transaction_data['amount']}"
    if current_height > 0:
        prev_hash = get_last_block_hash()
        block_data += prev_hash
        transaction_data['prev_block_hash'] = prev_hash
    else:
        # Genesis block
        transaction_data['prev_block_hash'] = hashlib.sha256("genesis".encode()).hexdigest()
    transaction_data['block_hash'] = hashlib.sha256(block_data.encode()).hexdigest()
    
    # Ensure all fields exist
    for field in fieldnames:
        if field not in transaction_data:
            transaction_data[field] = ''
    
    # Write in append-only mode to maintain immutability
    with open(ledger_file, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(transaction_data)

def read_ledger(filters=None):
    """Read transactions from the ledger, with optional filtering."""
    ledger_file = 'data/ledger.csv'
    if not os.path.isfile(ledger_file):
        # If the file doesn't exist, create an empty one with proper headers
        with open(ledger_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[
                'transaction_id', 'block_height', 'block_hash', 'prev_block_hash',
                'transaction_type', 'timestamp', 'amount', 'user', 'email',
                'notes', 'voucher_code', 'zakat_type_id', 'zakat_type_name',
                'recipient_id', 'disbursement_type', 'signatures'
            ])
            writer.writeheader()
        return []
    
    transactions = []
    try:
        with open(ledger_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Apply filters if provided
                if filters:
                    skip = False
                    for key, value in filters.items():
                        if value and key in row and str(value) != str(row.get(key, '')):
                            skip = True
                            break
                    if skip:
                        continue
                
                # Ensure block_height is always a valid integer
                try:
                    row['block_height'] = int(row.get('block_height', '0') or '0')
                except (ValueError, TypeError):
                    row['block_height'] = 0
                
                transactions.append(row)
    except Exception as e:
        print(f"Error reading ledger: {e}")
        return []
    
    # Sort by block height (newest first)
    transactions.sort(key=lambda x: x['block_height'], reverse=True)
    return transactions

def get_last_block_hash():
    """Get the hash of the last block in the chain."""
    ledger_file = 'data/ledger.csv'
    if not os.path.isfile(ledger_file):
        return hashlib.sha256("genesis".encode()).hexdigest()
    
    with open(ledger_file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        last_hash = hashlib.sha256("genesis".encode()).hexdigest()
        for row in reader:
            if 'block_hash' in row:
                last_hash = row['block_hash']
    return last_hash

def verify_chain_integrity():
    """Verify the integrity of the entire blockchain."""
    ledger_file = 'data/ledger.csv'
    
    with open(ledger_file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        prev_hash = hashlib.sha256("genesis".encode()).hexdigest()
        for row in reader:
            # Verify block hash
            block_data = f"{row['block_height']}{row['transaction_id']}{row['timestamp']}{row['amount']}{prev_hash}"
            calculated_hash = hashlib.sha256(block_data.encode()).hexdigest()
            if calculated_hash != row['block_hash']:
                return False
            
            # Verify previous hash
            if row['prev_block_hash'] != prev_hash:
                return False
            
            # Verify signatures (simplified)
            try:
                signatures = json.loads(row['signatures'])
                if not signatures.get('validator_1') or not signatures.get('validator_2'):
                    return False
            except:
                return False
            
            prev_hash = row['block_hash']
    return True

def format_amount(amount):
    """Format amount in RM."""
    try:
        return f"RM {float(amount):,.2f}"
    except (ValueError, TypeError):
        return "RM 0.00"

# Add template filters
@app.template_filter('format_amount')
def format_amount_filter(amount):
    """Format amount in RM for templates."""
    try:
        return f"RM {float(amount):,.2f}"
    except (ValueError, TypeError):
        return "RM 0.00"

@app.template_filter('attr_from_dict')
def attr_from_dict(id_val, dictionary, attr, default=None):
    """Get an attribute from a dictionary using ID as key"""
    try:
        id_val = int(id_val) if id_val else 0
        item = dictionary.get(id_val, {})
        return item.get(attr, default)
    except (ValueError, TypeError):
        return default

@app.context_processor
def inject_utility_functions():
    """Make utility functions available to all templates"""
    return {
        'format_amount': format_amount,  # Make format_amount available to templates
        'zakat_types': app.config['ZAKAT_TYPES'],
        'zakat_types_by_id': app.config['ZAKAT_TYPES_BY_ID']
    }

if __name__ == '__main__':
    app.run(debug=True)
