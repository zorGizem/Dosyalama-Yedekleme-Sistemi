import tkinter as tk
from tkinter import messagebox
from tkinter import messagebox, ttk
from system_logger import LogType,StatusCode,SystemLogger


import json
import os
from datetime import datetime
from tkinter import filedialog
import shutil

class TeamManagement:
    def __init__(self, root_path):
        self.root_path = root_path
        self.teams_file = os.path.join(root_path, "teams.json")
        self.notifications_file = os.path.join(root_path, "notifications.json")
        self.shared_files_dir = os.path.join(root_path, "shared_files")
        self.logger=SystemLogger(".")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.logger = SystemLogger(current_dir)
        
        # Teams ve notifications dosyalarını oluştur
        if not os.path.exists(self.teams_file):
            self.save_teams({})
        if not os.path.exists(self.notifications_file):
            self.save_notifications({})
        if not os.path.exists(self.shared_files_dir):
            os.makedirs(self.shared_files_dir)

    def create_team_window(self, current_window, username,open_main_callback):
        start_time=datetime.now()
        team_window = tk.Toplevel(current_window)
        team_window.title("Takım Oluştur")
        team_window.geometry('500x400')

        # Mevcut kullanıcıları yükle
        users = self.load_users()
        team_members = []

        # Kullanıcı listesi
        tk.Label(team_window, text="Kullanıcılar").pack(pady=10)
        listbox = tk.Listbox(team_window, selectmode=tk.MULTIPLE, width=40)
        for user in users:
            if user != username:  # Kendisi hariç
                listbox.insert(tk.END, user)
        listbox.pack(pady=10)

        def add_team():
            end_time=datetime.now()
            selections = listbox.curselection()
            if not selections:
                messagebox.showwarning("Uyarı", "Lütfen en az bir üye seçin")
                return

            team_members = [listbox.get(i) for i in selections]
            try:
                teams = self.load_teams()
                
                # Takımı oluştur
                if username not in teams:
                    teams[username] = []
                teams[username].extend(team_members)
                
                # Bildirimleri oluştur
                for member in team_members:
                    self.create_notification(member, f"{username} sizi takımına ekledi")
                    
                    # Karşılıklı dosya paylaşım izinlerini ayarla
                    if member not in teams:
                        teams[member] = []
                    teams[member].append(username)

                self.save_teams(teams)

                self.logger.log_team_management(
                    username=username,
                    status=StatusCode.SUCCESS,
                    details={
                        'start_time':start_time,
                        'end_time':end_time,
                        'operation_details':'Takımlar Başarıyla oluşturuldu.'
                    }
                )
                messagebox.showinfo("Başarılı", "Takım oluşturuldu")
                team_window.destroy()
            except Exception as e:
                self.logger.log_team_management(
                    username=username,
                    status=StatusCode.FAILED,
                    details={
                        'start_time':start_time,
                        'end_time':end_time,
                        'operation_details':'Takım oluşturulamadı',
                        'error_message':str(e)
                    }
                )

        tk.Button(team_window, text="Takım Oluştur", command=add_team).pack(pady=10)
        tk.Button(team_window, text="İptal", command=team_window.destroy).pack(pady=5)

        def on_close():
            team_window.destroy()
            current_window.destroy()
            open_main_callback(username)

        team_window.protocol("WM_DELETE_WINDOW", on_close)
        tk.Button(team_window, text="Ana Sayfaya Dön", command=on_close).pack(pady=5)

    def load_users(self):
        users_file = os.path.join(self.root_path, "kayıt.txt")
        users = []
        if os.path.exists(users_file):
            with open(users_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    if "Kullanıcı  Adı:" in line:
                        username = line.split("Kullanıcı  Adı:")[1].split()[0]
                        users.append(username)
        return users

    def load_teams(self):
        with open(self.teams_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_teams(self, teams):
        with open(self.teams_file, 'w', encoding='utf-8') as f:
            json.dump(teams, f,ensure_ascii=False, indent=4)

    def create_notification(self, username, message):
        notifications = self.load_notifications()
        if username not in notifications:
            notifications[username] = []
            
        notifications[username].append({
            "message": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "read": False
        })
        self.save_notifications(notifications)

    def load_notifications(self):
        with open(self.notifications_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_notifications(self, notifications):
        with open(self.notifications_file, 'w', encoding='utf-8') as f:
            json.dump(notifications, f,ensure_ascii=False, indent=4)

    def can_share_file(self, from_user, to_user):
        teams = self.load_teams()
        return (from_user in teams and to_user in teams[from_user]) or \
               (to_user in teams and from_user in teams[to_user])
    
  


    def show_file_sharing_window(self, current_window, username, open_main_callback):
        share_window = tk.Toplevel(current_window)
        share_window.title("Dosya Paylaşımı")
        share_window.geometry('600x500')

        def load_teams():
            try:
                with open('teams.json', 'r', encoding='utf-8') as file:
                    return json.load(file)
            except FileNotFoundError:
                messagebox.showerror("Hata", "teams.json dosyası bulunamadı")
                return {}
            except json.JSONDecodeError:
                messagebox.showerror("Hata", "teams.json dosyası düzgün bir formatta değil")
                return {}

        teams = load_teams()
        username_clean = username.strip()
        team_members = []
        
        if username in teams:
            team_members = teams[username]
        elif username_clean in teams:
            team_members = teams[username_clean]
        elif username + " " in teams:
            team_members = teams[username + " "]

        # Dosya seçme bölümü
        file_frame = tk.LabelFrame(share_window, text="Dosya Seç")
        file_frame.pack(pady=10, padx=10, fill=tk.X)

        selected_file = tk.StringVar()
        file_label = tk.Label(file_frame, textvariable=selected_file, wraplength=400)
        file_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        def select_file():
            filename = filedialog.askopenfilename()
            if filename:
                selected_file.set(filename)
                share_button['state'] = 'normal'

        select_button = tk.Button(file_frame, text="Dosya Seç", command=select_file)
        select_button.pack(side=tk.RIGHT, padx=5)

        # Kullanıcı listesi
        users_frame = tk.LabelFrame(share_window, text="Paylaşılacak Kullanıcılar")
        users_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(users_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        user_listbox = tk.Listbox(users_frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set)
        user_listbox.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
        scrollbar.config(command=user_listbox.yview)

        # Kullanıcıları listbox'a ekle
        if team_members:
            for member in team_members:
                member_clean = member.strip()
                if member_clean != username_clean:
                    user_listbox.insert(tk.END, member_clean)
        else:
            messagebox.showwarning("Uyarı", "Paylaşım yapılabilecek takım üyesi bulunamadı!")

        def share_file():
            selections = user_listbox.curselection()
            selected_filepath = selected_file.get()
            
            if not selections:
                messagebox.showwarning("Uyarı", "Lütfen en az bir kullanıcı seçin")
                return
            if not selected_filepath:
                messagebox.showwarning("Uyarı", "Lütfen bir dosya seçin")
                return

            try:
                selected_users = [user_listbox.get(i) for i in selections]
                start_time = datetime.now()

                for user in selected_users:
                    user_dir = os.path.join(self.shared_files_dir, user.strip())
                    os.makedirs(user_dir, exist_ok=True)
                    dest_file = os.path.join(user_dir, os.path.basename(selected_filepath))
                    shutil.copy2(selected_filepath, dest_file)
                    
                    self.create_notification(
                        user.strip(),
                        f"{username_clean} sizinle '{os.path.basename(selected_filepath)}' dosyasını paylaştı"
                    )

                log_details = {
                    'start_time': start_time,
                    'end_time': datetime.now(),
                    'target_user': ', '.join(selected_users),
                    'message': f"Dosyalar şu kişiler ile paylaşıldı: {', '.join(selected_users)}"
                }

                self.logger.log_doc_sharing(
                    username=username_clean,
                    status=StatusCode.SUCCESS,
                    source_dir=selected_filepath,
                    data_size=os.path.getsize(selected_filepath),
                    details=log_details
                )
                messagebox.showinfo("Başarılı", "Dosya paylaşımı tamamlandı")
                share_window.destroy()
                
            except Exception as e:
                error_details = {
                    'start_time': start_time if 'start_time' in locals() else datetime.now(),
                    'end_time': datetime.now(),
                    'target_user': ', '.join(selected_users) if 'selected_users' in locals() else 'N/A',
                    'message': f"Hata: {str(e)}"
                }
                
                self.logger.log_doc_sharing(
                    username=username_clean,
                    status=StatusCode.FAILED,
                    source_dir=selected_filepath,
                    data_size=None,
                    details=error_details
                )
                messagebox.showerror("Hata", f"Dosya paylaşımı sırasında bir hata oluştu: {e}")

        share_button = tk.Button(share_window, text="Paylaş", command=share_file, state='disabled')
        share_button.pack(pady=10)

        def on_close():
            share_window.destroy()
            current_window.destroy()
            open_main_callback(username_clean)

        share_window.protocol("WM_DELETE_WINDOW", on_close)
        tk.Button(share_window, text="Ana Sayfaya Dön", command=on_close).pack(pady=5)


    def show_shared_files_window(self, current_window, username,open_main_callback):
        files_window = tk.Toplevel(current_window)
        files_window.title("Paylaşılan Dosyalar")
        files_window.geometry('600x400')

        # Dosyaları listele
        user_dir = os.path.join(self.shared_files_dir, username)
        if os.path.exists(user_dir):
            files = os.listdir(user_dir)
            
            if files:
                tree = ttk.Treeview(files_window, columns=('Dosya', 'Tarih'), show='headings')
                tree.heading('Dosya', text='Dosya Adı')
                tree.heading('Tarih', text='Paylaşım Tarihi')
                
                tree.column('Dosya', width=300)
                tree.column('Tarih', width=200)
                
                for file in files:
                    file_path = os.path.join(user_dir, file)
                    modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    tree.insert('', tk.END, values=(file, modified_time.strftime("%Y-%m-%d %H:%M:%S")))
                
                tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

                def open_file():
                    selected_item = tree.selection()
                    if selected_item:
                        file_name = tree.item(selected_item[0])['values'][0]
                        file_path = os.path.join(user_dir, file_name)
                        os.startfile(file_path)

                tk.Button(files_window, text="Dosyayı Aç", command=open_file).pack(pady=5)
            else:
                tk.Label(files_window, text="Henüz paylaşılan dosya bulunmamaktadır.").pack(pady=20)
        else:
            tk.Label(files_window, text="Henüz paylaşılan dosya bulunmamaktadır.").pack(pady=20)
        
        def on_close():
            files_window.destroy()
            current_window.destroy()
            open_main_callback(username)

        files_window.protocol("WM_DELETE_WINDOW", on_close)
        tk.Button(files_window, text="Ana Sayfaya Dön", command=on_close).pack(pady=5)


