import os
from OpenSSL import crypto
from datetime import datetime
from dateutil import parser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class CertificateCheckerApp:
    def __init__(self, root):
        self.root = root
        self.current_language = "ru"
        self.translations = {
            "ru": {
                "title": "Проверка сертификатов",
                "folder_frame": "Путь к сертификатам",
                "settings_frame": "Настройки поиска",
                "revoke_interval": "Интервал отзыва (дней)",
                "search_button": "ПОИСК",
                "file_column": "Имя файла",
                "expiry_column": "Дата истечения",
                "days_left_column": "Дней осталось",
                "issuer_column": "Издатель",
                "subject_column": "Владелец",
                "serial_column": "Серийный номер",
                "status_ready": "Готов к работе",
                "error_no_folder": "Укажите правильную папку с сертификатами!",
                "select_folder_button": "Выбрать",
                "scanning_status": "Проверяю сертификаты в {}...",
                "done_status": "Готово. Найдено {} сертификатов, истекающих в ближайшие {} дней.",
                "error_status": "Ошибка при проверке",
                "copy_button": "Копировать",
                "copy_success": "Данные скопированы в буфер!"
            },
            "en": {
                "title": "Certificate Checker",
                "folder_frame": "Certificate Folder",
                "settings_frame": "Search Settings",
                "revoke_interval": "Expiry Threshold (days)",
                "search_button": "SEARCH",
                "file_column": "File Name",
                "expiry_column": "Expiry Date",
                "days_left_column": "Days Left",
                "issuer_column": "Issuer",
                "subject_column": "Subject",
                "serial_column": "Serial Number",
                "status_ready": "Ready",
                "error_no_folder": "Select a valid certificate folder!",
                "select_folder_button": "Browse",
                "scanning_status": "Scanning certificates in {}...",
                "done_status": "Done. Found {} certificates expiring in the next {} days.",
                "error_status": "Error during scan",
                "copy_button": "Copy",
                "copy_success": "Data copied to clipboard!"
            }
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        self.root.title(self.translations[self.current_language]["title"])
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        
        try:
            self.root.iconbitmap("cert_icon.ico")
        except:
            pass
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Folder selection frame
        frame_folder = ttk.LabelFrame(main_frame, 
                                   text=self.translations[self.current_language]["folder_frame"])
        frame_folder.pack(fill=tk.X, pady=5)
        
        self.folder_path = tk.StringVar()
        ttk.Entry(frame_folder, textvariable=self.folder_path, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_folder, 
                 text=self.translations[self.current_language]["select_folder_button"],
                 command=self.select_folder).pack(side=tk.LEFT)
        
        # Settings frame
        frame_settings = ttk.LabelFrame(main_frame,
                                     text=self.translations[self.current_language]["settings_frame"])
        frame_settings.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame_settings, 
                text=self.translations[self.current_language]["revoke_interval"]).pack(side=tk.LEFT)
        self.days_before = tk.IntVar(value=30)
        ttk.Spinbox(frame_settings, from_=1, to=365, 
                  textvariable=self.days_before, width=5).pack(side=tk.LEFT, padx=5)
        
        # Buttons frame
        frame_buttons = ttk.Frame(main_frame)
        frame_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Button(frame_buttons,
                 text=self.translations[self.current_language]["search_button"],
                 command=self.run_check).pack(side=tk.LEFT)
        
        ttk.Button(frame_buttons,
                 text=self.translations[self.current_language]["copy_button"],
                 command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=10)
        
        # Treeview with scrollbars
        frame_tree = ttk.Frame(main_frame)
        frame_tree.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(frame_tree, columns=("file", "expiry", "days_left", "issuer", "subject", "serial"), 
                               show="headings")
        
        # Configure columns
        columns = {
            "file": {"width": 200, "anchor": tk.W},
            "expiry": {"width": 120, "anchor": tk.CENTER},
            "days_left": {"width": 100, "anchor": tk.CENTER},
            "issuer": {"width": 200, "anchor": tk.W},
            "subject": {"width": 200, "anchor": tk.W},
            "serial": {"width": 120, "anchor": tk.CENTER}
        }
        
        for col, params in columns.items():
            self.tree.heading(col, text=self.translations[self.current_language][f"{col}_column"])
            self.tree.column(col, **params)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(frame_tree, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        
        frame_tree.grid_rowconfigure(0, weight=1)
        frame_tree.grid_columnconfigure(0, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar(value=self.translations[self.current_language]["status_ready"])
        ttk.Label(main_frame, textvariable=self.status_var, 
                relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X, pady=(5,0))
        
        # Language switch
        ttk.Button(main_frame, text="EN/RU", width=6,
                 command=self.toggle_language).pack(side=tk.RIGHT, pady=5)
    
    def select_folder(self):
        folder = filedialog.askdirectory(title=self.translations[self.current_language]["select_folder_button"])
        if folder:
            self.folder_path.set(folder)
    
    def get_cert_info(self, cert_path):
        try:
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
            
            cert = crypto.load_certificate(crypto.FILETYPE_ASN1, cert_data)
            
            expiry_date = parser.parse(cert.get_notAfter().decode('ascii')).replace(tzinfo=None)
            issuer = cert.get_issuer().CN or "N/A"
            subject = cert.get_subject().CN or "N/A"
            serial = cert.get_serial_number()
            
            return {
                "expiry": expiry_date,
                "issuer": issuer,
                "subject": subject,
                "serial": f"{serial:X}"  # Convert to hex string
            }
        except Exception as e:
            raise ValueError(f"Certificate read error: {str(e)}")
    
    def run_check(self):
        folder = self.folder_path.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror(
                self.translations[self.current_language]["title"],
                self.translations[self.current_language]["error_no_folder"]
            )
            return
        
        self.clear_table()
        days_threshold = self.days_before.get()
        
        self.status_var.set(self.translations[self.current_language]["scanning_status"].format(folder))
        self.root.update_idletasks()
        
        try:
            count = 0
            for filename in os.listdir(folder):
                if filename.lower().endswith(('.cer', '.pem', '.crt')):
                    cert_path = os.path.join(folder, filename)
                    
                    try:
                        cert_info = self.get_cert_info(cert_path)
                        days_left = (cert_info["expiry"] - datetime.now()).days
                        
                        if days_left <= days_threshold:
                            self.add_to_table(
                                filename,
                                cert_info["expiry"].strftime('%Y-%m-%d'),
                                days_left,
                                cert_info["issuer"],
                                cert_info["subject"],
                                cert_info["serial"]
                            )
                            count += 1
                    except Exception as e:
                        self.add_to_table(
                            filename,
                            str(e),
                            "N/A",
                            "N/A",
                            "N/A",
                            "N/A"
                        )
            
            self.status_var.set(
                self.translations[self.current_language]["done_status"].format(count, days_threshold)
            )
        except Exception as e:
            messagebox.showerror(
                self.translations[self.current_language]["title"],
                f"{self.translations[self.current_language]['error_status']}: {str(e)}"
            )
            self.status_var.set(self.translations[self.current_language]["error_status"])
    
    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def add_to_table(self, filename, expiry, days_left, issuer, subject, serial):
        self.tree.insert("", tk.END, values=(
            filename,
            expiry,
            days_left,
            issuer,
            subject,
            serial
        ))
    
    def copy_to_clipboard(self):
        if not self.tree.get_children():
            messagebox.showwarning(
                self.translations[self.current_language]["title"],
                "No data to copy!"
            )
            return
        
        clipboard_text = []
        
        # Add headers
        headers = [
            self.translations[self.current_language]["file_column"],
            self.translations[self.current_language]["expiry_column"],
            self.translations[self.current_language]["days_left_column"],
            self.translations[self.current_language]["issuer_column"],
            self.translations[self.current_language]["subject_column"],
            self.translations[self.current_language]["serial_column"]
        ]
        clipboard_text.append("\t".join(headers))
        
        # Add rows
        for item in self.tree.get_children():
            row = self.tree.item(item)['values']
            clipboard_text.append("\t".join(map(str, row)))
        
        # Copy to clipboard
        self.root.clipboard_clear()
        self.root.clipboard_append("\n".join(clipboard_text))
        
        messagebox.showinfo(
            self.translations[self.current_language]["title"],
            self.translations[self.current_language]["copy_success"]
        )
    
    def toggle_language(self):
        self.current_language = "en" if self.current_language == "ru" else "ru"
        self.update_ui_text()
    
    def update_ui_text(self):
        lang = self.current_language
        texts = self.translations[lang]
        
        self.root.title(texts["title"])
        
        # Update all widgets
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                if "folder_frame" in widget.cget("text"):
                    widget.config(text=texts["folder_frame"])
                elif "settings_frame" in widget.cget("text"):
                    widget.config(text=texts["settings_frame"])
        
        # Update treeview headers
        for col in ["file", "expiry", "days_left", "issuer", "subject", "serial"]:
            self.tree.heading(col, text=texts[f"{col}_column"])
        
        # Update status
        self.status_var.set(texts["status_ready"])

if __name__ == "__main__":
    root = tk.Tk()
    app = CertificateCheckerApp(root)
    root.mainloop()
    