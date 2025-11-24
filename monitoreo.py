# monitoring/monitoreo.py
import requests
import logging
import json
import platform
import socket
import time
from datetime import datetime
from abc import ABC, abstractmethod
import sys
import os
from logging.handlers import RotatingFileHandler
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

ROOT = os.path.dirname(os.path.dirname(__file__)) if os.path.basename(__file__) == 'monitoreo.py' else os.getcwd()
CONFIG_PATH = os.path.join(ROOT, 'config.json')
ALERTS_FILE = os.path.join(ROOT, 'alerts.json')
STATUS_STORE = os.path.join(ROOT, 'status_store.json')

def load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {
            'websites': {},
            'databases': {},
            'email': {},
            'monitor_settings': {},
            'logging_settings': {}
        }

def setup_logging():
    config = load_config()
    logging_config = config.get('logging_settings', {
        'enable_file_logging': True,
        'max_bytes': 5*1024*1024,
        'backup_count': 5,
        'log_file': 'monitor_servicios.log'
    })
    logger = logging.getLogger('issandash')
    logger.setLevel(logging.INFO)
    for h in list(logger.handlers):
        logger.removeHandler(h)
    fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    if logging_config.get('enable_file_logging', True):
        fh = RotatingFileHandler(logging_config['log_file'],
                                 maxBytes=logging_config['max_bytes'],
                                 backupCount=logging_config['backup_count'],
                                 encoding='utf-8')
        fh.setFormatter(fmt)
        logger.addHandler(fh)
        logger.info(f"File logging enabled -> {logging_config['log_file']}")
    else:
        logger.info("File logging disabled by config")
    return logger

logger = setup_logging()

class ServiceStatus:
    def __init__(self):
        self.failures = {}
        self.successes = {}
        self.last_alert = {}
        self.is_down = {}

    def record_failure(self, name):
        self.failures[name] = self.failures.get(name, 0) + 1
        self.successes[name] = 0
        return self.failures[name]

    def record_success(self, name):
        self.successes[name] = self.successes.get(name, 0) + 1
        self.failures[name] = 0
        return self.successes[name]

    def should_alert(self, name, threshold, repeat_interval):
        current_failures = self.failures.get(name, 0)
        last_time = self.last_alert.get(name)
        if current_failures < threshold:
            return False
        if last_time is None:
            return True
        elapsed = (datetime.now() - last_time).total_seconds()
        return elapsed >= repeat_interval

    def mark_alerted(self, name):
        self.last_alert[name] = datetime.now()
        self.is_down[name] = True

    def is_recovered(self, name, threshold):
        return (self.is_down.get(name, False) and self.successes.get(name, 0) >= threshold)

    def mark_recovered(self, name):
        if name in self.last_alert:
            del self.last_alert[name]
        self.is_down[name] = False

class SystemInfo:
    @staticmethod
    def get_system_info():
        return {
            'hostname': socket.gethostname(),
            'system': platform.system(),
            'release': platform.release(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }

def check_website(url, retry_attempts=3, retry_delay=5):
    headers = {'User-Agent': 'IndustrialSafetyMonitor/1.0'}
    for attempt in range(retry_attempts):
        try:
            r = requests.get(url, timeout=10, headers=headers)
            if r.status_code == 200:
                return True
            logger.warning(f"Attempt {attempt+1} failed (status {r.status_code}) for {url}")
            if attempt < retry_attempts - 1:
                time.sleep(retry_delay)
        except requests.RequestException as e:
            logger.error(f"Attempt {attempt+1} exception: {e}")
            if attempt < retry_attempts - 1:
                time.sleep(retry_delay)
    return False

def write_alert_record(payload):
    existing = []
    if os.path.exists(ALERTS_FILE):
        try:
            with open(ALERTS_FILE, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except Exception:
            existing = []
    existing.append(payload)
    with open(ALERTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(existing, f, indent=2, default=str)
    logger.info("Alert appended to alerts.json")

def send_alert_email_or_log(service_name, service_type, status="down", additional_info=None):
    cfg = load_config().get('email', {})
    # if credentials exist, attempt SMTP (kept safe). Otherwise, write to alerts.json for demo.
    if cfg.get('sender_password'):
        try:
            server = smtplib.SMTP(cfg['smtp_server'], cfg['smtp_port'])
            server.ehlo()
            if cfg.get('smtp_use_tls'):
                server.starttls()
                server.ehlo()
            if cfg.get('sender_password'):
                server.login(cfg['sender_email'], cfg['sender_password'])
            recipients = cfg.get('recipient_emails', [])
            for rcpt in recipients:
                msg = MIMEMultipart()
                msg['From'] = cfg['sender_email']
                msg['To'] = rcpt
                sub = f"ALERT: {service_name}" if status == "down" else f"RECOVERED: {service_name}"
                msg['Subject'] = sub
                body = f"Service: {service_name}\nType: {service_type}\nStatus: {status}\nTime: {datetime.now()}\n\nSystem: {SystemInfo.get_system_info()}"
                msg.attach(MIMEText(body, 'plain'))
                server.send_message(msg)
            server.quit()
            logger.info("SMTP alerts sent (credentials provided)")
            return
        except Exception as e:
            logger.error(f"SMTP failed: {e} -- falling back to alerts.json")

    # fallback: write to alerts.json
    payload = {
        "time": datetime.now().isoformat(),
        "service": service_name,
        "type": service_type,
        "status": status,
        "info": additional_info,
        "system": SystemInfo.get_system_info()
    }
    write_alert_record(payload)

def save_status_store(store):
    try:
        with open(STATUS_STORE, 'w', encoding='utf-8') as f:
            json.dump(store, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Failed saving status_store: {e}")

def monitor_services():
    cfg = load_config()
    status_tracker = ServiceStatus()
    store = {}
    websites = cfg.get('websites', {})
    if not websites and not cfg.get('databases', {}):
        logger.error("No services configured to monitor. Exiting.")
        sys.exit(1)
    logger.info("Starting Industrial Safety Monitor")
    for name in websites:
        store[name] = {"status": "unknown", "last_checked": None, "failures": 0}
    save_status_store(store)
    while True:
        try:
            start = datetime.now()
            for name, url in websites.items():
                logger.info(f"Checking {name} -> {url}")
                ok = check_website(url,
                                   cfg['monitor_settings'].get('retry_attempts', 2),
                                   cfg['monitor_settings'].get('retry_delay', 3))
                if not ok:
                    fails = status_tracker.record_failure(name)
                    store[name]['failures'] = fails
                    store[name]['status'] = "down"
                    store[name]['last_checked'] = datetime.now().isoformat()
                    if status_tracker.should_alert(name,
                                                   cfg['monitor_settings'].get('alert_threshold', 2),
                                                   cfg['monitor_settings'].get('alert_repeat_interval', 120)):
                        logger.error(f"{name} is DOWN: sending alert/log")
                        send_alert_email_or_log(name, "web", status="down")
                        status_tracker.mark_alerted(name)
                else:
                    succ = status_tracker.record_success(name)
                    store[name]['status'] = "up"
                    store[name]['last_checked'] = datetime.now().isoformat()
                    store[name]['failures'] = 0
                    if status_tracker.is_recovered(name, cfg['monitor_settings'].get('recovery_threshold', 2)):
                        logger.info(f"{name} recovered: sending recover notification/log")
                        send_alert_email_or_log(name, "web", status="recovered")
                        status_tracker.mark_recovered(name)
                save_status_store(store)
            end = datetime.now()
            exec_time = (end - start).total_seconds()
            wait = max(1, cfg['monitor_settings'].get('check_interval', 30) - exec_time)
            logger.info(f"Cycle complete. Sleeping {wait}s")
            time.sleep(wait)
        except KeyboardInterrupt:
            logger.info("Monitor interrupted by user. Exiting.")
            break
        except Exception as e:
            logger.error(f"Unexpected error in monitor loop: {e}")
            time.sleep(30)

if __name__ == "__main__":
    monitor_services()
