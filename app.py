import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Kosmon Data Center Dashboard",
    page_icon="🖥️",
    layout="wide"
)

# Auto-refresh every 5 seconds
st_autorefresh(interval=5000, key="refresh")

# -----------------------------
# LOAD DATA
# -----------------------------
servers = pd.read_csv("data/server_data_with_status.csv")

# -----------------------------
# CONSTANTS
# -----------------------------
DARK_BG = "#0e1117"
CARD_BG = "#161b22"

STATUS_COLORS = {
    "Healthy": "#3fb950",
    "Warning": "#d29922",
    "Critical": "#ff4b4b"
}

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def get_gauge_color(value, warning, critical):
    if value >= critical:
        return "#ff4b4b"
    elif value >= warning:
        return "#f0ad4e"
    else:
        return "#00cc66"


def apply_dark_theme(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=DARK_BG,
        plot_bgcolor=DARK_BG,
        font=dict(color="#f5f5f5"),
        margin=dict(l=30, r=30, t=60, b=30)
    )
    return fig


# -----------------------------
# SUMMARY METRICS
# -----------------------------
total_servers = len(servers)
healthy_servers = len(servers[servers["Status"] == "Healthy"])
warning_servers = len(servers[servers["Status"] == "Warning"])
critical_servers = len(servers[servers["Status"] == "Critical"])

avg_cpu = round(servers["CPU_Usage"].mean(), 2)
avg_memory = round(servers["Memory_Usage"].mean(), 2)
avg_temp = round(servers["Temperature"].mean(), 2)
avg_power = round(servers["Power_Usage"].mean(), 2)
avg_network = round(servers["Network_Traffic"].mean(), 2)

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: #f5f5f5;
}

section[data-testid="stSidebar"] {
    background-color: #f3f6fa;
}

.metric-card {
    background-color: #161b22;
    padding: 22px;
    border-radius: 14px;
    border: 1px solid #30363d;
    text-align: center;
    min-height: 130px;
}

.metric-card h3 {
    margin-bottom: 12px;
    color: #8b949e;
    font-size: 22px;
}

.metric-card h1 {
    margin-top: 0;
    color: white;
    font-size: 38px;
}

.alert-header {
    background: linear-gradient(90deg, #2d1117, #161b22);
    border-left: 5px solid #ff4b4b;
    padding: 14px 18px;
    border-radius: 10px;
    margin-bottom: 10px;
}

.stDownloadButton > button {
    background-color: #1f6feb;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 10px 18px;
    font-weight: bold;
}

.stDownloadButton > button:hover {
    background-color: #388bfd;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.title("🖥️ Kosmon Data Center Monitoring Dashboard")
st.write(
    "Enterprise-style monitoring dashboard for simulated server health, power, "
    "temperature, CPU, memory, and network activity."
)

current_time = datetime.now().strftime("%B %d, %Y | %I:%M:%S %p")
st.caption(f"Last updated: {current_time}")

# -----------------------------
# SIDEBAR CONTROLS
# -----------------------------
st.sidebar.title("🛠️ Dashboard Controls")
st.sidebar.markdown("---")

st.sidebar.success(f"Healthy: {healthy_servers}")
st.sidebar.warning(f"Warning: {warning_servers}")
st.sidebar.error(f"Critical: {critical_servers}")

status_filter = st.sidebar.multiselect(
    "Filter by server status",
    options=servers["Status"].unique(),
    default=servers["Status"].unique()
)

server_search = st.sidebar.text_input("Search server name")

filtered_servers = servers[servers["Status"].isin(status_filter)]

if server_search:
    filtered_servers = filtered_servers[
        filtered_servers["Server"].str.contains(server_search, case=False, na=False)
    ]

# -----------------------------
# LIVE ALERT CENTER
# -----------------------------
critical_alerts = (
    filtered_servers[filtered_servers["Status"] == "Critical"]
    .sort_values(["CPU_Usage", "Memory_Usage", "Temperature"], ascending=False)
    .head(10)
)

st.subheader("🚨 Live Alert Center")

if len(critical_alerts) > 0:
    for _, row in critical_alerts.iterrows():
        st.error(
            f"🚨 {row['Server']} | CPU: {row['CPU_Usage']}% | "
            f"Memory: {row['Memory_Usage']}% | "
            f"Temperature: {row['Temperature']}°C | "
            f"Power: {row['Power_Usage']}W | "
            f"Network: {row['Network_Traffic']} Mbps"
        )
else:
    st.success("✅ No critical server alerts at this time.")

st.divider()

# -----------------------------
# KPI CARDS
# -----------------------------
col1, col2, col3, col4, col5 = st.columns(5)

col1.markdown(
    f"<div class='metric-card'><h3>🖥️ Total Servers</h3><h1>{total_servers}</h1></div>",
    unsafe_allow_html=True
)

col2.markdown(
    f"<div class='metric-card'><h3>🟢 Healthy</h3><h1 style='color:#3fb950'>{healthy_servers}</h1></div>",
    unsafe_allow_html=True
)

col3.markdown(
    f"<div class='metric-card'><h3>⚠️ Warning</h3><h1 style='color:#d29922'>{warning_servers}</h1></div>",
    unsafe_allow_html=True
)

col4.markdown(
    f"<div class='metric-card'><h3>🔴 Critical</h3><h1 style='color:#ff4b4b'>{critical_servers}</h1></div>",
    unsafe_allow_html=True
)

col5.markdown(
    f"<div class='metric-card'><h3>🌡️ Avg Temp °C</h3><h1>{avg_temp}</h1></div>",
    unsafe_allow_html=True
)

st.divider()

# -----------------------------
# OPERATIONAL GAUGES
# -----------------------------
st.subheader("📊 Operational Gauges")

g1, g2, g3, g4 = st.columns(4)

cpu_color = get_gauge_color(avg_cpu, 70, 85)
temp_color = get_gauge_color(avg_temp, 35, 40)
power_color = get_gauge_color(avg_power, 650, 800)
network_color = get_gauge_color(avg_network, 750, 900)

cpu_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=avg_cpu,
    title={"text": "Average CPU %"},
    gauge={
        "axis": {"range": [0, 100]},
        "bar": {"color": cpu_color}
    }
))
apply_dark_theme(cpu_gauge)

temp_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=avg_temp,
    title={"text": "Average Temp °C"},
    gauge={
        "axis": {"range": [0, 100]},
        "bar": {"color": temp_color}
    }
))
apply_dark_theme(temp_gauge)

power_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=avg_power,
    title={"text": "Average Power Watts"},
    gauge={
        "axis": {"range": [0, 900]},
        "bar": {"color": power_color}
    }
))
apply_dark_theme(power_gauge)

network_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=avg_network,
    title={"text": "Average Network Mbps"},
    gauge={
        "axis": {"range": [0, 1000]},
        "bar": {"color": network_color}
    }
))
apply_dark_theme(network_gauge)

g1.plotly_chart(cpu_gauge, width="stretch")
g2.plotly_chart(temp_gauge, width="stretch")
g3.plotly_chart(power_gauge, width="stretch")
g4.plotly_chart(network_gauge, width="stretch")

# -----------------------------
# SERVER HEALTH OVERVIEW
# -----------------------------
st.subheader("Server Health Overview")

status_counts = servers["Status"].value_counts().reset_index()
status_counts.columns = ["Status", "Count"]

fig_status = px.bar(
    status_counts,
    x="Status",
    y="Count",
    color="Status",
    color_discrete_map=STATUS_COLORS,
    title="Server Health Status Count",
    labels={"Count": "Number of Servers"}
)
apply_dark_theme(fig_status)
st.plotly_chart(fig_status, width="stretch")

# -----------------------------
# CPU VS TEMPERATURE
# -----------------------------
st.subheader("CPU Usage vs Temperature")

fig_scatter = px.scatter(
    filtered_servers,
    x="CPU_Usage",
    y="Temperature",
    color="Status",
    color_discrete_map=STATUS_COLORS,
    size="Power_Usage",
    hover_name="Server",
    hover_data=["Memory_Usage", "Network_Traffic", "Power_Usage"],
    title="CPU Usage vs Temperature by Server"
)
apply_dark_theme(fig_scatter)
st.plotly_chart(fig_scatter, width="stretch")

# -----------------------------
# TOP 10 CPU USAGE
# -----------------------------
st.subheader("🔥 Top 10 Highest CPU Usage")

top_cpu = (
    filtered_servers
    .sort_values("CPU_Usage", ascending=False)
    .head(10)
)

fig_top_cpu = px.bar(
    top_cpu,
    x="Server",
    y="CPU_Usage",
    color="Status",
    color_discrete_map=STATUS_COLORS,
    title="Top 10 Servers by CPU Usage"
)
apply_dark_theme(fig_top_cpu)
st.plotly_chart(fig_top_cpu, width="stretch")

# -----------------------------
# TOP 10 HOTTEST SERVERS
# -----------------------------
st.subheader("🌡️ Top 10 Hottest Servers")

top_temp = (
    filtered_servers
    .sort_values("Temperature", ascending=False)
    .head(10)
)

fig_top_temp = px.bar(
    top_temp,
    x="Server",
    y="Temperature",
    color="Status",
    color_discrete_map=STATUS_COLORS,
    title="Top 10 Servers by Temperature"
)
apply_dark_theme(fig_top_temp)
st.plotly_chart(fig_top_temp, width="stretch")

# -----------------------------
# POWER USAGE
# -----------------------------
st.subheader("Power Usage by Server")

fig_power = px.bar(
    filtered_servers,
    x="Server",
    y="Power_Usage",
    color="Status",
    color_discrete_map=STATUS_COLORS,
    title="Power Usage Across Servers"
)
apply_dark_theme(fig_power)
st.plotly_chart(fig_power, width="stretch")

# -----------------------------
# NETWORK TRAFFIC
# -----------------------------
st.subheader("Network Traffic by Server")

fig_network = px.line(
    filtered_servers,
    x="Server",
    y="Network_Traffic",
    color="Status",
    color_discrete_map=STATUS_COLORS,
    title="Network Traffic Across Servers"
)
apply_dark_theme(fig_network)
st.plotly_chart(fig_network, width="stretch")

# -----------------------------
# SERVER DATA TABLE
# -----------------------------
st.subheader("Server Data Table")
st.dataframe(filtered_servers, width="stretch")

csv = filtered_servers.to_csv(index=False)

st.download_button(
    "⬇ Download Current Server Report",
    csv,
    "server_report.csv",
    "text/csv"
)