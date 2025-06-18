import os
from OpenSSL import crypto
from datetime import datetime
from dateutil import parser, relativedelta
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk  # Для иконок (опционально)

class CertificateCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Проверка сертификатов")
        self.root.geometry("600x400")
        
        # Иконка (опционально)
        try:
            self.root.iconbitmap("cert_icon.ico")  # Или используйте .png через Pillow
        except:
            pass
        
        self.create_widgets()
    
    def create_widgets(self):
        # Фрейм для выбора папки
        frame_folder = ttk.LabelFrame(self.root, text="Путь к сертификатам", padding=10)
        frame_folder.pack(fill=tk.X, padx=10, pady=5)
        
        self.folder_path = tk.StringVar()
        ttk.Entry(frame_folder, textvariable=self.folder_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_folder, text="Выбрать", command=self.select_folder).pack(side=tk.LEFT)
        
        # Фрейм для настроек
        frame_settings = ttk.LabelFrame(self.root, text="Настройки поиска", padding=10)
        frame_settings.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frame_settings, text="Интервал отзыва").pack(side=tk.LEFT)
        self.days_before = tk.IntVar(value=20)
        ttk.Spinbox(frame_settings, from_=1, to=365, textvariable=self.days_before, width=5).pack(side=tk.LEFT, padx=5)
        
        # Кнопка проверки
        ttk.Button(self.root, text="ПОИСК", command=self.run_check).pack(pady=10)
        
        # Таблица для результатов
        self.tree = ttk.Treeview(self.root, columns=("file", "expiry", "days_left"), show="headings")
        self.tree.heading("file", text="Имя файла")
        self.tree.heading("expiry", text="Дата истечения")
        self.tree.heading("days_left", text="Дней осталось")
        self.tree.column("file", width=200)
        self.tree.column("expiry", width=150)
        self.tree.column("days_left", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X, padx=10, pady=5)
    
    def select_folder(self):
        folder = filedialog.askdirectory(title="Выберите папку с сертификатами")
        if folder:
            self.folder_path.set(folder)
            self.status_var.set(f"Выбрана папка: {folder}")
    
    def get_cert_expiry_date(self, cert_path):
        with open(cert_path, 'rb') as f:
            cert_data = f.read()
        cert = crypto.load_certificate(crypto.FILETYPE_ASN1, cert_data)
        expiry_date = parser.parse(cert.get_notAfter().decode('ascii'))
        return expiry_date.replace(tzinfo=None)
    
    def run_check(self):
        folder = self.folder_path.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Ошибка", "Укажите правильную папку с сертификатами!")
            return
        
        # Очищаем предыдущие результаты
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        days = self.days_before.get()
        self.status_var.set(f"Проверяю сертификаты в {folder}...")
        self.root.update()  # Обновляем интерфейс
        
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
                            f"Ошибка: {str(e)}",
                            "N/A"
                        ))
            
            self.status_var.set(f"Готово. Найдено {count} сертификатов, истекающих в ближайшие {days} дней.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось проверить сертификаты: {str(e)}")
            self.status_var.set("Ошибка при проверке")

if __name__ == "__main__":
    root = tk.Tk()
    app = CertificateCheckerApp(root)
    root.mainloop()