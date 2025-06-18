# Certificate Checker  

![Screenshot](screenshot.png)  

A simple GUI tool to check SSL/TLS certificate expiration dates in bulk.  

## Features  
- Scan `.cer` files in a selected folder.  
- Filter certificates expiring within a specified days range.  
- Clear table view with sorting.  

## Usage  
1. Run `main.py`.  
2. Select a folder containing certificates.  
3. Set the "days before expiry" threshold.  
4. Click **"ПОИСК"** (Search) to see results.  

## Requirements  
- Python 3.x  
- `pyOpenSSL`  
- `tkinter` (included in Python)  
- Optional: `Pillow` for custom icons  

## License  
MIT  