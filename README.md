# Certificate Checker  

A GUI application for checking SSL/TLS certificate expiration dates in bulk with multilingual support (English/Russian). 

# Features  
    🗂️ Scan folders for .cer certificate files
    📅 Check expiration dates of certificates
    🔍 Filter certificates expiring within a specified timeframe
    🌍 Bilingual interface (English/Russian)
    📊 Results displayed in sortable table
    🚦 Status bar with operation progress  

# Usage  
1. Run the application:
    bash
    python main.py

2. In the application:
    Click "Browse" to select a folder containing certificates
    Set the expiration threshold (in days)
    Click "SEARCH" to scan certificates
    Use the "En/Ru" button to toggle between English and Russian interfaces

## Requirements  
    Python 3.8+
    pyOpenSSL (for certificate parsing)
    tkinter (included with Python)
    python-dateutil (for date handling)

# License  
MIT  
