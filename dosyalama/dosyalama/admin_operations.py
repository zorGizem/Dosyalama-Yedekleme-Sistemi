import json
import os
from tkinter import ttk, messagebox
import tkinter as tk
from datetime import datetime
from system_logger import LogType,StatusCode,SystemLogger


class AdminOperations:
    def __init__(self):
        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.users_file = os.path.join(self.root_path, "kayıt.txt")
        self.password_requests_file = os.path.join(self.root_path, "password_requests.txt")
        self.teams_file = os.path.join(self.root_path, "teams.json")
        self.notifications_file = os.path.join(self.root_path, "notifications.json")
        self.logger=SystemLogger(".")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.logger = SystemLogger(current_dir)

    def read_users(self):
        users = []
        try:
            with open(self.users_file, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    # "Kullanıcı Adı:", "Şifre:" ve "Kullanıcı Tipi:" etiketlerini temizle
                    if line.startswith("Kullanıcı  Adı:"):
                        username = line.split("Kullanıcı  Adı:")[1].split()[0]
                    if "Şifre:" in line:
                        password = line.split("Şifre:")[1].split()[0]
                    if "Kullanıcı Tipi:" in line:
                        role = line.split("Kullanıcı Tipi:")[1].strip()
                        users.append({
                            'username': username,
                            'password': password,
                            'role': role
                        })
        except FileNotFoundError:
            messagebox.showerror("Hata", "Kullanıcı dosyası bulunamadı!")
        return users


    def list_users(self, parent_window, admin_username):
        user_window = tk.Toplevel(parent_window)
        user_window.title("Kullanıcı Listesi")
        user_window.geometry('600x400')

        # Treeview oluştur
        tree = ttk.Treeview(user_window, columns=('Username','Password','Role'), show='headings')
        tree.heading('Username', text='Kullanıcı Adı')
        tree.heading('Password',text="Şifre")
        tree.heading('Role', text='Rol')
        tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        users = self.read_users()
        for user in users:
            tree.insert('', 'end', values=(user['username'], user['password'],user['role']))

    def set_storage_limit(self, parent_window, admin_username):
        def update_limit():
            username = username_var.get()
            limit = limit_var.get()
            
            # Kullanıcı limitleri için JSON dosyası oluştur/güncelle
            limits_file = os.path.join(self.root_path, "storage_limits.json")
            try:
                with open(limits_file, 'r') as f:
                    limits = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                limits = {}
            
            limits[username] = limit
            
            with open(limits_file, 'w') as f:
                json.dump(limits, f, indent=4)
            
            messagebox.showinfo("Başarılı", f"{username} için depolama limiti {limit}MB olarak güncellendi.")

        limit_window = tk.Toplevel(parent_window)
        limit_window.title("Depolama Limiti Ayarla")
        limit_window.geometry('400x200')

        username_var = tk.StringVar()
        limit_var = tk.IntVar()

        tk.Label(limit_window, text="Kullanıcı Adı:").pack(pady=5)
        tk.Entry(limit_window, textvariable=username_var).pack(pady=5)
        
        tk.Label(limit_window, text="Limit (MB):").pack(pady=5)
        tk.Entry(limit_window, textvariable=limit_var).pack(pady=5)
        
        tk.Button(limit_window, text="Limiti Güncelle", command=update_limit).pack(pady=10)

    

    def view_password_requests(self, parent_window, admin_username):
        """Parola değiştirme isteklerini görüntüler"""
        try:
            with open(self.password_requests_file, 'r', encoding='utf-8') as file:
                lines = file.readlines()  # Dosyadaki tüm satırları oku

            requests = []  # İstekleri saklamak için bir liste
            current_request = {}  # Her bir isteği geçici olarak saklayacağımız sözlük

            for line in lines:
                line = line.strip()  # Satırdaki boşlukları temizle
                if line == "---":  # Bu, isteklerin arasındaki ayırıcı
                    if current_request:
                        requests.append(current_request)  # İstek bitince listeye ekle
                    current_request = {}  # Yeni istek için boş bir sözlük oluştur
                elif line.startswith("Kullanıcı:"):
                    current_request['username'] = line.replace("Kullanıcı:", "").strip()  # Kullanıcı adı
                elif line.startswith("Sebep:"):
                    current_request['reason'] = line.replace("Sebep:", "").strip()  # Sebep
                elif line.startswith("Tarih:"):
                    current_request['date'] = line.replace("Tarih:", "").strip()  # Tarih
                elif line.startswith("Durum:"):
                    current_request['status'] = line.replace("Durum:", "").strip()  # Durum

            if not requests:
                messagebox.showinfo("Bilgi", "Bekleyen şifre değiştirme isteği bulunmamaktadır.")
                return

            # Yeni pencere oluştur
            req_window = tk.Toplevel(parent_window)
            req_window.title("Şifre Değiştirme İstekleri")
            req_window.geometry('700x500')

            tk.Label(req_window, text="Şifre Değiştirme İstekleri", font=('Arial', 12, 'bold')).pack(pady=10)

            # Her bir istek için yeni bir frame oluştur
            for req in requests:
                frame = tk.Frame(req_window, relief='solid', borderwidth=1)
                frame.pack(fill='x', padx=5, pady=2)

                username = req.get('username', 'Bilinmiyor')
                request_date = req.get('date', 'Tarih bilgisi yok')
                reason = req.get('reason', 'Sebep belirtilmemiş')
                status = req.get('status', 'Durum belirtilmemiş')

                # İstek bilgilerini gösteren etiketler
                tk.Label(frame, text=f"Kullanıcı: {username}").pack(side='left', padx=5)
                tk.Label(frame, text=f"Tarih: {request_date}").pack(side='left', padx=5)
                tk.Label(frame, text=f"Sebep: {reason}").pack(side='left', padx=5)
                tk.Label(frame, text=f"Durum: {status}").pack(side='left', padx=5)

                # Onayla ve Reddet butonları
                tk.Button(frame, text="Onayla", command=lambda u=username: self.approve_password_request(u, admin_username)).pack(side='right', padx=5)
                tk.Button(frame, text="Reddet", command=lambda u=username: self.reject_password_request(u, admin_username)).pack(side='right', padx=5)

        except Exception as e:
            messagebox.showerror("Hata", f"İstekler alınırken bir hata oluştu: {str(e)}")


    def approve_password_request(self, username, admin_username):
        try:
            start_time = datetime.now()
            with open(self.password_requests_file, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            updated_lines = []
            for i, line in enumerate(lines):
                if line.strip().startswith(f"Kullanıcı:{username}"):
                    # Kullanıcının isteğini bul ve satırları güncelle
                    updated_lines.extend(lines[i:i+3])  # Kullanıcı, Sebep ve Tarih satırlarını kopyala
                    updated_lines.append(f"Durum: Onaylandı\n")  # Durum satırını ekle
                    updated_lines.append("---\n")  # Ayırıcı
                    i += 4  # Sonraki isteğe geç
                else:
                    updated_lines.append(line)

            with open(self.password_requests_file, 'w', encoding='utf-8') as file:
                file.writelines(updated_lines)

            self.logger.log_password_accept(
                username=username,
                admin_username=admin_username,
                status=StatusCode.APPROVED,
                details={
                    'start_time': start_time,
                    'end_time': datetime.now(),
                    'operation_details': f'Şifre değiştirme isteği onaylandı. Onaylayan: {admin_username}'
                }
            )
        
            self.add_notification(f"{username} kullanıcısının şifre değiştirme isteği onaylandı", username)
            messagebox.showinfo("Başarılı", f"{username} kullanıcısının şifre değiştirme isteği onaylandı!")

        except Exception as e:
            self.logger.log_password_accept(
                username=username,
                admin_username=admin_username,
                status=StatusCode.FAILED,
                details={
                    'start_time': start_time,
                    'end_time': datetime.now(),
                    'operation_details': f"Şifre değiştirme isteği onaylama hatası - Onaylayan: {username}",
                    'error_message': str(e)
                }
            )
            messagebox.showerror("Hata", f"Dosya işlemleri sırasında hata oluştu!{str(e)}")

    def reject_password_request(self, username, admin_username):
        try:
            start_time = datetime.now()
            with open(self.password_requests_file, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            updated_lines = []
            for i, line in enumerate(lines):
                if line.strip().startswith(f"Kullanıcı:{username}"):
                    updated_lines.extend(lines[i:i+3])  # Kullanıcı, Sebep ve Tarih satırlarını kopyala
                    updated_lines.append(f"Durum: Reddedildi\n")  # Durum satırını ekle
                    updated_lines.append("---\n")  # Ayırıcı
                    i += 4
                else:
                    updated_lines.append(line)

            with open(self.password_requests_file, 'w', encoding='utf-8') as file:
                file.writelines(updated_lines)

            self.logger.log_password_accept(
                username=username,
                admin_username=admin_username,
                status=StatusCode.REJECTED,
                details={
                    'start_time': start_time,
                    'end_time': datetime.now(),
                    'operation_details': f'Şifre değiştirme isteği reddedildi. Reddeden: {admin_username}'
                }
            )
            
            self.add_notification(f"{username} kullanıcısının şifre değiştirme isteği reddedildi")
            messagebox.showinfo("Bilgi", f"{username} kullanıcısının şifre değiştirme isteği reddedildi!")
        
        except Exception as e:
            self.logger.log_password_accept(
                username=username,
                admin_username=admin_username,
                status=StatusCode.FAILED,
                details={
                    'start_time': start_time,
                    'end_time': datetime.now(),
                    'operation_details': f'Şifre değiştirme isteği reddedildi. Reddeden: {username}',
                    'error_message': str(e)
                }
            )
            messagebox.showerror("Hata", "Dosya işlemleri sırasında hata oluştu!")
    
    def view_teams(self,parent_window,admin_username):
        """Takımları görüntüler"""
        try:
            with open(self.teams_file, 'r', encoding='utf-8') as file:
                teams = json.load(file)
            
            if not teams:
                messagebox.showinfo("Bilgi", "Kayıtlı takım bulunmamaktadır.")
                return
            
            # Yeni pencere oluştur
            teams_window = tk.Toplevel()
            teams_window.title("Takımlar")
            teams_window.geometry('500x400')
            
            tk.Label(teams_window, text="Takımlar", 
                  font=('Arial', 12, 'bold')).pack(pady=10)
            
            for team_name, members in teams.items():
                frame = tk.Frame(teams_window, relief='solid', borderwidth=1)
                frame.pack(fill='x', padx=5, pady=5)
                
                tk.Label(frame, text=f"Takım: {team_name}", 
                      font=('Arial', 10, 'bold')).pack(pady=2)
                tk.Label(frame, text=f"Üyeler: {', '.join(members)}").pack(pady=2)
                
        except FileNotFoundError:
            messagebox.showerror("Hata", "Takımlar dosyası bulunamadı!")
        except json.JSONDecodeError:
            messagebox.showerror("Hata", "Takımlar dosyası okunamadı!")

    def view_notifications(self,parent_window,admin_username):
        """Bildirimleri görüntüler"""
        try:
            with open(self.notifications_file, 'r', encoding='utf-8') as file:
                notifications = json.load(file)
            
            if not notifications:
                messagebox.showinfo("Bilgi", "Bildirim bulunmamaktadır.")
                return
            
            # Yeni pencere oluştur
            notif_window = tk.Toplevel()
            notif_window.title("Bildirimler")
            notif_window.geometry('500x400')
            
            tk. Label(notif_window, text="Bildirimler", 
                  font=('Arial', 12, 'bold')).pack(pady=10)
            
            for notif in notifications:
                frame = tk.Frame(notif_window, relief='solid', borderwidth=1)
                frame.pack(fill='x', padx=5, pady=2)
                tk.Label(frame, text=notif).pack(pady=5)
                
        except FileNotFoundError:
            messagebox.showerror("Hata", "Bildirimler dosyası bulunamadı!")
        except json.JSONDecodeError:
            messagebox.showerror("Hata", "Bildirimler dosyası okunamadı!")

    def add_notification(self, message, username):
        """Yeni bildirim ekler"""
        try:
            current_data = {}
            # Mevcut dosyayı oku
            if os.path.exists(self.notifications_file):
                with open(self.notifications_file, 'r', encoding='utf-8') as file:
                    current_data = json.load(file)
            
            # Yeni bildirimin detaylarını hazırla
            new_notification = {
                "message": message,
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "read": False
            }
            
            # Kullanıcı için bildirim ekle
            if username not in current_data:
                current_data[username] = []  # Eğer kullanıcı yoksa, yeni bir liste başlat
            current_data[username].append(new_notification)
            
            # Güncellenmiş veriyi kaydet
            with open(self.notifications_file, 'w', encoding='utf-8') as file:
                json.dump(current_data, file, indent=4, ensure_ascii=False)
                
        except Exception as e:
            print(f"Bildirim eklenirken hata oluştu: {str(e)}")


    
    
    def view_user_files(self, parent_window, admin_username):
        files_window = tk.Toplevel(parent_window)
        files_window.title("Kullanıcı Dosyaları")
        files_window.geometry('800x600')
        
        frame = tk.Frame(files_window)
        frame.pack(pady=10)
        
        tk.Label(frame, text="Kullanıcı Seçin:").pack(side=tk.LEFT, padx=5)
        user_var = tk.StringVar()
        user_combo = ttk.Combobox(frame, textvariable=user_var)
        user_combo.pack(side=tk.LEFT, padx=5)
        
        show_button = tk.Button(frame, text="Dosyaları Göster", 
                            command=lambda: load_user_files())
        show_button.pack(side=tk.LEFT, padx=5)
        
        close_button = tk.Button(frame, text="Ana Menüye Dön",
                                command=lambda: return_to_main())
        close_button.pack(side=tk.LEFT, padx=5)
        
        tree = ttk.Treeview(files_window, columns=('Filename', 'Size', 'Modified'), show='headings')
        tree.heading('Filename', text='Dosya Adı')
        tree.heading('Size', text='Boyut')
        tree.heading('Modified', text='Son Değişiklik')
        tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        def return_to_main():
            files_window.destroy()
            parent_window.deiconify()
        
        def load_user_files():
            selected_user = user_var.get()
            if not selected_user:
                messagebox.showwarning("Uyarı", "Lütfen bir kullanıcı seçin!")
                return
            
            user_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads", selected_user)

            
            for item in tree.get_children():
                tree.delete(item)
                
            if os.path.exists(user_dir):
                found_files = False
                for file in os.listdir(user_dir):
                    file_path = os.path.join(user_dir, file)
                    if os.path.isfile(file_path):
                        stats = os.stat(file_path)
                        tree.insert('', 'end', values=(
                            file,
                            f"{stats.st_size / 1024:.1f} KB",
                            datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                        ))
                        found_files = True
                
                if not found_files:
                    messagebox.showinfo("Bilgi", f"{selected_user} kullanıcısına ait dosya bulunamadı!")
            else:
                messagebox.showinfo("Bilgi", f"{selected_user} kullanıcısına ait klasör bulunamadı!")
        
        files_window.protocol("WM_DELETE_WINDOW", return_to_main)
        
        users = [user['username'] for user in self.read_users()]
        user_combo['values'] = users

    def view_user_actions(self, parent_window, admin_username):
        def get_users_from_file(self):
            users = []
            try:
                users_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kayıt.txt")
                print(f"Kullanıcı dosyası yolu: {users_file}")
                
                with open(users_file, 'r', encoding='utf-8') as file:
                    content = file.read()
                    user_blocks = content.split('Kullanıcı  Adı:')
                    for block in user_blocks[1:]:  # İlk boş bloğu atla
                        if block.strip():
                            username = block.split('Şifre:')[0].strip()
                            if username:
                                users.append(username)
                                print(f"Bulunan kullanıcı: '{username}'")
                                
            except FileNotFoundError:
                print("Kullanıcı dosyası bulunamadı!")
                messagebox.showerror("Hata", f"Kullanıcı dosyası bulunamadı: {users_file}")
            except Exception as e:
                print(f"Hata: {str(e)}")
                messagebox.showerror("Hata", f"Kullanıcı listesi alınırken hata oluştu: {str(e)}")
                
            print(f"Toplam bulunan kullanıcı sayısı: {len(users)}")
            return sorted(users)  # Kullanıcıları alfabetik sırala

        def load_user_actions(selected_user=None):
            if not selected_user:
                print("Kullanıcı seçilmedi!")
                return
                
            print(f"\nSeçilen kullanıcı: '{selected_user}'")
            
            # Treeview'i temizle
            for item in tree.get_children():
                tree.delete(item)
                
            logs_base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
            print(f"Log klasörü yolu: {logs_base_dir}")
            
            log_folders = {
                'password_request': 'Şifre Talebi',
                'password_accept': 'Şifre Onayı',
                'profile_access': 'Profil Erişimi',
                'doc_sharing': 'Döküman Paylaşımı',
                'team_management': 'Takım Yönetimi',
                'system_logs': 'Sistem Logları',
                'anomalies': 'Anomali',
                'backup': 'Yedekleme',
                'change_username': 'Kullanıcı Adı Değişikliği',
                'shared_files': 'Paylaşılan Dosyalar'
            }
            
            found_entries = 0
            all_entries = []
            
            try:
                for folder, folder_display in log_folders.items():
                    folder_path = os.path.join(logs_base_dir, folder)
                    if os.path.exists(folder_path):
                        for filename in os.listdir(folder_path):
                            if filename.endswith('.txt'):
                                log_path = os.path.join(folder_path, filename)
                                try:
                                    with open(log_path, 'r', encoding='utf-8') as file:
                                        current_entry = {}
                                        for line in file:
                                            line = line.strip()
                                            if line.startswith('Kullanıcı:'):
                                                if current_entry and current_entry.get('username') == selected_user:
                                                    # Önceki kaydı ekle
                                                    date = current_entry.get('start_time', '')
                                                    action = f"{current_entry.get('operation_type', '')}: {current_entry.get('operation_detail', '')}"
                                                    all_entries.append((date, selected_user, action))
                                                    found_entries += 1
                                                
                                                # Yeni kayıt başlat
                                                current_entry = {}
                                                current_entry['username'] = line.split(':', 1)[1].strip()
                                            elif line.startswith('İşlem Başlangıç:'):
                                                current_entry['start_time'] = line.split(':', 1)[1].strip()
                                            elif line.startswith('İşlem Türü:'):
                                                current_entry['operation_type'] = line.split(':', 1)[1].strip()
                                            elif line.startswith('İşlem Detayı:'):
                                                current_entry['operation_detail'] = line.split(':', 1)[1].strip()
                                            elif line.startswith('------------------------'):
                                                # Son kaydı kontrol et
                                                if current_entry and current_entry.get('username') == selected_user:
                                                    date = current_entry.get('start_time', '')
                                                    action = f"{current_entry.get('operation_type', '')}: {current_entry.get('operation_detail', '')}"
                                                    all_entries.append((date, selected_user, action))
                                                    found_entries += 1
                                                current_entry = {}
                                        
                                        # Dosya sonundaki son kaydı kontrol et
                                        if current_entry and current_entry.get('username') == selected_user:
                                            date = current_entry.get('start_time', '')
                                            action = f"{current_entry.get('operation_type', '')}: {current_entry.get('operation_detail', '')}"
                                            all_entries.append((date, selected_user, action))
                                            found_entries += 1
                                            
                                except Exception as e:
                                    print(f"Dosya okuma hatası ({filename}): {str(e)}")
                                    continue

                # Tarihe göre sırala (en yeni en üstte)
                all_entries.sort(reverse=True)
                
                # Sıralanmış kayıtları Treeview'e ekle
                for date, user, action in all_entries:
                    tree.insert('', 'end', values=(user, action, date))

            except Exception as e:
                print(f"Genel hata: {str(e)}")
                messagebox.showerror("Hata", f"Log dosyaları okunurken bir hata oluştu: {str(e)}")
            
            if found_entries == 0:
                messagebox.showinfo("Bilgi", f"{selected_user} kullanıcısı için kayıt bulunamadı.")

        def on_user_select(event):
            selected_user = user_combobox.get()
            if selected_user:
                print(f"\nKullanıcı seçildi: '{selected_user}'")
                load_user_actions(selected_user)

        # Ana pencereyi oluştur
        actions_window = tk.Toplevel(parent_window)
        actions_window.title("Kullanıcı İşlemleri Görüntüleyici")
        actions_window.geometry('900x500')

        # Kullanıcı seçme alanı
        users = get_users_from_file(self)
        frame = ttk.Frame(actions_window)
        frame.pack(pady=5, padx=10, fill=tk.X)
        
        ttk.Label(frame, text="Kullanıcı Seç:").pack(side=tk.LEFT, padx=5)
        user_combobox = ttk.Combobox(frame, values=users, width=30, state="readonly")
        user_combobox.pack(side=tk.LEFT, padx=5)
        user_combobox.bind('<<ComboboxSelected>>', on_user_select)

        # Treeview oluştur
        tree = ttk.Treeview(actions_window, columns=('User', 'Action', 'Date'), show='headings')
        tree.heading('User', text='Kullanıcı')
        tree.heading('Action', text='İşlem')
        tree.heading('Date', text='Tarih')
        
        tree.column('User', width=150)
        tree.column('Action', width=450)
        tree.column('Date', width=200)
        
        # Scrollbar ekle
        scrollbar = ttk.Scrollbar(actions_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar.pack(pady=10, fill=tk.Y, side=tk.RIGHT)