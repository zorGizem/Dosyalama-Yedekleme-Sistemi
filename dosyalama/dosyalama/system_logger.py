from enum import Enum
import os
import json
from datetime import datetime
import logging

class LogType(Enum):
    TEAM_MANAGEMENT = "TEAM_MANAGEMENT"  # Takım üyesi belirleme
    DOC_SHARING = "DOC_SHARING"      # Doküman paylaşımı
    PASSWORD_REQUEST = "PASSWORD_REQUEST" # Parola değiştirme talebi
    PASSWORD_ACCEPT = "PASSWORD_ACCEPT" # Parola değiştirme onayı
    PROFILE_ACCESS = "PROFILE_ACCESS"   # Profile giriş
    CHANGE_USERNAME = "CHANGE_USERNAME"
    BACKUP = "BACKUP"          # Yedekleme
    ANOMALY = "ANOMALY"         # Anormal durum

class StatusCode(Enum):
    SUCCESS = "SUCCESS"          # Başarılı
    FAILED = "FAILED"           # Başarısız
    PENDING = "PENDİNG"          # Beklemede
    APPROVED = "APPROVED"         # Onaylandı
    REJECTED = "REJECTED"         # Reddedildi

class SystemLogger:
    def __init__(self, root_path):
        self.root_path = root_path
        self.logs_dir = os.path.join(root_path, "logs")
        self.ensure_log_directories()
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def ensure_log_directories(self):
        log_types = [
            "team_management",
            "doc_sharing",
            "password_request",
            "password_accept",
            "profile_access",
            "change_username",
            "backup",
            "anomalies"
        ]
        
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
            
        for log_type in log_types:
            dir_path = os.path.join(self.logs_dir, log_type)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

    def _write_log(self, log_type: LogType, log_entry: str):
        log_file = os.path.join(
            self.logs_dir,
            log_type.name.lower(),
            f"{datetime.now().strftime('%Y%m')}_log.txt"
        )
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Log kaydı oluşturulurken hata: {str(e)}")

    def log_team_management(self, username, status: StatusCode, details):
        log_entry = (
            f"Kullanıcı: {username}\n"
            f"İşlem Başlangıç: {details.get('start_time', datetime.now())}\n"
            f"İşlem Bitiş: {details.get('end_time', datetime.now())}\n"
            f"İşlem Türü: TEAM_MANAGEMENT\n"
            f"Durum Kodu: {status.value}\n"
            f"Detaylar: {details.get('action', 'N/A')}\n"
            f"İşlem Detayı: {details.get('operation_details', 'N/A')}\n"  # İşlem detayı alanı eklendi
            f"Hata Detayı: {details.get('error_message', 'N/A')}\n"  
            f"------------------------\n"
        )
        logging.info(f"Kullanıcı: {username}, İşlem: Takım Yönetimi, Durum: {status.value}")
        self._write_log(LogType.TEAM_MANAGEMENT, log_entry)

    def log_doc_sharing(self, username, status: StatusCode, source_dir, data_size, details):
        log_entry = (
            f"Kullanıcı: {username}\n"
            f"İşlem Başlangıç: {details.get('start_time', datetime.now())}\n"
            f"İşlem Bitiş: {details.get('end_time', datetime.now())}\n"
            f"İşlem Türü: DOC_SHARING\n"
            f"Durum Kodu: {status.value}\n"
            f"Kaynak Dizin: {source_dir}\n"
            f"Hedef Kullanıcı: {details.get('target_user', 'N/A')}\n"
            f"Veri Boyutu: {data_size} bytes\n"
            f"------------------------\n"
        )
        logging.info(f"Kullanıcı: {username}, İşlem: Doküman Paylaşımı, Durum: {status.value}")
        self._write_log(LogType.DOC_SHARING, log_entry)

    def log_password_request(self, username, status: StatusCode, details):
        log_entry = (
            f"Kullanıcı: {username}\n"
            f"İşlem Başlangıç: {details.get('start_time', datetime.now())}\n"
            f"İşlem Bitiş: {details.get('end_time', datetime.now())}\n"
            f"İşlem Türü: PASSWORD_REQUEST\n"
            f"Durum Kodu: {status.value}\n"
            f"Talep Nedeni: {details.get('reason', 'N/A')}\n"
            f"İşlem Detayı: {details.get('operation_details', 'N/A')}\n"  # İşlem detayı alanı eklendi
            f"Hata Detayı: {details.get('error_message', 'N/A')}\n"  
            f"------------------------\n"
        )
        logging.info(f"Kullanıcı: {username}, İşlem: Parola Değişiklik Talebi, Durum: {status.value}")
        self._write_log(LogType.PASSWORD_REQUEST, log_entry)


    def log_password_accept(self, username,admin_username, status: StatusCode, details):
        """
        Parola değiştirme onayı için log kaydı oluşturur
        """
        log_entry = (
            f"Kullanıcı: {admin_username}\n"
            f"İşlem Başlangıç: {details.get('start_time', datetime.now())}\n"
            f"İşlem Bitiş: {details.get('end_time', datetime.now())}\n"
            f"İşlem Türü: PASSWORD_ACCEPT\n"
            f"Durum Kodu: {status.value}\n"
            f"İşlem Yapan Admin: {details.get('admin_username', 'N/A')}\n"
            f"İşlem Detayı: {details.get('operation_details', 'N/A')}\n"
            f"Hata Detayı: {details.get('error_message', 'N/A')}\n"
            f"------------------------\n"
        )
        logging.info(f"Kullanıcı: {username}, İşlem: Parola Değişiklik Onayı, Durum: {status.value}")
        self._write_log(LogType.PASSWORD_ACCEPT, log_entry)
    

    def log_profile_access(self, username, status: StatusCode, details):
        log_entry = (
            f"Kullanıcı: {username}\n"
            f"İşlem Başlangıç: {details.get('start_time', datetime.now())}\n"
            f"İşlem Bitiş: {details.get('end_time', datetime.now())}\n"
            f"İşlem Türü: PROFILE_ACCESS\n"
            f"Durum Kodu: {status.value}\n"
            f"Erişim Tipi: {details.get('access_type', 'N/A')}\n"
            f"İşlem Detayı: {details.get('operation_details', 'N/A')}\n"  # İşlem detayı alanı eklendi
            f"Hata Detayı: {details.get('error_message', 'N/A')}\n"  
            #f"IP Adresi: {details.get('ip_address', 'N/A')}\n"
            f"------------------------\n"
        )
        logging.info(f"Kullanıcı: {username}, İşlem: Profil Erişimi, Durum: {status.value}")
        self._write_log(LogType.PROFILE_ACCESS, log_entry)

    def log_change_username(self, username, status: StatusCode, details):
        log_entry = (
            f"Kullanıcı: {username}\n"
            f"İşlem Başlangıç: {details.get('start_time', datetime.now())}\n"
            f"İşlem Bitiş: {details.get('end_time', datetime.now())}\n"
            f"İşlem Türü: CHANGE_USERNAME\n"
            f"Durum Kodu: {status.value}\n"
            f"Eski Kullanıcı Adı: {details.get('old_username','N/A')}\n"
            f"Yeni Kullanıcı Adı: {details.get('new_username', 'N/A')}\n"
            f"İşlem Detayı: {details.get('operation_details', 'N/A')}\n"  # İşlem detayı alanı eklendi
            f"Hata Detayı: {details.get('error_message', 'N/A')}\n"  
            f"------------------------\n"
        )
        logging.info(f"Kullanıcı: {username}, İşlem: Kullanıcı Adı Değişikliği, Durum: {status.value}")
        self._write_log(LogType.CHANGE_USERNAME, log_entry)

    def log_backup(self, username, status: StatusCode, source_dir, data_size, details):
        log_entry = (
            f"Kullanıcı: {username}\n"
            f"İşlem Başlangıç: {details.get('start_time', datetime.now())}\n"
            f"İşlem Bitiş: {details.get('end_time', datetime.now())}\n"
            f"İşlem Türü: BACKUP\n"
            f"Durum Kodu: {status.value}\n"
            f"Kaynak Dizin: {source_dir}\n"
            f"Yedek Dizin: {details.get('backup_path', 'N/A')}\n"
            f"Veri Boyutu: {data_size} bytes\n"
            f"İşlem Detayı: {details.get('operation_details', 'N/A')}\n"  # İşlem detayı alanı eklendi
            f"Hata Detayı: {details.get('error_message', 'N/A')}\n" 
            f"------------------------\n"
        )
        logging.info(f"Kullanıcı: {username}, İşlem: Yedekleme, Durum: {status.value}")
        self._write_log(LogType.BACKUP, log_entry)

    def log_anomaly(self, username, status: StatusCode, details):
        log_entry = (
            f"Kullanıcı: {username}\n"
            f"İşlem Başlangıç: {details.get('start_time', datetime.now())}\n"
            f"İşlem Bitiş: {details.get('end_time', datetime.now())}\n"
            f"İşlem Türü: ANOMALY\n"
            f"Durum Kodu: {status.value}\n"
            f"Anomali Tipi: {details.get('anomaly_type', 'N/A')}\n"
            f"Açıklama: {details.get('description', 'N/A')}\n"
            f"------------------------\n"
        )
        logging.info(f"Kullanıcı: {username}, İşlem: Anormal Durum, Durum: {status.value}")
        self._write_log(LogType.ANOMALY, log_entry)

    def get_logs_by_type(self, log_type: LogType, start_date=None, end_date=None):
        log_dir = os.path.join(self.logs_dir, log_type.name.lower())
        all_logs = []

        for file in os.listdir(log_dir):
            if file.endswith('_log.txt'):
                with open(os.path.join(log_dir, file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    logs = content.split('------------------------\n')
                    for log in logs:
                        if log.strip():
                            all_logs.append(log.strip())

        return all_logs