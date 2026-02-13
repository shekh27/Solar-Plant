
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Solar Command Center", layout="wide")
st.title("☀️ Solar Operations Command Center")

@st.cache_data
def load_and_prep():
    gen = pd.read_csv('Plant_1_Generation_Data.csv')
    weather = pd.read_csv('Plant_1_Weather_Sensor_Data.csv')
    gen['DATE_TIME'] = pd.to_datetime(gen['DATE_TIME'])
    weather['DATE_TIME'] = pd.to_datetime(weather['DATE_TIME'])
    df = pd.merge(gen, weather, on='DATE_TIME', how='inner')
    df['DATE'] = df['DATE_TIME'].dt.date
    daily = df.groupby('DATE').agg({'DC_POWER':'mean', 'AC_POWER':'mean', 'DAILY_YIELD':'max'}).reset_index()
    hourly = df.groupby(df['DATE_TIME'].dt.hour).agg({'DC_POWER':'mean', 'AC_POWER':'mean'}).reset_index()
    return df, daily, hourly

df_plant1, daily_plant1, hourly_plant1 = load_and_prep()

# KPI CARDS
total_mwh = daily_plant1['DAILY_YIELD'].sum() / 1000
peak_power = df_plant1['DC_POWER'].max()
avg_energy = daily_plant1['DAILY_YIELD'].mean()

k1, k2, k3 = st.columns(3)
k1.metric("Total Plant Production", f"{total_mwh:.1f} MWh", delta="-1%")
k2.metric("Average Daily Energy", f"{avg_energy:.0f} kWh")
k3.metric("Peak DC Power", f"{peak_power:.1f} kW")

# THE MASTER GRAPH WITH AXIS LABELS
fig = go.Figure()
fig.add_trace(go.Scatter(x=hourly_plant1.index, y=hourly_plant1['DC_POWER'], name='Hourly DC', line=dict(color='#1f77b4')))
fig.add_trace(go.Scatter(x=hourly_plant1.index, y=hourly_plant1['AC_POWER'], name='Hourly AC', line=dict(color='orange')))
fig.add_trace(go.Scatter(x=daily_plant1['DATE'], y=daily_plant1['DC_POWER'], name='Daily DC', line=dict(color='#d62728', width=3), visible=False))
fig.add_trace(go.Scatter(x=daily_plant1['DATE'], y=daily_plant1['AC_POWER'], name='Daily AC', line=dict(color='yellow', width=3), visible=False))
fig.add_trace(go.Scatter(x=df_plant1['DATE_TIME'], y=df_plant1['DC_POWER'], name='Raw 15-Min DC', line=dict(color='#2ca02c', width=1), visible=False))

fig.update_layout(
    template="plotly_dark",
    hovermode="x unified",
    xaxis_title="Timeline",      # Global X Label
    yaxis_title="Power (kW)",    # Global Y Label
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    updatemenus=[dict(type="buttons", direction="down", x=1.1, y=0.9,
            buttons=list([
                dict(label="Hourly Overview", method="update", args=[{"visible": [True, True, False, False, False]}, {"xaxis": {"title": "Hour Index"}}]),
                dict(label="Daily Performance", method="update", args=[{"visible": [False, False, True, True, False]}, {"xaxis": {"title": "Date"}}]),
                dict(label="High-Res (Forensic)", method="update", args=[{"visible": [False, False, False, False, True]}, {"xaxis": {"title": "Full Timeline"}}])
            ]))])

st.plotly_chart(fig, use_container_width=True)
