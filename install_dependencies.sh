#!/bin/bash

echo "Installing Zakat DAO dependencies..."

# Check if we're running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS environment"
    
    # Check for Python
    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &>/dev/null; then
        PYTHON_CMD="python"
    else
        echo "Error: Python not found. Please install Python first."
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d" " -f2)
    echo "Found Python version: $PYTHON_VERSION"
    
    # Handle compatibility issues with Python 3.12+
    if [[ "$PYTHON_VERSION" == 3.12* ]]; then
        echo "Python 3.12 detected - installing compatible setuptools version first"
        $PYTHON_CMD -m pip install --upgrade pip wheel
        $PYTHON_CMD -m pip install --upgrade "setuptools>=65.5.0" --force-reinstall
        
        echo "Installing compatible version of Pillow"
        $PYTHON_CMD -m pip install "Pillow>=10.1.0"
    else
        # For Python 3.11 and earlier
        echo "Installing setuptools"
        $PYTHON_CMD -m pip install --upgrade pip setuptools wheel
    fi
    
    # Check if pip is installed
    if command -v pip3 &>/dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &>/dev/null; then
        PIP_CMD="pip"
    else
        echo "Installing pip..."
        $PYTHON_CMD -m ensurepip --upgrade
        PIP_CMD="$PYTHON_CMD -m pip"
    fi

else
    # Non-macOS systems
    # Check if pip is installed
    if command -v pip &>/dev/null; then
        PIP_CMD="pip"
    elif command -v pip3 &>/dev/null; then
        PIP_CMD="pip3"
    else
        echo "Error: pip or pip3 not found. Please install Python and pip first."
        exit 1
    fi
    
    # Check Python version
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d" " -f2)
        
        if [[ "$PYTHON_VERSION" == 3.12* ]]; then
            echo "Python 3.12 detected - installing compatible setuptools version first"
            python3 -m pip install --upgrade pip wheel
            python3 -m pip install --upgrade "setuptools>=65.5.0" --force-reinstall
        fi
    fi
fi

# Ensure pip is up to date
echo "Updating pip..."
$PIP_CMD install --upgrade pip

# Install dependencies individually for better error handling
echo "Installing required Python packages..."
echo "1/4: Installing base packages..."
$PIP_CMD install Flask==2.3.3 || {
    echo "Flask installation failed. Trying without version constraint..."
    $PIP_CMD install Flask
}

echo "2/4: Installing setuptools and wheel..."
$PIP_CMD install "setuptools>=65.5.0" wheel || {
    echo "Warning: Could not install latest setuptools. Continuing with current version."
}

echo "3/4: Installing Pillow..."
$PIP_CMD install "Pillow>=10.1.0" || {
    echo "Pillow installation failed. You may need additional system packages."
    echo "For macOS: brew install libjpeg zlib"
    echo "For Ubuntu/Debian: sudo apt-get install python3-dev python3-pil.imagetk libjpeg-dev zlib1g-dev"
    # Continue anyway
}

echo "4/4: Installing qrcode and numpy..."
$PIP_CMD install qrcode==7.4.2 numpy==1.24.3 || {
    echo "Warning: Could not install qrcode or numpy. Some features may not work correctly."
}

# Creating a test file to verify a successful installation
echo "Verifying installation..."
cat > test_install.py << EOL
try:
    import flask
    print("Flask installed successfully!")
    
    try:
        import PIL
        print("Pillow installed successfully!")
    except ImportError:
        print("WARNING: Pillow not installed. QR code generation will not work.")
    
    try:
        import qrcode
        print("QR code module installed successfully!")
    except ImportError:
        print("WARNING: QR code module not installed. QR code generation will not work.")
    
    try:
        import numpy
        print("NumPy installed successfully!")
    except ImportError:
        print("WARNING: NumPy not installed. Some AI features may not work properly.")
        
    print("\nCongratulations! Base requirements are met to run the application.")
    print("You can now start the application with: python app.py")
except ImportError:
    print("ERROR: Flask not installed. Application will not run.")
    print("Please check the error messages above and refer to TROUBLESHOOTING.md")
EOL

# Run the test file
$PYTHON_CMD test_install.py
rm test_install.py  # Clean up

echo ""
echo "Blockchain-style Ledger Features:"
echo "--------------------------------"
echo "- View the public ledger at: http://127.0.0.1:5000/ledger"
echo "- Check voucher status at: http://127.0.0.1:5000/voucher/<voucher-id>"
echo "- Access JSON API at: http://127.0.0.1:5000/api/ledger.json"
echo "- Admin interface at: http://127.0.0.1:5000/admin (username: admin, password: admin123)"
echo "- AI Disbursement at: http://127.0.0.1:5000/admin/ai-disbursement"
echo ""
echo "Note: The ledger.csv file in the data directory simulates a blockchain and is append-only"
echo "for immutability. Each transaction is linked to previous ones via hash references."
echo ""
echo "If you encounter any issues, please refer to the TROUBLESHOOTING.md file."
