import os
import shutil
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from system_logger import LogType, StatusCode, SystemLogger

# Yedekleme işlemlerini yapan thread fonksiyonu
def backup_thread(file_path, handler, progress_callback):
    try:
        handler.backup_file(file_path)
        progress_callback("Başarıyla yedeklendi: " + file_path)
    except Exception as e:
        progress_callback(f"Hata oluştu: {str(e)}")

class BackupHandler(FileSystemEventHandler):
    def __init__(self, username, source_dir, backup_dir, progress_callback=None):
        self.username = username
        self.source_dir = source_dir
        self.backup_dir = os.path.join(backup_dir, username)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.logger = SystemLogger(current_dir)
        self.progress_callback = progress_callback

    def on_modified(self, event):
        if not event.is_directory:
            self.backup_file(event.src_path)

    def backup_file(self, file_path):
        start_time = datetime.now()
        try:
            relative_path = os.path.relpath(file_path, self.source_dir)
            backup_path = os.path.join(self.backup_dir, relative_path)
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(file_path, backup_path)
            
            end_time = datetime.now()
            file_size = os.path.getsize(file_path)
            self.logger.log_backup(
                username=self.username,
                status=StatusCode.SUCCESS,
                source_dir=file_path,
                data_size=file_size,
                details={
                    'start_time': start_time,
                    'end_time': end_time,
                    'backup_path': backup_path,
                    'operation_details': 'Yedekleme işlemi başarılı'
                }
            )
        except Exception as e:
            self.logger.log_backup(
                username=self.username,
                status=StatusCode.FAILED,
                source_dir=file_path,
                data_size=os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                details={
                    'start_time': start_time,
                    'end_time': datetime.now(),
                    'error_message': str(e),
                    'operation_details': 'Yedekleme işlemi başarısız'
                }
            )
            raise

class BackupInterface:
    def __init__(self, parent_window, username):
        self.parent_window = parent_window
        self.username = username
        self.window = None
        self.setup_directories()
        self.observer = None

    def setup_directories(self):
        self.user_source_dir = os.path.join("uploads", self.username)
        self.user_backup_dir = os.path.join("backups", self.username)
        os.makedirs(self.user_source_dir, exist_ok=True)
        os.makedirs(self.user_backup_dir, exist_ok=True)
        
    def show_backup_window(self):
        if self.window is None:
            self.window = tk.Toplevel(self.parent_window)
            self.window.title(f"Dosya Yedekleme - {self.username}")
            self.window.geometry("500x400")
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            x = (screen_width - 500) // 2
            y = (screen_height - 400) // 2
            self.window.geometry(f"500x400+{x}+{y}")
            
            tk.Label(self.window, 
                     text=f"{self.username} - Yedekleme Sistemi", 
                     font=("Arial", 14, "bold")).pack(pady=20)
            
            tk.Button(self.window, 
                     text="Manuel Yedekleme", 
                     width=25,
                     command=self.handle_manual_backup).pack(pady=10)
            
            tk.Button(self.window, 
                     text="Otomatik Yedekleme", 
                     width=25,
                     command=self.handle_auto_backup).pack(pady=10)
            
            tk.Button(self.window, 
                     text="Ana Menüye Dön", 
                     width=25,
                     command=self.close_window).pack(pady=10)
            
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.transient(self.parent_window)
            self.window.grab_set()

            # İlerleme için Label ekleniyor
            self.progress_label = tk.Label(self.window, text="İlerleme: 0%", font=("Arial", 10))
            self.progress_label.pack(pady=10)

    def update_progress(self, message):
        # İlerleme label'ını günceller
        self.progress_label.config(text=message)

    def handle_manual_backup(self):
        files = filedialog.askopenfilenames(
            initialdir=self.user_source_dir,
            title=f"{self.username} - Yedeklenecek Dosyaları Seçin",
            filetypes=(("Tüm dosyalar", "*.*"),)
        )
        
        if files:
            handler = BackupHandler(self.username, self.user_source_dir, "backups", progress_callback=self.update_progress)
            for file_path in files:
                # Her dosya için bir thread başlatıyoruz
                threading.Thread(target=backup_thread, args=(file_path, handler, self.update_progress)).start()
                self.window.grab_set()

    def handle_auto_backup(self):
        handler = BackupHandler(self.username, self.user_source_dir, "backups", progress_callback=self.update_progress)
        for root, _, files in os.walk(self.user_source_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                threading.Thread(target=backup_thread, args=(file_path, handler, self.update_progress)).start()
        messagebox.showinfo("Başarılı", "Tüm dosyalar başarıyla yedeklendi!")

    def close_window(self):
        if self.window:
            self.window.grab_release()
            self.window.destroy()
            self.window = None
            if self.observer:
                self.observer.stop()
                self.observer.join()
