# Troubleshooting Guide

This document provides solutions for common issues you might encounter when setting up and running the Zakat DAO application.

## Installation Issues

### Missing 'distutils' Module

**Error Message:**
```
ModuleNotFoundError: No module named 'distutils'
```

**Solution:**
This error commonly occurs in Python 3.12+ where distutils was removed from the standard library.

1. Reinstall setuptools with the proper dependencies:
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   ```

2. Run the installation script again:
   ```bash
   ./install_dependencies.sh
   ```

### Setuptools ImpImporter Error with Python 3.12

**Error Message:**
```
AttributeError: module 'pkgutil' has no attribute 'ImpImporter'. Did you mean: 'zipimporter'?
```

**Solution:**
This error occurs because older versions of setuptools are not compatible with Python 3.12.

1. Manually install a compatible version of setuptools first:
   ```bash
   pip install --upgrade "setuptools>=65.5.0"
   ```

2. Then install other dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Alternatively, create a fresh virtual environment with Python 3.11 or earlier:
   ```bash
   # For macOS/Linux
   python3.11 -m venv venv
   source venv/bin/activate
   
   # For Windows
   python3.11 -m venv venv
   venv\Scripts\activate
   ```

### Pillow or QR Code Installation Failures

**Error Message:**
```
Failed building wheel for pillow
```

**Solution:**
This usually indicates missing system dependencies required for image processing.

For macOS:
```bash
brew install libjpeg zlib
```

For Ubuntu/Debian:
```bash
sudo apt-get install python3-dev python3-pil.imagetk libjpeg-dev zlib1g-dev
```

### Permission Denied When Running Installation Script

**Error Message:**
```
bash: ./install_dependencies.sh: Permission denied
```

**Solution:**
Make the script executable:
```bash
chmod +x install_dependencies.sh
```

## Runtime Issues

### Application Won't Start

**Error Message:**
```
Address already in use
```

**Solution:**
Another application is using port 5000. You can:
1. Close the other application
2. Modify the app to use a different port:
   ```python
   if __name__ == '__main__':
       app.run(debug=True, port=5001)  # Change 5001 to any available port
   ```

### QR Code Generation Not Working

**Error Message:**
```
QR code generation is not available
```

**Solution:**
Install the required QR code dependencies:
```bash
pip install qrcode[pil]
```

## Data Issues

### Ledger Migration Errors

**Error Message:**
```
Ledger migration failed due to incompatible data format.
```

**Solution:**
This error occurs when the ledger file format is incompatible with the current application version.

1. Back up your existing data:
   ```bash
   cp data/ledger.csv data/ledger.csv.backup
   ```

2. Check the ledger file for formatting issues:
   - Ensure the file uses UTF-8 encoding.
   - Verify that all columns match the expected schema.

3. Reset the ledger (caution: this deletes all transaction data):
   ```bash
   rm data/ledger.csv
   ```

4. Restart the application to create a fresh ledger file.

5. If the issue persists, contact support with the following details:
   - A copy of your ledger file
   - Application version
   - Python version
   - Operating system details

## For Further Help

If you continue to experience issues, please create an issue on the GitHub repository with:
- Your operating system and version
- Python version (`python --version`)
- Full error message
- Steps to reproduce the issue
