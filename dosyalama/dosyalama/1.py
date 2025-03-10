import tkinter as tk
from tkinter import messagebox
from tkinter import messagebox, ttk
from datetime import datetime


from tkinter.ttk import Combobox 
from tkinter import Toplevel, Label
from file_operations import FileOperations
import bcrypt
from team_Management import TeamManagement
from admin_operations import AdminOperations
#from backup_module import handle_backup_button
from backup_module import BackupInterface
from system_logger import LogType,StatusCode,SystemLogger

#from backup_sync_module import create_backup_instance  # Yeni modülü import et

import os

class File:
    def __init__(self, root):
        self.root = root
        self.root.title("Dosya Depolama ve Yedekleme Sistemi")
        root.geometry('800x500')
        
        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.team_manager = TeamManagement(self.root_path)
        self.logger=SystemLogger(".")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.logger = SystemLogger(current_dir)


        # Login frame
        self.login_frame = tk.Frame(root)
        self.login_frame.grid(row=0, column=0, padx=10, pady=10)

        # Registration frame
        self.register_frame = tk.Frame(root)

        # Initially show login frame
        self.show_login_frame()

    def show_login_frame(self):
        self.register_frame.grid_remove()
        self.login_frame.grid()

        tk.Label(self.login_frame, text="Giriş Yap").grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(self.login_frame, text="Kullanıcı Adı:").grid(row=1, column=0, padx=10, pady=10)
        self.login_username = tk.Entry(self.login_frame, width=30)
        self.login_username.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.login_frame, text="Şifre:").grid(row=2, column=0, padx=10, pady=10)
        self.login_password = tk.Entry(self.login_frame, width=30, show="*")
        self.login_password.grid(row=2, column=1, padx=10, pady=10)

        tk.Button(self.login_frame, text="Giriş Yap", command=self.girisYap).grid(row=3, column=1, pady=10)
        tk.Button(self.login_frame, text="Hesabınız yok mu? Kayıt olun", command=self.show_register_frame).grid(row=4, column=1, pady=10)

    def show_register_frame(self):
        self.login_frame.grid_remove()
        self.register_frame.grid()

        tk.Label(self.register_frame, text="Kayıt Ol").grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(self.register_frame, text="Kullanıcı Adı:").grid(row=1, column=0, padx=10, pady=10)
        self.register_username = tk.Entry(self.register_frame, width=30)
        self.register_username.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.register_frame, text="Şifre:").grid(row=2, column=0, padx=10, pady=10)
        self.register_password = tk.Entry(self.register_frame, width=30, show="*")
        self.register_password.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(self.register_frame, text="Kullanıcı Tipi:").grid(row=3, column=0, padx=10, pady=10)
        self.user_type = Combobox(self.register_frame, values=["Bireysel Kullanıcı", "Sistem Yöneticisi"])
        self.user_type.grid(row=3, column=1, padx=10, pady=10)

        tk.Button(self.register_frame, text="Kayıt Ol", command=self.kayıtOl).grid(row=4, column=1, pady=10)
        tk.Button(self.register_frame, text="Giriş sayfasına dön", command=self.show_login_frame).grid(row=5, column=1, pady=10)

    def kayıtOl(self):
        username = self.register_username.get()
        password = self.register_password.get()
        userType=self.user_type.get()

        if not username or not password:
            messagebox.showwarning("Uyarı", "Kullanıcı adı ve şifre boş bırakılamaz.")
            return

        try:
            with open("kayıt.txt", "r", encoding="utf-8") as file:
                for line in file:
                    if f"Kullanıcı  Adı:{username}" in line:
                        messagebox.showwarning("Uyarı", "Bu kullanıcı adı kullanılıyor. Başka bir kullanıcı adı seçiniz.")
                        self.register_username.delete(0, tk.END)
                        return
        except FileNotFoundError:
            pass

        hashed_password = self.hash_password(password)
        with open("kayıt.txt", "a", encoding="utf-8") as file:
            file.write(f"Kullanıcı  Adı:{username}      Şifre:{hashed_password.decode('utf-8')}     Kullanıcı Tipi:{userType}\n")

        messagebox.showinfo("Başarılı", "Kayıt başarıyla tamamlandı.")
        self.show_login_frame()

    def girisYap(self):
        username = self.login_username.get()
        password = self.login_password.get()

        start_time=datetime.now()

        if not username or not password:

            self.logger.log_profile_access(
                username=username if username else "Bilinmeyen",
                status=StatusCode.FAILED,
                details={
                    'start_time':start_time,
                    'end_time':datetime.now(),
                    'access_type':'login',
                    'operation_details':'Kullanıcı adı veya şifre boş bırakıldı.',
                    'error_message':'N/A'
                }
            )
            messagebox.showwarning("Uyarı", "Kullanıcı adı ve şifre boş bırakılamaz.")
            return

        try:
            with open("kayıt.txt", "r", encoding="utf-8") as file:
                for line in file:
                    if f"Kullanıcı  Adı:{username}" in line:
                        stored_hash = line.split('Şifre:')[1].split('Kullanıcı Tipi:')[0].strip()
                        user_type = line.split('Kullanıcı Tipi:')[1].strip()

                        if self.check_password(stored_hash.encode('utf-8'), password):
                            self.logger.log_profile_access(
                                username=username,
                                status=StatusCode.SUCCESS,
                                details={
                                    'start_time':start_time,
                                    'end_time':datetime.now(),
                                    'access_type':'login',
                                    'operation_detais':f'Başarılı giriş -{user_type}'
                                }

                            )
                            if user_type == "Bireysel Kullanıcı":
                                messagebox.showinfo("Başarılı", "Bireysel kullanıcı olarak giriş yapıldı.")
                                self.open_user_window(username)  # Bireysel pencereyi aç
                            elif user_type == "Sistem Yöneticisi":
                                messagebox.showinfo("Başarılı", "Yönetici olarak giriş yapıldı.")
                                self.open_manager_window(username)  # Yönetici pencereyi aç
                            else:

                                self.logger.log_profile_access(
                                    username=username,
                                    status=StatusCode.FAILED,
                                    details={
                                        'start_time':start_time,
                                        'end_time':datetime.now(),
                                        'access_type':'login',
                                        'operation_details':f'Geçersiz kullanıcı tipi:{user_type}',
                                        'error_message':str(e)
                                    }
                                )
                                messagebox.showwarning("Hata", "Geçersiz kullanıcı tipi!")
                            return
                        else:
                            self.logger.log_profile_access(
                                username=username,
                                status=StatusCode.FAILED,
                                details={
                                    'start_time':start_time,
                                    'end_time':datetime.now(),
                                    'access_type':'login',
                                    'operation_details':'Yanlış Şifre Girişi',
                                    #'error_message':str(e)
                                }
                            )
                            messagebox.showwarning("Hata", "Yanlış Şifre!")
                            return
        except FileNotFoundError as e:
            self.logger.log_profile_access(
                username=username,
                status=StatusCode.FAILED,
                details={
                    'start_time':start_time,
                    'end_time':datetime.now(),
                    'access_type':'login',
                    'operation_details':'kayıt dosyası bulunamadı',
                    'error_message':str(e)
                

                }
            )

        self.logger.log_profile_access(
        username=username,
        status=StatusCode.FAILED,
        details={
            'start_time': start_time,
            'end_time': datetime.now(),
            'access_type': 'login',
            'ip_address': 'local',
            'operation_details': 'Kullanıcı bulunamadı',

           # 'error_message':str(e)
        }
    )
        messagebox.showwarning("Hata", "Kullanıcı Bulunamadı!")




    def open_user_window(self, username):
        UserWindow(username)

    def open_manager_window(self,username):
        ManagerWindow(username)


    def hash_password(self, password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed

    def check_password(self, stored_hash, password):
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash)


class UserWindow:
    def __init__(self, username):
        self.window = Toplevel()
        self.window.title("Ana Menü")
        self.window.geometry('1000x600')
        self.file_ops = FileOperations()
        self.username=username 
        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.team_manager = TeamManagement(self.root_path)

        self.user_dir = f"users/{username}/files"
        self.backup_dir = f"users/{username}/backup"
        #self.backup_manager = create_backup_instance(self.user_dir, self.backup_dir)
        Label(self.window, text=f"Hoş geldiniz, {username}!", font=('Arial', 14)).pack(pady=20)

        
        def reopen_window(new_username=None):
            self.window.destroy()
            UserWindow(new_username if new_username else self.username)
        # Ana menü butonları
        
        tk.Button(self.window, text="Kullanıcı Adı Değiştir", width=20, command=lambda: self.file_ops.change_username(self.window,self.username,lambda new_username:UserWindow(new_username))).pack(pady=10)
        
        tk.Button(self.window, text="Şifre Değiştirme İsteği Gönder", width=20, command=lambda: self.file_ops.request_password_change(self.window, self.username)).pack(pady=10)
        tk.Button(self.window, text="Dosya Yükle", width=20, command=lambda:self.file_ops.upload_file(self.window,self.username)).pack(pady=10)
        tk.Button(self.window, text="Takım Oluştur", width=20, command=lambda: self.team_manager.create_team_window(self.window, self.username,reopen_window)).pack(pady=10)
        tk.Button(self.window, text="Bildirimler", width=20, command=lambda:self.team_manager.show_notifications_window(self.window,self.username,reopen_window)).pack(pady=10)
        tk.Button(self.window, text="Paylaş", width=20, command=lambda:self.team_manager.show_file_sharing_window(self.window,self.username,reopen_window)).pack(pady=10)
        tk.Button(self.window, text="Paylaşılan Dosyalar", width=20, command=lambda:self.team_manager.show_shared_files_window(self.window,self.username,reopen_window)).pack(pady=10)
        tk.Button(self.window, text="Yedekle", width=20, 
         command=lambda: BackupInterface(self.window, self.username).show_backup_window()).pack(pady=10)
        tk.Button(self.window, text="Dosya Düzenleme", width=20, command=lambda:self.file_ops.edit_file(self.window,self.username)).pack(pady=10)
        tk.Button(self.window, text="Çıkış", width=20, command=self.window.destroy).pack(pady=10)
        def on_closing():
            if messagebox.askokcancel("Çıkış", "Uygulamadan çıkmak istiyor musunuz?"):
                self.window.destroy()

        self.window.protocol("WM_DELETE_WINDOW", on_closing)



class ManagerWindow:
    def __init__(self, username):
        self.window = Toplevel()
        self.window.title("Yönetici Paneli")
        self.window.geometry('800x500')
        self.username = username
        self.admin_ops = AdminOperations()
        
        # Root path ve gerekli sınıf örnekleri
        self.root_path = os.path.dirname(os.path.abspath(__file__))
        
        Label(self.window, text=f"Hoş geldiniz, {username}!", font=('Arial', 14)).pack(pady=20)
        
        def reopen_window(new_username=None):
            self.window.destroy()
            ManagerWindow(new_username if new_username else self.username)
        
        # Ana menü butonları
        tk.Button(self.window, text="Kullanıcıları Listele",  width=20,  command=lambda: self.admin_ops.list_users(self.window, self.username)).pack(pady=10)
        
        tk.Button(self.window, text="Depolama Limiti Ayarla",  width=20,  command=lambda: self.admin_ops.set_storage_limit(self.window, self.username)).pack(pady=10)
        
        tk.Button(self.window, text="Şifre Değiştirme İstekleri",  width=20, command=lambda: self.admin_ops.view_password_requests(self.window, self.username)).pack(pady=10)
        
        tk.Button(self.window, text="Takımları Görüntüle", width=20, command=lambda: self.admin_ops.view_teams(self.window, self.username)).pack(pady=10)
        -----+++++-
        tk.Button(self.window, text="Bildirimleri Görüntüle", width=20, command=lambda: self.admin_ops.view_notifications(self.window, self.username)).pack(pady=10)
        
        tk.Button(self.window, text="Kullanıcı Dosyalarını Görüntüle",  width=20, command=lambda: self.admin_ops.view_user_files(self.window, self.username)).pack(pady=10)
        
        tk.Button(self.window, text="Kullanıcı İşlemlerini Görüntüle",  width=20, command=lambda: self.admin_ops.view_user_actions(self.window, self.username)).pack(pady=10)
        
        tk.Button(self.window, text="Çıkış", width=20, command=self.window.destroy).pack(pady=10)
        
        def on_closing():
            if messagebox.askokcancel("Çıkış", "Uygulamadan çıkmak istiyor musunuz?"):
                self.window.destroy()
        
        self.window.protocol("WM_DELETE_WINDOW", on_closing)
root = tk.Tk()
app = File(root)
root.mainloop()