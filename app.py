import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SAP CostShield V2 PRO",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# PROFESSIONAL UI
# ============================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at 15% 10%, #102c45 0%, transparent 30%),
        radial-gradient(circle at 85% 20%, #10263b 0%, transparent 28%),
        #050b14;
    color: #edf7ff;
}

[data-testid="stSidebar"] {
    background: #07121f;
    border-right: 1px solid #1d3b55;
}

.block-container {
    max-width: 1500px;
    padding-top: 1.2rem;
}

.hero {
    padding: 24px;
    border-radius: 18px;
    background:
        linear-gradient(135deg,
        rgba(14,43,66,.98),
        rgba(6,16,28,.98));
    border: 1px solid #24516e;
    box-shadow: 0 10px 40px rgba(0,0,0,.3);
    margin-bottom: 18px;
}

.hero-title {
    font-size: 2.35rem;
    font-weight: 900;
    letter-spacing: .03em;
}

.hero-sub {
    color: #91abc0;
    margin-top: 5px;
}

.kpi {
    padding: 18px;
    border-radius: 15px;
    background: linear-gradient(145deg,#10263a,#091522);
    border: 1px solid #23465e;
    min-height: 115px;
}

.kpi-label {
    color: #8ea7bb;
    font-size: .75rem;
    text-transform: uppercase;
    letter-spacing: .08em;
}

.kpi-value {
    font-size: 1.65rem;
    font-weight: 850;
    margin-top: 8px;
}

.kpi-small {
    color: #6fd8ff;
    font-size: .78rem;
    margin-top: 4px;
}

.section {
    font-size: 1.35rem;
    font-weight: 800;
    margin-top: 18px;
    margin-bottom: 12px;
}

.status {
    display: inline-block;
    padding: 5px 11px;
    border-radius: 20px;
    font-size: .72rem;
    font-weight: 800;
}

.safe {
    color: #6fffa8;
    border: 1px solid #276b4a;
    background: #0b2b1d;
}

.warning {
    color: #ffd56a;
    border: 1px solid #756126;
    background: #2c250b;
}

.danger {
    color: #ff7e7e;
    border: 1px solid #713030;
    background: #300f0f;
}

.info {
    color: #6fd8ff;
    border: 1px solid #24536d;
    background: #0b2637;
}

div[data-testid="stMetric"] {
    background: #0c1c2c;
    padding: 12px;
    border-radius: 12px;
    border: 1px solid #1d3b52;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "mitigated_pos" not in st.session_state:
    st.session_state.mitigated_pos = set()

if "audit_log" not in st.session_state:
    st.session_state.audit_log = []

if "scenario_history" not in st.session_state:
    st.session_state.scenario_history = []


# ============================================================
# SAMPLE DATA ENGINE
# ============================================================

@st.cache_data
def generate_data(n=180):

    rng = np.random.default_rng(108)

    suppliers = [
        {
            "name": "Foxconn Precision Systems",
            "tier": "Tier-1",
            "origin": "Shenzhen",
            "lat": 22.5431,
            "lon": 114.0579,
            "port": "Shenzhen Port",
            "material": "Power Inverter IC"
        },
        {
            "name": "Klaus Micro-Pneumatics",
            "tier": "Tier-1",
            "origin": "Munich",
            "lat": 48.1351,
            "lon": 11.5820,
            "port": "Hamburg Gateway",
            "material": "Hydraulic Actuator"
        },
        {
            "name": "Tata AutoComp Modules",
            "tier": "Tier-1",
            "origin": "Pune",
            "lat": 18.5204,
            "lon": 73.8567,
            "port": "Nhava Sheva (JNPT)",
            "material": "EV Thermal Chassis"
        },
        {
            "name": "Kyoto Wafer & Sensor Corp",
            "tier": "Tier-2",
            "origin": "Kyoto",
            "lat": 35.0116,
            "lon": 135.7681,
            "port": "Kobe Maritime",
            "material": "LiDAR Optical Array"
        },
        {
            "name": "TSMC Fab-18 Foundry",
            "tier": "Tier-2",
            "origin": "Tainan",
            "lat": 23.1118,
            "lon": 120.2736,
            "port": "Kaohsiung Hub",
            "material": "5nm Logic Wafer"
        },
        {
            "name": "Antofagasta Lithium Refine",
            "tier": "Tier-3",
            "origin": "Santiago",
            "lat": -33.4489,
            "lon": -70.6693,
            "port": "Valparaiso Port",
            "material": "Battery Grade Li2CO3"
        },
        {
            "name": "Rotterdam Euro-Chem",
            "tier": "Tier-2",
            "origin": "Rotterdam",
            "lat": 51.9244,
            "lon": 4.4777,
            "port": "Port of Rotterdam",
            "material": "Dielectric Coolant"
        }
    ]

    rows = []

    for i in range(n):

        s = suppliers[rng.integers(0, len(suppliers))]

        order_value = int(rng.integers(55000, 520000))

        lead_time = int(rng.integers(14, 52))

        port_delay = float(rng.uniform(1.5, 9.8))

        geo_risk = float(rng.uniform(.3, 4.9))

        esg = int(rng.integers(68, 98))

        buffer = int(rng.integers(1, 13))

        risk = (
            port_delay * 3.9
            + geo_risk * 5.1
            + (100 - esg) * .4
            - buffer * 2.1
        )

        risk = float(np.clip(round(risk, 1), 5, 98.5))

        if risk > 68:
            status = "CRITICAL"
        elif risk > 42:
            status = "ELEVATED"
        else:
            status = "STABLE"

        delay = (
            int(round(risk / 6.2))
            if risk > 42
            else 0
        )

        rows.append({
            "PO_Number": f"SAP-PO-{202600+i}",
            "Supplier": s["name"],
            "Material": s["material"],
            "Supply_Tier": s["tier"],
            "Origin_City": s["origin"],
            "Origin_Lat": s["lat"],
            "Origin_Lon": s["lon"],
            "Gateway_Port": s["port"],
            "Dest_Lat": 18.9750,
            "Dest_Lon": 72.8258,
            "Order_Value_USD": order_value,
            "Planned_Lead_Time": lead_time,
            "Port_Bottleneck_Index": round(port_delay, 2),
            "Geopolitical_Risk": round(geo_risk, 2),
            "ESG_Compliance_Index": esg,
            "Inventory_Buffer_Days": buffer,
            "Disruption_Risk_Score": risk,
            "Status": status,
            "Predicted_Delay_Days": delay
        })

    return pd.DataFrame(rows)


# ============================================================
# CSV NORMALIZATION
# ============================================================

def normalize_csv(df):

    df = df.copy()

    aliases = {
        "po": "PO_Number",
        "ponumber": "PO_Number",
        "vendor": "Supplier",
        "supplier_name": "Supplier",
        "tier": "Supply_Tier",
        "port": "Gateway_Port",
        "order_value": "Order_Value_USD",
        "amount": "Order_Value_USD",
        "cost": "Order_Value_USD",
        "lead_time": "Planned_Lead_Time",
        "port_delay": "Port_Bottleneck_Index",
        "congestion": "Port_Bottleneck_Index",
        "geo_risk": "Geopolitical_Risk",
        "esg": "ESG_Compliance_Index",
        "buffer": "Inventory_Buffer_Days"
    }

    normalized = {
        str(c).lower().strip().replace(" ", "_"): c
        for c in df.columns
    }

    rename = {}

    for key, target in aliases.items():

        if key in normalized and target not in df.columns:
            rename[normalized[key]] = target

    df.rename(columns=rename, inplace=True)

    defaults = {
        "Supplier": "Global Supplier",
        "Material": "Industrial Material",
        "Supply_Tier": "Tier-1",
        "Origin_City": "Global Hub",
        "Gateway_Port": "Nhava Sheva (JNPT)",
        "Order_Value_USD": 135000,
        "Planned_Lead_Time": 28,
        "Port_Bottleneck_Index": 6.2,
        "Geopolitical_Risk": 2.5,
        "ESG_Compliance_Index": 82,
        "Inventory_Buffer_Days": 4
    }

    for col, default in defaults.items():

        if col not in df.columns:

            if col == "PO_Number":
                df[col] = [
                    f"CUSTOM-PO-{1000+i}"
                    for i in range(len(df))
                ]
            else:
                df[col] = default

    numeric = [
        "Order_Value_USD",
        "Planned_Lead_Time",
        "Port_Bottleneck_Index",
        "Geopolitical_Risk",
        "ESG_Compliance_Index",
        "Inventory_Buffer_Days"
    ]

    for col in numeric:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

        df[col] = df[col].fillna(
            defaults.get(col, 0)
        )

    return calculate_risk(df)


# ============================================================
# RISK ENGINE
# ============================================================

def calculate_risk(df):

    df = df.copy()

    risk = (
        df["Port_Bottleneck_Index"] * 3.9
        + df["Geopolitical_Risk"] * 5.1
        + (100 - df["ESG_Compliance_Index"]) * .4
        - df["Inventory_Buffer_Days"] * 2.1
    )

    df["Disruption_Risk_Score"] = np.clip(
        risk.round(1),
        0,
        100
    )

    df["Status"] = np.select(
        [
            df["Disruption_Risk_Score"] > 68,
            df["Disruption_Risk_Score"] > 42
        ],
        [
            "CRITICAL",
            "ELEVATED"
        ],
        default="STABLE"
    )

    df["Predicted_Delay_Days"] = np.where(
        df["Disruption_Risk_Score"] > 42,
        np.round(
            df["Disruption_Risk_Score"] / 6.2
        ),
        0
    ).astype(int)

    return df


# ============================================================
# COST ENGINE
# ============================================================

def calculate_costs(
    df,
    waiting_rate=0.004,
    holding_rate=0.00035,
    downtime_rate=0.012,
    air_rate=0.065,
    road_rate=0.028,
    expedite_rate=0.035
):

    df = df.copy()

    delay = df["Predicted_Delay_Days"]

    value = df["Order_Value_USD"]

    df["Waiting_Loss_USD"] = (
        value * delay * waiting_rate
    )

    df["Inventory_Holding_USD"] = (
        value * delay * holding_rate
    )

    df["Production_Downtime_USD"] = (
        value * delay * downtime_rate
    )

    df["Air_Recovery_Cost_USD"] = (
        value * air_rate
    )

    df["Road_Recovery_Cost_USD"] = (
        value * road_rate
    )

    df["Expedite_Premium_USD"] = (
        value * expedite_rate
    )

    df["Value_at_Risk_USD"] = (
        df["Waiting_Loss_USD"]
        + df["Inventory_Holding_USD"]
        + df["Production_Downtime_USD"]
    )

    df["Road_Recovery_Total_USD"] = (
        df["Road_Recovery_Cost_USD"]
        + df["Expedite_Premium_USD"]
    )

    df["Best_Recovery_Cost_USD"] = np.minimum(
        df["Air_Recovery_Cost_USD"],
        df["Road_Recovery_Total_USD"]
    )

    df["Potential_Savings_USD"] = np.maximum(
        df["Value_at_Risk_USD"]
        - df["Best_Recovery_Cost_USD"],
        0
    )

    return df


# ============================================================
# FORMATTING
# ============================================================

def money(value):
    return f"${value:,.0f}"


def badge(status):

    if status == "CRITICAL":
        return '<span class="status danger">CRITICAL</span>'

    if status == "ELEVATED":
        return '<span class="status warning">ELEVATED</span>'

    return '<span class="status safe">STABLE</span>'


# ============================================================
# LOAD DATA
# ============================================================

if "master_df" not in st.session_state:

    st.session_state.master_df = generate_data()

df = st.session_state.master_df.copy()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🛡️ CostShield V2")

    st.caption(
        "Enterprise Cost & Supply Resilience OS"
    )

    st.divider()

    data_mode = st.radio(
        "Data Source",
        [
            "Demo ERP Dataset",
            "Upload Custom CSV"
        ]
    )

    if data_mode == "Upload Custom CSV":

        uploaded = st.file_uploader(
            "Upload ERP / SAP CSV",
            type=["csv"]
        )

        if uploaded:

            try:

                uploaded_df = pd.read_csv(uploaded)

                df = normalize_csv(
                    uploaded_df
                )

                st.session_state.master_df = df

                st.success(
                    f"{len(df):,} records loaded"
                )

            except Exception as e:

                st.error(
                    f"Import failed: {e}"
                )

    else:

        df = generate_data()

    st.divider()

    tier_filter = st.multiselect(
        "Supply Tier",
        sorted(
            df["Supply_Tier"].unique()
        ),
        default=sorted(
            df["Supply_Tier"].unique()
        )
    )

    if tier_filter:

        df = df[
            df["Supply_Tier"].isin(
                tier_filter
            )
        ].copy()

    st.divider()

    page = st.radio(
        "CONTROL CENTER",
        [
            "🏠 Executive Dashboard",
            "🌐 Global Control Tower",
            "📦 Purchase Orders",
            "🚢 Shipment Control",
            "💰 Cost Intelligence",
            "⚠️ Risk & Exceptions",
            "🧪 Scenario Simulator",
            "🤖 AI Copilot",
            "🏭 Supplier 360°",
            "📊 Analytics & ML",
            "📑 Reports",
            "🔌 SAP Integration",
            "🔐 Admin & Audit"
        ]
    )

    st.divider()

    st.markdown(
        '<span class="status info">'
        'DEMO / SAFE MODE'
        '</span>',
        unsafe_allow_html=True
    )

    st.caption(
        "Real SAP connectivity requires configured credentials."
    )


# ============================================================
# COST CALCULATION
# ============================================================

df = calculate_costs(df)


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero">

<div class="hero-title">
🛡️ SAP CostShield V2
</div>

<div class="hero-sub">
Autonomous Cost Intelligence • Supply Risk • Recovery Optimization • Scenario Analytics
</div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# EXECUTIVE DASHBOARD
# ============================================================

if page == "🏠 Executive Dashboard":

    total_value = df["Order_Value_USD"].sum()

    total_var = df["Value_at_Risk_USD"].sum()

    savings = df["Potential_Savings_USD"].sum()

    critical = (
        df["Status"] == "CRITICAL"
    ).sum()

    avg_risk = df[
        "Disruption_Risk_Score"
    ].mean()

    delayed = (
        df["Predicted_Delay_Days"] > 0
    ).mean()

    otif = max(
        0,
        100 - delayed * 100
    )

    cols = st.columns(6)

    cards = [
        ("TOTAL PO VALUE", money(total_value)),
        ("VALUE AT RISK", money(total_var)),
        ("POTENTIAL SAVINGS", money(savings)),
        ("CRITICAL POs", f"{critical:,}"),
        ("OTIF RELIABILITY", f"{otif:.1f}%"),
        ("AVG RISK", f"{avg_risk:.1f}/100")
    ]

    for col, (label, value) in zip(
        cols,
        cards
    ):

        col.markdown(
            f"""
            <div class="kpi">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="section">Enterprise Risk Overview</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:

        status = (
            df["Status"]
            .value_counts()
            .reset_index()
        )

        status.columns = [
            "Status",
            "Count"
        ]

        fig = px.pie(
            status,
            names="Status",
            values="Count",
            hole=.55,
            title="Risk Status Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with c2:

        ports = (
            df.groupby(
                "Gateway_Port"
            )["Value_at_Risk_USD"]
            .sum()
            .reset_index()
            .sort_values(
                "Value_at_Risk_USD",
                ascending=False
            )
            .head(10)
        )

        fig = px.bar(
            ports,
            x="Value_at_Risk_USD",
            y="Gateway_Port",
            orientation="h",
            title="Top Gateway VaR Exposure"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.markdown(
        '<div class="section">Top Exceptions</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        df.sort_values(
            "Disruption_Risk_Score",
            ascending=False
        ).head(15),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# GLOBAL CONTROL TOWER
# ============================================================

elif page == "🌐 Global Control Tower":

    st.markdown(
        '<div class="section">🌐 Global Supply Network</div>',
        unsafe_allow_html=True
    )

    fig = go.Figure()

    # Supplier nodes

    for supplier, group in df.groupby(
        "Supplier"
    ):

        row = group.iloc[0]

        fig.add_trace(
            go.Scattergeo(
                lon=[row["Origin_Lon"]],
                lat=[row["Origin_Lat"]],
                text=[
                    f"{supplier}<br>"
                    f"Risk: {group['Disruption_Risk_Score'].mean():.1f}"
                ],
                mode="markers",
                marker=dict(
                    size=10
                ),
                name=supplier
            )
        )

        # route to Mumbai

        fig.add_trace(
            go.Scattergeo(
                lon=[
                    row["Origin_Lon"],
                    row["Dest_Lon"]
                ],
                lat=[
                    row["Origin_Lat"],
                    row["Dest_Lat"]
                ],
                mode="lines",
                line=dict(
                    width=1
                ),
                showlegend=False
            )
        )

    fig.update_geos(
        projection_type="orthographic",
        showland=True,
        showcountries=True
    )

    fig.update_layout(
        height=620,
        title="Global Supplier → India Network"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown(
        '<div class="section">Gateway Choke Points</div>',
        unsafe_allow_html=True
    )

    gateway = (
        df.groupby("Gateway_Port")
        .agg(
            POs=("PO_Number", "count"),
            Avg_Risk=("Disruption_Risk_Score", "mean"),
            VaR=("Value_at_Risk_USD", "sum")
        )
        .reset_index()
        .sort_values(
            "VaR",
            ascending=False
        )
    )

    st.dataframe(
        gateway,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PURCHASE ORDERS
# ============================================================

elif page == "📦 Purchase Orders":

    st.subheader(
        "📦 Purchase Order Command Center"
    )

    search = st.text_input(
        "Search PO / Supplier / Material"
    )

    status_filter = st.multiselect(
        "Status",
        sorted(df["Status"].unique()),
        default=sorted(df["Status"].unique())
    )

    view = df[
        df["Status"].isin(
            status_filter
        )
    ].copy()

    if search:

        mask = (
            view.astype(str)
            .apply(
                lambda c:
                c.str.contains(
                    search,
                    case=False,
                    na=False
                )
            )
            .any(axis=1)
        )

        view = view[mask]

    st.dataframe(
        view.sort_values(
            "Disruption_Risk_Score",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# SHIPMENT CONTROL
# ============================================================

elif page == "🚢 Shipment Control":

    st.subheader(
        "🚢 Shipment Control Tower"
    )

    route = (
        df.groupby(
            ["Origin_City", "Gateway_Port"]
        )
        .agg(
            POs=("PO_Number", "count"),
            Avg_Risk=("Disruption_Risk_Score", "mean"),
            Avg_Delay=("Predicted_Delay_Days", "mean")
        )
        .reset_index()
    )

    fig = px.scatter(
        route,
        x="Avg_Delay",
        y="Avg_Risk",
        size="POs",
        color="Avg_Risk",
        hover_name="Gateway_Port",
        title="Route Risk vs Predicted Delay"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        route.sort_values(
            "Avg_Risk",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# COST INTELLIGENCE
# ============================================================

elif page == "💰 Cost Intelligence":

    st.subheader(
        "💰 Cost Intelligence Engine"
    )

    cols = st.columns(5)

    metrics = [
        (
            "Waiting Loss",
            df["Waiting_Loss_USD"].sum()
        ),
        (
            "Downtime",
            df["Production_Downtime_USD"].sum()
        ),
        (
            "Inventory Holding",
            df["Inventory_Holding_USD"].sum()
        ),
        (
            "Recovery Cost",
            df["Best_Recovery_Cost_USD"].sum()
        ),
        (
            "Potential Savings",
            df["Potential_Savings_USD"].sum()
        )
    ]

    for col, (label, value) in zip(
        cols,
        metrics
    ):

        col.metric(
            label,
            money(value)
        )

    components = pd.DataFrame({
        "Component": [
            "Waiting Loss",
            "Inventory Holding",
            "Production Downtime",
            "Best Recovery"
        ],
        "USD": [
            df["Waiting_Loss_USD"].sum(),
            df["Inventory_Holding_USD"].sum(),
            df["Production_Downtime_USD"].sum(),
            df["Best_Recovery_Cost_USD"].sum()
        ]
    })

    fig = px.bar(
        components,
        x="Component",
        y="USD",
        title="Enterprise Cost Exposure"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        df.sort_values(
            "Potential_Savings_USD",
            ascending=False
        ).head(25),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# RISK & EXCEPTIONS
# ============================================================

elif page == "⚠️ Risk & Exceptions":

    st.subheader(
        "⚠️ Risk & Exception Management"
    )

    critical = df[
        df["Status"] == "CRITICAL"
    ].copy()

    st.error(
        f"{len(critical)} critical purchase orders detected."
    )

    st.dataframe(
        critical[
            [
                "PO_Number",
                "Supplier",
                "Gateway_Port",
                "Disruption_Risk_Score",
                "Predicted_Delay_Days",
                "Value_at_Risk_USD",
                "Potential_Savings_USD"
            ]
        ].sort_values(
            "Disruption_Risk_Score",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# SCENARIO SIMULATOR
# ============================================================

elif page == "🧪 Scenario Simulator":

    st.subheader(
        "🧪 Supply Chain Stress Simulator"
    )

    c1, c2, c3 = st.columns(3)

    port_shock = c1.slider(
        "Port Congestion Shock %",
        0,
        100,
        25
    )

    buffer_injection = c2.slider(
        "Emergency Buffer Days",
        0,
        14,
        2
    )

    freight_premium = c3.slider(
        "Air Freight Premium %",
        0,
        30,
        0
    )

    scenario = df.copy()

    scenario["Port_Bottleneck_Index"] = (
        scenario["Port_Bottleneck_Index"]
        * (1 + port_shock / 100)
    ).clip(0, 10)

    scenario["Inventory_Buffer_Days"] += (
        buffer_injection
    )

    scenario["Predicted_Delay_Days"] = (
        scenario["Predicted_Delay_Days"]
        * (1 + port_shock / 100)
        - buffer_injection * .7
    ).clip(lower=0).round().astype(int)

    scenario = calculate_costs(
        scenario,
        air_rate=.065 + freight_premium / 100
    )

    baseline_var = df[
        "Value_at_Risk_USD"
    ].sum()

    scenario_var = scenario[
        "Value_at_Risk_USD"
    ].sum()

    baseline_recovery = df[
        "Best_Recovery_Cost_USD"
    ].sum()

    scenario_recovery = scenario[
        "Best_Recovery_Cost_USD"
    ].sum()

    a, b, c, d = st.columns(4)

    a.metric(
        "Baseline VaR",
        money(baseline_var)
    )

    b.metric(
        "Scenario VaR",
        money(scenario_var),
        delta=money(
            scenario_var - baseline_var
        )
    )

    c.metric(
        "Baseline Recovery",
        money(baseline_recovery)
    )

    d.metric(
        "Scenario Recovery",
        money(scenario_recovery)
    )

    comparison = pd.DataFrame({
        "Metric": [
            "Value at Risk",
            "Recovery Cost"
        ],
        "Baseline": [
            baseline_var,
            baseline_recovery
        ],
        "Scenario": [
            scenario_var,
            scenario_recovery
        ]
    })

    fig = px.bar(
        comparison,
        x="Metric",
        y=[
            "Baseline",
            "Scenario"
        ],
        barmode="group",
        title="Baseline vs Stress Scenario"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# AI COPILOT
# ============================================================

elif page == "🤖 AI Copilot":

    st.subheader(
        "🤖 CostShield AI Copilot"
    )

    st.caption(
        "Local analytical copilot — no fake SAP Joule response."
    )

    selected_po = st.selectbox(
        "Select Purchase Order",
        df["PO_Number"].tolist()
    )

    row = df[
        df["PO_Number"] == selected_po
    ].iloc[0]

    st.markdown(
        f"""
        **Supplier:** {row.Supplier}

        **Material:** {row.Material}

        **Risk:** {row.Disruption_Risk_Score:.1f}/100

        **Predicted Delay:** {row.Predicted_Delay_Days} days

        **VaR:** {money(row.Value_at_Risk_USD)}
        """
    )

    value = row["Order_Value_USD"]

    actions = pd.DataFrame({
        "Action": [
            "Monitor",
            "Road + Expedite",
            "Air Expedite"
        ],
        "Recovery Cost": [
            0,
            value * (.028 + .035),
            value * .065
        ]
    })

    actions["Net Benefit"] = (
        row["Value_at_Risk_USD"]
        - actions["Recovery Cost"]
    )

    actions["ROI %"] = np.where(
        actions["Recovery Cost"] > 0,
        actions["Net Benefit"]
        / actions["Recovery Cost"]
        * 100,
        0
    )

    st.dataframe(
        actions,
        use_container_width=True,
        hide_index=True
    )

    best = actions.sort_values(
        "Net Benefit",
        ascending=False
    ).iloc[0]

    st.success(
        f"Recommended action: {best['Action']} | "
        f"Expected net benefit: {money(best['Net Benefit'])}"
    )

    if st.button(
        "⚡ EXECUTE MITIGATION — DEMO",
        type="primary"
    ):

        st.session_state.mitigated_pos.add(
            selected_po
        )

        st.session_state.audit_log.append({
            "Timestamp": datetime.now().isoformat(),
            "PO": selected_po,
            "Action": best["Action"],
            "Net_Benefit_USD": float(
                best["Net Benefit"]
            )
        })

        st.success(
            "Mitigation recorded in local audit log."
        )

    st.markdown("### Ask CostShield")

    question = st.text_input(
        "Example: Which supplier has highest risk?"
    )

    if question:

        q = question.lower()

        if "supplier" in q:

            supplier = (
                df.groupby("Supplier")
                ["Disruption_Risk_Score"]
                .mean()
                .sort_values(
                    ascending=False
                )
                .index[0]
            )

            st.info(
                f"Highest average-risk supplier: {supplier}"
            )

        elif "port" in q:

            port = (
                df.groupby("Gateway_Port")
                ["Value_at_Risk_USD"]
                .sum()
                .sort_values(
                    ascending=False
                )
                .index[0]
            )

            st.info(
                f"Highest VaR gateway: {port}"
            )

        elif "saving" in q:

            st.info(
                f"Potential modeled savings: "
                f"{money(df['Potential_Savings_USD'].sum())}"
            )

        elif "critical" in q:

            st.info(
                f"Critical POs: "
                f"{(df['Status']=='CRITICAL').sum()}"
            )

        else:

            st.info(
                "I can analyze suppliers, ports, "
                "critical POs, risk and savings."
            )


# ============================================================
# SUPPLIER 360
# ============================================================

elif page == "🏭 Supplier 360°":

    st.subheader(
        "🏭 Supplier 360° Intelligence"
    )

    supplier = (
        df.groupby(
            ["Supplier", "Supply_Tier"]
        )
        .agg(
            POs=("PO_Number", "count"),
            PO_Value=("Order_Value_USD", "sum"),
            Avg_Risk=(
                "Disruption_Risk_Score",
                "mean"
            ),
            VaR=(
                "Value_at_Risk_USD",
                "sum"
            ),
            Potential_Savings=(
                "Potential_Savings_USD",
                "sum"
            )
        )
        .reset_index()
    )

    fig = px.scatter(
        supplier,
        x="Avg_Risk",
        y="VaR",
        size="POs",
        color="Supply_Tier",
        hover_name="Supplier",
        title="Supplier Risk vs Financial Exposure"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        supplier.sort_values(
            "Avg_Risk",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# ANALYTICS + ML
# ============================================================

elif page == "📊 Analytics & ML":

    st.subheader(
        "📊 Analytics & Explainable ML"
    )

    c1, c2 = st.columns(2)

    with c1:

        fig = px.histogram(
            df,
            x="Disruption_Risk_Score",
            nbins=20,
            title="Risk Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with c2:

        fig = px.scatter(
            df,
            x="Port_Bottleneck_Index",
            y="Disruption_Risk_Score",
            color="Status",
            size="Order_Value_USD",
            title="Port Congestion vs Risk"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.markdown(
        "### Risk Driver Importance"
    )

    importance = pd.DataFrame({
        "Driver": [
            "Port Bottleneck",
            "Geopolitical Risk",
            "ESG",
            "Inventory Buffer"
        ],
        "Impact": [
            3.9,
            5.1,
            .4,
            2.1
        ]
    })

    fig = px.bar(
        importance,
        x="Impact",
        y="Driver",
        orientation="h",
        title="Transparent Risk Formula Weights"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# REPORTS
# ============================================================

elif page == "📑 Reports":

    st.subheader(
        "📑 Enterprise Reports"
    )

    report = df.copy()

    csv = report.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Download Complete Risk Report",
        csv,
        "SAP_CostShield_V2_Risk_Report.csv",
        "text/csv"
    )

    summary = {
        "Generated": datetime.now().isoformat(),
        "PO Count": len(df),
        "PO Value USD": float(
            df["Order_Value_USD"].sum()
        ),
        "Value at Risk USD": float(
            df["Value_at_Risk_USD"].sum()
        ),
        "Potential Savings USD": float(
            df["Potential_Savings_USD"].sum()
        ),
        "Critical POs": int(
            (df["Status"] == "CRITICAL").sum()
        )
    }

    st.json(summary)


# ============================================================
# SAP INTEGRATION
# ============================================================

elif page == "🔌 SAP Integration":

    st.subheader(
        "🔌 SAP Integration Center"
    )

    st.warning(
        "SAFE MODE: SAP connection is not claimed as LIVE."
    )

    st.markdown("""
### Supported integration architecture

**SAP S/4HANA**
→ OData/API Layer  
→ CostShield Integration Layer  
→ Risk Engine  
→ Cost Engine  
→ Recommendation Engine  
→ Control Tower
""")

    st.markdown("### Environment configuration")

    sap_url = st.text_input(
        "SAP Base URL",
        type="default"
    )

    sap_token = st.text_input(
        "SAP Access Token",
        type="password"
    )

    if st.button(
        "Test SAP Configuration"
    ):

        if sap_url and sap_token:

            st.success(
                "Configuration fields received. "
                "Implement authorized endpoint validation before production use."
            )

        else:

            st.error(
                "SAP Base URL and token are required."
            )


# ============================================================
# ADMIN & AUDIT
# ============================================================

elif page == "🔐 Admin & Audit":

    st.subheader(
        "🔐 Administration & Audit"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Active Records",
        len(df)
    )

    c2.metric(
        "Mitigated POs",
        len(st.session_state.mitigated_pos)
    )

    c3.metric(
        "Audit Events",
        len(st.session_state.audit_log)
    )

    st.markdown(
        "### Risk Thresholds"
    )

    col1, col2 = st.columns(2)

    critical_threshold = col1.number_input(
        "Critical Risk Threshold",
        min_value=1,
        max_value=100,
        value=68
    )

    elevated_threshold = col2.number_input(
        "Elevated Risk Threshold",
        min_value=1,
        max_value=100,
        value=42
    )

    st.markdown(
        "### Audit Log"
    )

    if st.session_state.audit_log:

        st.dataframe(
            pd.DataFrame(
                st.session_state.audit_log
            ),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No mitigation events recorded."
        )

    st.markdown(
        "### System State"
    )

    st.json({
        "Application": "SAP CostShield V2",
        "Mode": "Demo / Safe",
        "SAP_Connection": "Not configured",
        "Critical_Threshold": critical_threshold,
        "Elevated_Threshold": elevated_threshold,
        "Records": len(df)
    })


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "SAP CostShield V2 PRO • "
    "Cost Intelligence + Risk Analytics + Scenario Optimization • "
    "Demo-safe architecture"
)