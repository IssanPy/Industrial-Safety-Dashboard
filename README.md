Industrial Safety Dashboard

Industrial Safety Dashboard is an adapted open-source monitoring system that simulates industrial telemetry, detects service outages, logs incidents, and visualizes system health in real time. This version adds an interactive Streamlit dashboard, file-based alert logging for safe demos, timeline analytics, and a small 3D turbine visual whose color and speed reflect alert state.

This project demonstrates HS&E-aligned alerting behavior, monitoring pipelines, incident recording, and operator-facing visualization — material directly relevant to energy operations and predictive-maintenance workflows.

Features

Continuous monitoring of configured endpoints (APIs / operator portals).

Retry mechanism and configurable thresholds for robust detection.

Smart detection of failures and recoveries with alert suppression.

File-based alert logging (alerts.json) for safe demos (SMTP optional).

Live state store (status_store.json) used by the dashboard.

Streamlit dashboard with:

Status table (service, status, failures, last checked)

Incident log (alerts.json)

Incidents timeline chart

Buttons to simulate failures and clear alerts

Embedded 3D turbine visual (Three.js) that changes color/rotation on alerts

Rotating logfile (monitor_servicios.log).

English translation of the monitoring engine and clear demo hooks.

Project layout
Industrial-Safety-Dashboard/
├─ monitoring/
│  └─ monitoreo.py          # Main monitor (English, safe demo mode)
├─ app/
│  └─ streamlit_app.py      # Streamlit dashboard + 3D visual
├─ config.json              # Configuration (endpoints, thresholds, logging)
├─ requirements.txt         # Python dependencies
├─ status_store.json        # Generated: stores live status
├─ alerts.json              # Generated: incident log
├─ monitor_servicios.log    # Generated rotating log
└─ README.md                # This file

Prerequisites

Python 3.8+

pip (package manager)

Git (optional, for pushing to GitHub)

Internet access for demo endpoints and Three.js CDN

Write permissions in project directory

Required Python packages

Minimal packages required (add others if needed):

requests==2.28.1
streamlit==1.22.0
plotly==5.15.0


Install via:

pip install -r requirements.txt

Configuration

Edit config.json to list the endpoints and tune thresholds. Example (already provided in repo):

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
  },
  "logging_settings": {
    "enable_file_logging": true,
    "max_bytes": 5242880,
    "backup_count": 5,
    "log_file": "monitor_servicios.log"
  }
}


Notes:

Leave sender_password empty for demo mode (alerts go to alerts.json instead of SMTP).

check_interval is seconds between cycles. Lower for faster demos.