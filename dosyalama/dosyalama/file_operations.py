import json
import tkinter as tk
from tkinter import Toplevel, Label, Entry, Button, messagebox,Text,filedialog
import os
import shutil
from datetime import datetime
from backup_module import BackupInterface,BackupHandler

from system_logger import LogType,StatusCode,SystemLogger






class FileOperations:
    def __init__(self):
 
        self.logger=SystemLogger(".")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.logger = SystemLogger(current_dir)
        self.upload_path = "uploads/"  # Örnek dosya yolu
        if not os.path.exists(self.upload_path):
            os.makedirs(self.upload_path) 

        self.base_log_dir = "system_logs"
        os.makedirs(self.base_log_dir, exist_ok=True)
        
        # Merkezi log dosyası yolu
        #self.central_log_file = os.path.join(self.base_log_dir, "all_users_backup_log.txt")
        
        # Kullanıcıya özel log dosyaları için klasör
       # self.user_logs_dir = "user_logs"
        #os.makedirs(self.user_logs_dir, exist_ok=True)
         
    
    
    def change_username(self, current_window, current_username, open_user_window_callback):
    # Yeni pencere oluştur
        start_time=datetime.now()
        self.change_window = Toplevel(current_window)
        self.change_window.title("Kullanıcı Adı Değiştir")
        self.change_window.geometry('400x200')
        
        Label(self.change_window, text="Yeni Kullanıcı Adı:", font=('Arial', 12)).pack(pady=10)
        username_entry = Entry(self.change_window, width=30)
        username_entry.pack(pady=10)
        
        def update_files_and_contents(old_username, new_username):
            try:
                # 1. Önce dosya içeriklerini güncelle
                files_to_update = {
                    'txt': [
                        'password_requests.txt',
                        
                        'kayıt.txt'
                    ],
                    'json': [
                        'notifications.json',
                        'teams.json'
                    ]
                }
                
                # TXT dosyalarını güncelle
                for txt_file in files_to_update['txt']:
                    if os.path.exists(txt_file):
                        try:
                            with open(txt_file, 'r', encoding='utf-8') as file:
                                content = file.read()
                            updated_content = content.replace(old_username, new_username)
                            with open(txt_file, 'w', encoding='utf-8') as file:
                                file.write(updated_content)
                        except Exception as e:
                            print(f"{txt_file} içerik güncellemesi hatası: {str(e)}")
                
                # JSON dosyalarını güncelle
                for json_file in files_to_update['json']:
                    if os.path.exists(json_file):
                        try:
                            with open(json_file, 'r', encoding='utf-8') as file:
                                data = json.load(file)
                            json_str = json.dumps(data, ensure_ascii=False)
                            updated_json_str = json_str.replace(old_username, new_username)
                            updated_data = json.loads(updated_json_str)
                            with open(json_file, 'w', encoding='utf-8') as file:
                                json.dump(updated_data, file, ensure_ascii=False, indent=4)
                        except Exception as e:
                            print(f"{json_file} içerik güncellemesi hatası: {str(e)}")
                
                # 2. Klasör ve dosya isimlerini güncelle
                base_folders = [
                    "logs",
                    "uploads",
                    "shared_files",
                    
                ]
                
                # Ana klasörleri tara ve güncelle
                for base_folder in base_folders:
                    if os.path.exists(base_folder):
                        # Alt klasörleri ve dosyaları güncelle
                        for root, dirs, files in os.walk(base_folder, topdown=False):
                            # Önce dosyaları güncelle
                            for file_name in files:
                                if old_username in file_name:
                                    old_file_path = os.path.join(root, file_name)
                                    new_file_path = os.path.join(root, file_name.replace(old_username, new_username))
                                    try:
                                        os.rename(old_file_path, new_file_path)
                                    except Exception as e:
                                        print(f"Dosya yeniden adlandırma hatası ({file_name}): {str(e)}")
                            
                            # Sonra klasörleri güncelle
                            for dir_name in dirs:
                                if old_username in dir_name:
                                    old_dir_path = os.path.join(root, dir_name)
                                    new_dir_path = os.path.join(root, dir_name.replace(old_username, new_username))
                                    try:
                                        os.rename(old_dir_path, new_dir_path)
                                    except Exception as e:
                                        print(f"Klasör yeniden adlandırma hatası ({dir_name}): {str(e)}")
                
                return True
            except Exception as e:
                print(f"Genel güncelleme hatası: {str(e)}")
                return False
        
        def save_new_username():
            end_time=datetime.now()
            new_username = username_entry.get().strip()
            
            if not new_username:
                messagebox.showwarning("Uyarı", "Kullanıcı adı boş olamaz!")
                return

            try:
                with open("kayıt.txt", "r", encoding="utf-8") as file:
                    content = file.read()
                    if f"Kullanıcı  Adı:{new_username}" in content:
                        messagebox.showwarning("Uyarı", "Bu kullanıcı adı kullanılıyor. Başka bir kullanıcı adı seçiniz.")
                        username_entry.delete(0, tk.END)
                        return
                    
                if update_files_and_contents(current_username, new_username):
                    self.logger.log_change_username(
                        username=new_username,
                        status=StatusCode.SUCCESS,
                        details={
                            'start_time':start_time,
                            'end_time':end_time,
                            'new_username':new_username,
                            'old_username':current_username,
                            'new_username':new_username,
                            'operation_details': f"{current_username} adı {new_username} olarak değiştirildi."
                        }
                    )
                    messagebox.showinfo("Başarılı", f"Kullanıcı Adı Başarıyla '{new_username}' olarak değiştirildi.")
                    self.change_window.destroy()
                    current_window.destroy()
                    open_user_window_callback(new_username)
            except Exception as e:
                self.logger.log_change_username(
                    username=current_username,
                    status=StatusCode.FAILED,
                    #details=f"Hata: {str(e)}"
                    details={
                        'start_time':start_time,
                        'end_time':end_time,
                        'old_username':current_username,
                        'new_username':'N/A',
                        'operation_details':'Kullanıcı adı değiştirilemedi.',
                        'error_message':str(e)
                        }
                )
                messagebox.showerror("Hata", f"Kullanıcı adı değiştirilirken bir hata oluştu: {str(e)}")
                                

        Button(self.change_window, text="Kaydet", command=save_new_username).pack(pady=10)

    def hash_password(self, password):
       import bcrypt
       salt = bcrypt.gensalt()
       hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
       return hashed
    




    def request_password_change(self, current_window, username):
        start_time=datetime.now()
        self.request_window = Toplevel(current_window)
        self.request_window.title("Şifre Değiştirme İsteği")
        self.request_window.geometry('400x300')
        
        Label(self.request_window, text="Şifre Değiştirme İsteği", font=('Arial', 14)).pack(pady=10)
        Label(self.request_window, text="Lütfen değiştirme sebebinizi yazın:", font=('Arial', 12)).pack(pady=10)
        
        reason_text = Text(self.request_window, height=5, width=40)
        reason_text.pack(pady=10)
        
        def send_request():
            end_time=datetime.now()
            reason = reason_text.get("1.0", "end-1c").strip()
            if not reason:
                messagebox.showwarning("Uyarı", "Lütfen bir sebep belirtin!")
                return
                
            try:
                start_time = datetime.now()  # Capture the time when the request starts
                # Format the current date and time
                formatted_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

                with open('password_requests.txt', 'a', encoding='utf-8') as file:
                    file.write(f"Kullanıcı:{username}\nSebep:{reason}\nDurum:Beklemede \n Tarih:{formatted_time}\n---\n")


                
                    self.logger.log_password_request(
                        username=username,
                        status=StatusCode.SUCCESS,
                        details={
                            'start_time':start_time,
                            'end_time':end_time,
                            'reason': reason,
                            'operation_details': 'Şifre değişiklik talebi başarıyla oluşturuldu ve yöneticiye iletildi'
                        }
                    )

                    
                messagebox.showinfo("Başarılı", "Şifre değiştirme isteğiniz gönderildi. Yönetici onayı bekleniyor.")
                self.request_window.destroy()
                
            except Exception as e:
                self.logger.log_password_request(
                    username=username,
                    status=StatusCode.FAILED,
                    details={
                        'start_time':start_time,
                        'end_time':end_time,
                        'reason': reason,
                        'operation_details': 'Şifre değişiklik talebi oluşturma işlemi başarısız',
                        'error_message': str(e)

                    }
                )
                messagebox.showerror("Hata", f"İstek gönderilirken bir hata oluştu: {str(e)}")
        
        def check_request_status():
            try:
                with open('password_requests.txt', 'r', encoding='utf-8') as file:
                    content = file.read()
                    requests = content.split('---\n')
                    
                    for request in requests:
                        if f"Kullanıcı:{username}" in request:
                            if "Durum:Onaylandı" in request:
                                self.show_password_change_form(username)
                                return
                            elif "Durum:Reddedildi" in request:
                                messagebox.showwarning("Bilgi", "Şifre değiştirme isteğiniz reddedildi.")
                                return
                            elif "Durum:Beklemede" in request:
                                messagebox.showinfo("Bilgi", "İsteğiniz hala inceleniyor.")
                                return
                                
                messagebox.showinfo("Bilgi", "Aktif bir şifre değiştirme isteğiniz bulunmuyor.")
                
            except FileNotFoundError:
                messagebox.showinfo("Bilgi", "Henüz hiç şifre değiştirme isteği bulunmuyor.")
            except Exception as e:
                messagebox.showerror("Hata", f"İstek durumu kontrol edilirken bir hata oluştu: {str(e)}")
        
        Button(self.request_window, text="İsteği Gönder", command=send_request).pack(pady=10)
        Button(self.request_window, text="İstek Durumunu Kontrol Et", command=check_request_status).pack(pady=10)
        Button(self.request_window, text="Kapat", command=self.request_window.destroy).pack(pady=10)
    
    def show_password_change_form(self, username):
        change_window = Toplevel()
        change_window.title("Şifre Değiştir")
        change_window.geometry('400x300')
        
        Label(change_window, text="Yeni Şifre:", font=('Arial', 12)).pack(pady=10)
        new_password = Entry(change_window, show="*", width=30)
        new_password.pack(pady=10)
        
        Label(change_window, text="Şifreyi Tekrar Girin:", font=('Arial', 12)).pack(pady=10)
        confirm_password = Entry(change_window, show="*", width=30)
        confirm_password.pack(pady=10)
        
        def save_new_password():
            if new_password.get() != confirm_password.get():
                messagebox.showwarning("Uyarı", "Şifreler eşleşmiyor!")
                return
                
            if len(new_password.get()) < 6:
                messagebox.showwarning("Uyarı", "Şifre en az 6 karakter olmalıdır!")
                return
                
            try:
                with open('kayıt.txt', 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    
                for i, line in enumerate(lines):
                    if f"Kullanıcı  Adı:{username}" in line:
                        parts = line.split('      ')
                        new_hash = self.hash_password(new_password.get()).decode('utf-8')
                        lines[i] = f"{parts[0]}      Şifre:{new_hash}      {parts[2]}"
                        break
                
                with open('kayıt.txt', 'w', encoding='utf-8') as file:
                    file.writelines(lines)
                    
                self.archive_password_request(username)
                    
                messagebox.showinfo("Başarılı", "Şifreniz başarıyla değiştirildi!")
                change_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Hata", f"Şifre değiştirilirken bir hata oluştu: {str(e)}")
        
        Button(change_window, text="Şifreyi Değiştir", command=save_new_password).pack(pady=10)
        Button(change_window, text="İptal", command=change_window.destroy).pack(pady=10)
    
    def archive_password_request(self, username):
        try:
            with open('password_requests.txt', 'r', encoding='utf-8') as file:
                requests = file.read().split('---\n')
            
            with open('password_requests.txt', 'w', encoding='utf-8') as file:
                for request in requests:
                    if f"Kullanıcı:{username}" not in request:
                        file.write(request + '---\n')
        except Exception as e:
            print(f"İstek arşivlenirken hata oluştu: {str(e)}")
            
   
    def upload_file(self, current_window, username):
        self.upload_window = Toplevel(current_window)
        self.upload_window.title("Dosya Yükleme")
        self.upload_window.geometry('400x300')
        
        Label(self.upload_window, text="Dosya Yükleme", font=('Arial', 14)).pack(pady=10)
        
        def select_file():
            try:
                file_path = filedialog.askopenfilename(
                    title="Dosya Seç",
                    filetypes=[
                        ("Tüm Dosyalar", "*.*"),
                        ("Text Dosyaları", "*.txt"),
                        ("PDF Dosyaları", "*.pdf"),
                        ("Word Dosyaları", "*.docx")
                    ]
                )
                
                if not file_path:
                    return

                # Kullanıcıya özel klasör oluştur
                user_folder = os.path.join(self.upload_path, username)
                if not os.path.exists(user_folder):
                    os.makedirs(user_folder)

                # Dosya adını zaman damgası ile birlikte oluştur
                original_filename = os.path.basename(file_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_filename = f"{timestamp}_{original_filename}"
                destination_path = os.path.join(user_folder, new_filename)

                # Dosyayı kopyala
                shutil.copy2(file_path, destination_path)

                # Dosya bilgilerini kaydet
                #with open(os.path.join(user_folder, "file_log.txt"), "a", encoding="utf-8") as log:
                 #   log.write(f"Dosya: {original_filename}\n")
                   # log.write(f"Yükleme Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                  #  log.write(f"Boyut: {os.path.getsize(destination_path)} bytes\n")
                    #log.write("-" * 50 + "\n")

                messagebox.showinfo("Başarılı", f"Dosya başarıyla yüklendi:\n{original_filename}")
                self.upload_window.destroy()

            except Exception as e:
                messagebox.showerror("Hata", f"Dosya yüklenirken bir hata oluştu:\n{str(e)}")

        Button(self.upload_window, text="Dosya Seç", command=select_file).pack(pady=20)
        Button(self.upload_window, text="Kapat", command=self.upload_window.destroy).pack(pady=20)            


    
    

    # file_operations.py


    def edit_file(self, current_window, username):
        self.edit_window = Toplevel()
        self.edit_window.title("Dosya Seç ve Düzenle")
        self.edit_window.geometry('600x600')  # Yeni butonlar için biraz daha yükseklik
        self.edit_window.transient(current_window)
        self.edit_window.grab_set()

        # Başlık etiketi
        Label(self.edit_window, text="Dosya Seç ve Düzenle", font=('Arial', 14, 'bold')).pack(pady=10)
        Label(self.edit_window, text="Lütfen düzenlemek istediğiniz dosyayı seçin:", font=('Arial', 12)).pack(pady=5)

        # Seçilen dosya yolunu tutmak için
        self.selected_file_path = None
        self.text_editor = None

        def select_file_to_edit():
            try:
                user_folder = os.path.join(self.upload_path, username)
                if not os.path.exists(user_folder):
                    messagebox.showwarning("Uyarı", "Henüz yüklenmiş dosyanız bulunmuyor!")
                    return

                file_path = filedialog.askopenfilename(
                    initialdir=user_folder,
                    title="Düzenlenecek Dosyayı Seç",
                    filetypes=[("Tüm Dosyalar", "*.*"), ("Text Dosyaları", "*.txt")]
                )

                if not file_path:
                    return

                self.selected_file_path = file_path  # Dosya yolunu kaydet

                with open(file_path, 'r', encoding='utf-8') as file:
                    file_content = file.read()

                if self.text_editor:
                    self.text_editor.destroy()

                self.text_editor = Text(self.edit_window, wrap='word', height=15, width=60, font=('Arial', 10))
                self.text_editor.pack(pady=10)
                self.text_editor.insert("1.0", file_content)

                # Yedekleme butonlarını aktifleştir
                backup_frame.pack(pady=10)

            except Exception as e:
                messagebox.showerror("Hata", f"Dosya seçme/düzenleme işleminde bir hata oluştu: {str(e)}")

        def save_edits():
            if not self.selected_file_path or not self.text_editor:
                messagebox.showwarning("Uyarı", "Lütfen önce bir dosya seçin!")
                return

            try:
                updated_content = self.text_editor.get("1.0", "end-1c")
                with open(self.selected_file_path, 'w', encoding='utf-8') as file:
                    file.write(updated_content)
                messagebox.showinfo("Başarılı", "Değişiklikler kaydedildi!")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya kaydedilirken bir hata oluştu: {str(e)}")

        def create_backup(username ):
            if not self.selected_file_path:
                messagebox.showwarning("Uyarı", "Lütfen önce bir dosya seçin!")
                return

            try:
                # Orijinal dosyanın dizin ve dosya adı bilgilerini al
                original_dir = os.path.dirname(self.selected_file_path)
                file_name, file_ext = os.path.splitext(os.path.basename(self.selected_file_path))
                
                # Tarih-saat eklenmiş yeni dosya adı oluştur
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"{file_name}_yedek_{timestamp}{file_ext}"
                
                # Yedek dosyayı orijinal dosyanın bulunduğu dizine kaydet
                backup_path = os.path.join(original_dir, backup_filename)
                
                # Dosyayı kopyala
                shutil.copy2(self.selected_file_path, backup_path)
                
                messagebox.showinfo("Başarılı", f"Dosya başarıyla yedeklendi!\nYedek dosya: {backup_filename}")
                
                # İsterseniz log kaydı da tutabilirsiniz
                #log_dir = os.path.join("logs", username)
                #os.makedirs(log_dir, exist_ok=True)
                #log_file = os.path.join(log_dir, "yedekleme_log.txt")
                
                log_entry = (
                    f"Tarih: {datetime.datetime.now()}\n"
                    f"İşlem: Dosya Yedekleme\n"
                    f"Orijinal Dosya: {self.selected_file_path}\n"
                    f"Yedek Dosya: {backup_path}\n"
                    f"------------------------\n"
                )
                
                #with open(log_file, "a", encoding="utf-8") as f:
                    #f.write(log_entry)
                
              #  with open(self.central_log_file, "a", encoding="utf-8") as central_log:
                  #  central_log.write(log_entry)
        
                    # Kullanıcıya özel log dosyasına da yaz
                    #user_log_dir = os.path.join(self.user_logs_dir, username)
                    #os.makedirs(user_log_dir, exist_ok=True)
                    #user_log_file = os.path.join(user_log_dir, "yedekleme_log.txt")
                   # with open(user_log_file, "a", encoding="utf-8") as user_log:
                       #user_log.write(log_entry)  
        

            except Exception as e:
                messagebox.showerror("Hata", f"Yedekleme sırasında hata oluştu: {str(e)}")

        def show_backup_interface():
            try:
                backup_interface = BackupInterface(self.edit_window, username)
                backup_interface.show_backup_window()
            except Exception as e:
                messagebox.showerror("Hata", f"Yedekleme arayüzü açılırken hata oluştu: {str(e)}")

        # Ana butonlar
        Button(self.edit_window, text="Dosya Seç ve Düzenle", 
               command=select_file_to_edit, 
               font=('Arial', 11)).pack(pady=10)

        # Yedekleme işlemleri için frame
        backup_frame = tk.Frame(self.edit_window)
        
        # Yedekleme butonları
        Button(backup_frame, text="Dosyayı Yedekle", 
       command=lambda: create_backup(username),  # username'i geçir
       font=('Arial', 11)).pack(side=tk.LEFT, padx=5)
        
        Button(backup_frame, text="Yedekleme Ayarları", 
               command=show_backup_interface, 
               font=('Arial', 11)).pack(side=tk.LEFT, padx=5)

        # Başlangıçta yedekleme frame'ini gizle
        # backup_frame.pack(pady=10)  # Dosya seçilince gösterilecek

        # Kaydet ve Kapat butonları
        Button(self.edit_window, text="Değişiklikleri Kaydet", 
               command=save_edits, 
               font=('Arial', 11)).pack(pady=10)

        Button(self.edit_window, text="Kapat", 
               command=lambda: self.edit_window.destroy(), 
               font=('Arial', 11)).pack(pady=10)

        def on_edit_window_close():
            self.edit_window.destroy()
            current_window.deiconify()

        self.edit_window.protocol("WM_DELETE_WINDOW", on_edit_window_close)