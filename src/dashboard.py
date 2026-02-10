import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import json
from pathlib import Path

# Paths
ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
CHANGE_POINTS_FILE = ROOT / "change_points.json"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_DIR / "BrentOilPrices.csv")
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date']).sort_values('Date').set_index('Date')
    df['log_return'] = np.log(df['Price']).diff()
    df['volatility'] = df['log_return'].rolling(30).std() * np.sqrt(252)
    return df

@st.cache_data
def load_events():
    return pd.read_csv(DATA_DIR / "events.csv", parse_dates=['Date'])

@st.cache_data
def load_change_points():
    if CHANGE_POINTS_FILE.exists():
        with open(CHANGE_POINTS_FILE, 'r') as f:
            return json.load(f)
    return []

df = load_data()
events = load_events()
change_points = load_change_points()

# Sidebar
st.sidebar.header("Dashboard Controls")

min_date = df.index.min().date()
max_date = df.index.max().date()
start_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

event_options = ["None"] + events['Event Description'].tolist()
selected_event = st.sidebar.selectbox("Highlight Event", event_options)

show_volatility = st.sidebar.checkbox("Show Volatility Overlay", value=True)

# Filter data
filtered_df = df.loc[start_date:end_date]

# Title
st.title("Brent Oil Prices & Geopolitical Events Dashboard")
st.markdown("Explore historical Brent crude prices, volatility, detected regime shifts, and event impacts.")

# Plotly Chart
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=filtered_df.index,
        y=filtered_df['Price'],
        mode='lines',
        name='Price (USD/barrel)',
        line=dict(color='royalblue', width=2)
    )
)

if show_volatility:
    fig.add_trace(
        go.Scatter(
            x=filtered_df.index,
            y=filtered_df['volatility'],
            mode='lines',
            name='Annualized Volatility (30-day rolling)',
            line=dict(color='red', width=2, dash='dot'),
            yaxis='y2'
        )
    )

# Events
for _, row in events.iterrows():
    if start_date <= row['Date'].date() <= end_date:
        fig.add_vline(
            x=row['Date'],
            line_dash="dash",
            line_color="gray",
            annotation_text=row['Event Description'][:25] + "...",
            annotation_position="top right",
            annotation_font_size=10,
            annotation_font_color="gray"
        )

# Change points
for cp in change_points:
    cp_date = pd.to_datetime(cp['date'])
    if start_date <= cp_date.date() <= end_date:
        fig.add_vline(
            x=cp_date,
            line_dash="dot",
            line_color="purple",
            annotation_text=cp['description'][:25] + "...",
            annotation_position="top left",
            annotation_font_size=10,
            annotation_font_color="purple"
        )

# Highlight selected event
if selected_event != "None":
    event_row = events[events['Event Description'] == selected_event].iloc[0]
    ev_date = event_row['Date']
    pre = ev_date - pd.Timedelta(days=30)
    post = ev_date + pd.Timedelta(days=30)

    fig.add_vrect(
        x0=pre,
        x1=post,
        fillcolor="red",
        opacity=0.1,
        line_width=0,
        layer="below"
    )

fig.update_layout(
    title="Brent Crude Oil Price & Volatility",
    xaxis_title="Date",
    yaxis_title="Price (USD/barrel)",
    yaxis2=dict(title="Volatility", overlaying="y", side="right") if show_volatility else None,
    hovermode="x unified",
    height=600,
    template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# Event Impact Metrics
if selected_event != "None":
    st.subheader(f"Impact Analysis: {selected_event}")

    ev_date = event_row['Date']
    window = 30

    pre_period = filtered_df.loc[:ev_date].tail(window)
    post_period = filtered_df.loc[ev_date:].head(window)

    if not pre_period.empty and not post_period.empty:
        pre_avg = pre_period['Price'].mean()
        post_avg = post_period['Price'].mean()
        pct_change = ((post_avg - pre_avg) / pre_avg * 100)

        col1, col2, col3 = st.columns(3)
        col1.metric("Avg Price (30 days before)", f"${pre_avg:.2f}")
        col2.metric("Avg Price (30 days after)", f"${post_avg:.2f}")
        col3.metric("Change", f"{pct_change:+.1f}%", delta_color="normal")
    else:
        st.info("Not enough data in selected range for impact calculation.")
else:
    st.info("Select an event from the sidebar to see impact metrics.")