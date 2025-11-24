# Industrial Safety Dashboard  
Real-time industrial telemetry monitoring with HS&E-aligned alerting, incident logging, a Streamlit dashboard, and a 3D turbine visualization that reacts to system health.

![status](https://img.shields.io/badge/status-active-success)
![python](https://img.shields.io/badge/Python-3.8+-blue)
![streamlit](https://img.shields.io/badge/Streamlit-dashboard-red)
![license](https://img.shields.io/badge/license-MIT-green)

---

## 🚀 Overview
Industrial Safety Dashboard is an enhanced monitoring system designed to simulate industrial telemetry, detect service outages, and visualize system health in real-time.  
Built for operations, reliability engineering, and HS&E workflows, the platform:

- Monitors services using retry thresholds  
- Detects failures & recoveries intelligently  
- Logs all alerts into a structured incident file  
- Provides an interactive dashboard to visualize system health  
- Includes a **3D turbine** whose **color & speed change** when alerts fire  

This project is ideal for demonstrating monitoring workflows used in the **energy, industrial, and safety engineering** sectors.

---

## 🛠 Features
### Monitoring Engine
- Continuous monitoring of configured endpoints  
- Configurable retry logic, thresholds & alert intervals  
- Smart detection of failure & recovery states  
- Rotating logfile (`monitor_servicios.log`)  
- Demo-safe alerting (writes to `alerts.json` instead of sending SMTP emails)

### Dashboard (Streamlit)
- Live status table  
- Incident log viewer  
- Incident timeline chart (Plotly)  
- Buttons to simulate failures  
- Embedded **3D turbine** (Three.js) that reflects alert state  

### 3D Visualization
- Normal state → green turbine, slow rotation  
- Alert state → red turbine, fast rotation  

---

## 📂 Project Structure
Industrial-Safety-Dashboard/
│
├── monitoring/
│ └── monitoreo.py # Monitoring engine (English + alert logging)
│
├── app/
│ └── streamlit_app.py # Streamlit dashboard + 3D turbine
│
├── config.json # Configurable endpoints & thresholds
├── status_store.json # Generated: live service state
├── alerts.json # Generated: incident log
├── monitor_servicios.log # Generated: rotating log file
├── requirements.txt
└── README.md

yaml
Copy code

---

## ⚙️ Installation

### 1. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate     # Mac/Linux
.venv\Scripts\activate.ps1    # Windows PowerShell
2. Install dependencies
bash
Copy code
pip install -r requirements.txt
🧩 Configuration
Edit config.json to set endpoints and thresholds.

Example:

json
Copy code
{
  "websites": {
    "Telemetry-API-01": "https://postman-echo.com/get?service=telemetry1",
    "Operator-Portal-01": "https://postman-echo.com/get?service=portal1"
  },
  "email": {
    "smtp_server": "mail.example.com",
    "smtp_port": 587,
    "smtp_use_tls": true,
    "sender_email": "alerts@example.com",
    "sender_password": ""
  },
  "monitor_settings": {
    "check_interval": 30,
    "retry_attempts": 2,
    "retry_delay": 3,
    "alert_threshold": 2,
    "recovery_threshold": 2,
    "alert_repeat_interval": 120
  }
}
Leaving "sender_password": "" enables safe demo mode.

▶️ Running the Monitor
Start the real-time monitor:

bash
Copy code
python monitoring/monitoreo.py
This creates:

status_store.json

alerts.json

monitor_servicios.log

🖥️ Running the Dashboard
Open a second terminal:

bash
Copy code
streamlit run app/streamlit_app.py
Dashboard features:

Live service table

Incident logs

Timeline analytics

Buttons: “Simulate Failure” & “Clear Alerts”

Interactive 3D turbine

📊 Demo Flow (great for internship interviews)
Start the monitor

Open dashboard

Click Simulate Failure

Watch:

alerts.json update

Incident log update

Turbine turn red and spin faster

Clear incidents to reset

Perfect 20–30s demo for recruiters.

🔧 Future Improvements (optional)
Add real sensor ingestion

Add role-based authentication

Add machine learning anomaly detection

Add WebSocket push updates

📜 License
MIT License — free to use and modify.

⭐ If you find this useful, star the repository!
It helps the project grow and makes your GitHub look more active.












ChatGPT can make mistakes. Che
