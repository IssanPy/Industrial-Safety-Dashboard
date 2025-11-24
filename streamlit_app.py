# app/streamlit_app.py
import streamlit as st
import pandas as pd
import json
import time
from pathlib import Path
import plotly.express as px

ROOT = Path(__file__).resolve().parents[1]
STATUS_FILE = ROOT / 'status_store.json'
ALERTS_FILE = ROOT / 'alerts.json'

st.set_page_config(page_title="Industrial Safety Dashboard", layout="wide")

def load_status():
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text())
        except:
            return {}
    return {}

def load_alerts():
    if ALERTS_FILE.exists():
        try:
            return json.loads(ALERTS_FILE.read_text())
        except:
            return []
    return []

st.title("Industrial Safety Dashboard")
st.markdown("Monitoring simulated industrial endpoints. Demo mode: alerts are logged to `alerts.json`.")

col1, col2 = st.columns([2,1])

with col2:
    st.header("Controls")
    if st.button("Simulate Failure (Telemetry-API-01)"):
        # append simulated error to alerts.json for demo purposes
        alerts = load_alerts()
        alerts.append({
            "time": pd.Timestamp.now().isoformat(),
            "service": "Telemetry-API-01",
            "type": "web",
            "status": "down",
            "info": "Simulated failure by user"
        })
        with open(ALERTS_FILE, 'w') as f:
            json.dump(alerts, f, indent=2)
        st.success("Simulated failure appended")
    if st.button("Clear Alerts"):
        with open(ALERTS_FILE, 'w') as f:
            json.dump([], f)
        st.warning("Alerts cleared")

with col1:
    st.header("System Status")
    status = load_status()
    if not status:
        st.info("No status data yet. Start the monitor script to populate status_store.json")
    else:
        df = pd.DataFrame.from_dict(status, orient='index')
        df = df.reset_index().rename(columns={'index':'service'})
        st.dataframe(df[['service','status','failures','last_checked']].fillna('N/A'), height=300)

# Alerts panel
st.subheader("Incident Log (alerts.json)")
alerts = load_alerts()
if alerts:
    df_alerts = pd.DataFrame(alerts)
    df_alerts['time'] = pd.to_datetime(df_alerts['time'])
    df_alerts = df_alerts.sort_values('time', ascending=False)
    st.dataframe(df_alerts[['time','service','status','info']].head(20))
else:
    st.info("No incidents logged")

# Simple timeline chart of failures over time
if alerts:
    try:
        chart_df = df_alerts.groupby([pd.Grouper(key='time', freq='1Min'), 'service']).size().reset_index(name='count')
        fig = px.line(chart_df, x='time', y='count', color='service', title='Incidents over time')
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.info("Unable to render chart for alerts")

# Embed small Three.js turbine visual using st.components.html
alert_active = any(a.get('status') == 'down' for a in alerts)
color = "#2ecc71" if not alert_active else "#e74c3c"
rotation_speed = 0.02 if not alert_active else 0.12

THREE_HTML = f"""
<!DOCTYPE html><html><head><meta charset="utf-8"></head><body style="margin:0">
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r152/three.min.js"></script>
<div id="canvas"></div>
<script>
let scene = new THREE.Scene();
let camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.1, 1000);
let renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(400,300);
document.body.appendChild(renderer.domElement);

let light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(5,10,7.5);
scene.add(light);

// tower
let towerGeom = new THREE.CylinderGeometry(0.4,0.6,2.5,32);
let towerMat = new THREE.MeshStandardMaterial({{color:0x444444}});
let tower = new THREE.Mesh(towerGeom, towerMat);
tower.position.y = -0.25;
scene.add(tower);

// hub
let hubGeom = new THREE.CylinderGeometry(0.12,0.12,0.6,16);
let hubMat = new THREE.MeshStandardMaterial({{color:0x222222}});
let hub = new THREE.Mesh(hubGeom, hubMat);
hub.position.y = 1.1;
hub.rotation.z = Math.PI/2;
scene.add(hub);

// blades
function makeBlade(angle){
  let bladeGeom = new THREE.BoxGeometry(1.6,0.06,0.2);
  let bladeMat = new THREE.MeshStandardMaterial({{color: '{color}' }});
  let blade = new THREE.Mesh(bladeGeom, bladeMat);
  blade.position.y = 1.1;
  blade.rotation.z = angle;
  blade.translateX(0.8);
  return blade;
}
let blades = new THREE.Group();
blades.add(makeBlade(0));
blades.add(makeBlade(2.094));
blades.add(makeBlade(4.188));
scene.add(blades);

camera.position.z = 5;
function animate(){
    requestAnimationFrame(animate);
    blades.rotation.z += {rotation_speed};
    renderer.render(scene, camera);
}
animate();
</script>
</body></html>
"""

st.subheader("3D Turbine (visual)")
st.components.v1.html(THREE_HTML, height=320)
st.caption("Turbine speed and color reflect alert state (red = alert).")
