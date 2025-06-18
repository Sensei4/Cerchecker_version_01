import os
from OpenSSL import crypto
from datetime import datetime
from dateutil import parser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class CertificateCheckerApp:
    def __init__(self, root):
        self.root = root
        self.current_language = "ru"  # Default Russian
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
                "status_ready": "Готов к работе",
                "error_no_folder": "Укажите правильную папку с сертификатами!",
                "select_folder_button": "Выбрать",
                "scanning_status": "Проверяю сертификаты в {}...",
                "done_status": "Готово. Найдено {} сертификатов, истекающих в ближайшие {} дней.",
                "error_status": "Ошибка при проверке"
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
                "status_ready": "Ready",
                "error_no_folder": "Select a valid certificate folder!",
                "select_folder_button": "Browse",
                "scanning_status": "Scanning certificates in {}...",
                "done_status": "Done. Found {} certificates expiring in the next {} days.",
                "error_status": "Error during scan"
            }
        }
        
        self.root.title(self.translations[self.current_language]["title"])
        self.root.geometry("600x400")
        
        try:
            self.root.iconbitmap("cert_icon.ico")
        except:
            pass
        
        self.create_widgets()
    
    def create_widgets(self):
        # Frame for selecting a folder
        frame_folder = ttk.LabelFrame(self.root, text=self.translations[self.current_language]["folder_frame"], padding=10)
        frame_folder.pack(fill=tk.X, padx=10, pady=5)
        
        self.folder_path = tk.StringVar()
        ttk.Entry(frame_folder, textvariable=self.folder_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_folder, text=self.translations[self.current_language]["select_folder_button"], 
                 command=self.select_folder).pack(side=tk.LEFT)
        
        # Frame for settings
        frame_settings = ttk.LabelFrame(self.root, text=self.translations[self.current_language]["settings_frame"], padding=10)
        frame_settings.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frame_settings, text=self.translations[self.current_language]["revoke_interval"]).pack(side=tk.LEFT)
        self.days_before = tk.IntVar(value=20)
        ttk.Spinbox(frame_settings, from_=1, to=365, textvariable=self.days_before, width=5).pack(side=tk.LEFT, padx=5)
        
        # Check button
        ttk.Button(self.root, text=self.translations[self.current_language]["search_button"], 
                 command=self.run_check).pack(pady=10)
        
        # Table for results
        self.tree = ttk.Treeview(self.root, columns=("file", "expiry", "days_left"), show="headings")
        self.tree.heading("file", text=self.translations[self.current_language]["file_column"])
        self.tree.heading("expiry", text=self.translations[self.current_language]["expiry_column"])
        self.tree.heading("days_left", text=self.translations[self.current_language]["days_left_column"])
        self.tree.column("file", width=200)
        self.tree.column("expiry", width=150)
        self.tree.column("days_left", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value=self.translations[self.current_language]["status_ready"])
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X, padx=10, pady=5)

        # Language switch button
        self.lang_button = ttk.Button(
            self.root, 
            text="En", 
            command=self.toggle_language,
            width=3
        )
        self.lang_button.place(relx=0.95, rely=0.02, anchor=tk.NE)
    
    def select_folder(self):
        folder = filedialog.askdirectory(title=self.translations[self.current_language]["select_folder_button"])
        if folder:
            self.folder_path.set(folder)
            self.status_var.set(f"{self.translations[self.current_language]['folder_frame']}: {folder}")
    
    def get_cert_expiry_date(self, cert_path):
        with open(cert_path, 'rb') as f:
            cert_data = f.read()
        cert = crypto.load_certificate(crypto.FILETYPE_ASN1, cert_data)
        expiry_date = parser.parse(cert.get_notAfter().decode('ascii'))
        return expiry_date.replace(tzinfo=None)
    
    def run_check(self):
        folder = self.folder_path.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror(
                self.translations[self.current_language]["title"],
                self.translations[self.current_language]["error_no_folder"]
            )
            return
        
        # Clearing previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        days = self.days_before.get()
        self.status_var.set(self.translations[self.current_language]["scanning_status"].format(folder))
        self.root.update()
        
        try:
            count = 0
            for filename in os.listdir(folder):
                if filename.lower().endswith('.cer'):
                    cert_path = os.path.join(folder, filename)
                    try:
                        expiry_date = self.get_cert_expiry_date(cert_path)
                        days_left = (expiry_date - datetime.now()).days
                        
                        if 0 <= days_left <= days:
                            self.tree.insert("", tk.END, values=(
                                filename,
                                expiry_date.strftime('%Y-%m-%d'),
                                days_left
                            ))
                            count += 1
                    except Exception as e:
                        self.tree.insert("", tk.END, values=(
                            filename,
                            f"{self.translations[self.current_language]['error_status']}: {str(e)}",
                            "N/A"
                        ))
            
            self.status_var.set(self.translations[self.current_language]["done_status"].format(count, days))
        except Exception as e:
            messagebox.showerror(
                self.translations[self.current_language]["title"],
                f"{self.translations[self.current_language]['error_status']}: {str(e)}"
            )
            self.status_var.set(self.translations[self.current_language]["error_status"])
    
    def toggle_language(self):
        """Переключает язык между русским и английским."""
        self.current_language = "en" if self.current_language == "ru" else "ru"
        self.update_ui_texts()
        self.lang_button.config(text="Ru" if self.current_language == "en" else "En")

    def update_ui_texts(self):
        """Обновляет все текстовые элементы интерфейса."""
        lang = self.current_language
        texts = self.translations[lang]
        
        self.root.title(texts["title"])
        
        # Updating frames
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                if widget.cget("text") in [self.translations["ru"]["folder_frame"], 
                                          self.translations["en"]["folder_frame"],
                                          self.translations["ru"]["settings_frame"],
                                          self.translations["en"]["settings_frame"]]:
                    if widget.cget("text") == self.translations["ru"]["folder_frame"]:
                        widget.config(text=texts["folder_frame"])
                    elif widget.cget("text") == self.translations["en"]["folder_frame"]:
                        widget.config(text=texts["folder_frame"])
                    elif widget.cget("text") == self.translations["ru"]["settings_frame"]:
                        widget.config(text=texts["settings_frame"])
                    elif widget.cget("text") == self.translations["en"]["settings_frame"]:
                        widget.config(text=texts["settings_frame"])
        
        # Updating the table
        self.tree.heading("file", text=texts["file_column"])
        self.tree.heading("expiry", text=texts["expiry_column"])
        self.tree.heading("days_left", text=texts["days_left_column"])
        
        # Updating buttons
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                if widget.cget("text") in [self.translations["ru"]["search_button"], 
                                        self.translations["en"]["search_button"],
                                        self.translations["ru"]["select_folder_button"],
                                        self.translations["en"]["select_folder_button"]]:
                    if widget.cget("text") == self.translations["ru"]["search_button"]:
                        widget.config(text=texts["search_button"])
                    elif widget.cget("text") == self.translations["en"]["search_button"]:
                        widget.config(text=texts["search_button"])
                    elif widget.cget("text") == self.translations["ru"]["select_folder_button"]:
                        widget.config(text=texts["select_folder_button"])
                    elif widget.cget("text") == self.translations["en"]["select_folder_button"]:
                        widget.config(text=texts["select_folder_button"])
        
        # Updating the status
        self.status_var.set(texts["status_ready"])

if __name__ == "__main__":
    root = tk.Tk()
    app = CertificateCheckerApp(root)
    root.mainloop()
