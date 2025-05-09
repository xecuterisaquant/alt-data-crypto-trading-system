import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Strategy Dashboard", layout="wide")

# Load data
btc_df = pd.read_csv("Model Output/BTC_Strategy_Output.csv", parse_dates=['Datetime'])
eth_df = pd.read_csv("Model Output/ETH_Strategy_Output.csv", parse_dates=['Datetime'])

# Clean and sort
for df in [btc_df, eth_df]:
    df.sort_values("Datetime", inplace=True)
    df.drop_duplicates(subset="Datetime", inplace=True)
    df['Price'] = df['Price'].fillna(method='ffill')
    df['Portfolio_Value'] = df['Portfolio_Value'].fillna(method='ffill')
    df['Portfolio_Value'] = df['Portfolio_Value'].fillna(method='bfill')

# Sidebar
st.sidebar.header("⚙️ Dashboard Controls")
asset = st.sidebar.selectbox("Select Asset", ['BTC', 'ETH'])
show_drawdown = st.sidebar.checkbox("Show Drawdown Curve", value=True)

# Use selected asset
df = btc_df if asset == 'BTC' else eth_df
df['Position'] = df['Position'].fillna(0)
buy_hold = 100000 * (df['Price'] / df['Price'].iloc[0])

# ========================
# 📌 SECTION 1: STRATEGY CHART
# ========================
st.header(f"📈 {asset} Strategy Performance")

entry_long = df[(df['Position'].shift(1) == 0) & (df['Position'] == 1)]
entry_short = df[(df['Position'].shift(1) == 0) & (df['Position'] == -1)]
exit_long = df[(df['Position'].shift(1) == 1) & (df['Position'] == 0)]
exit_short = df[(df['Position'].shift(1) == -1) & (df['Position'] == 0)]

fig1 = go.Figure()

fig1.add_trace(go.Scatter(x=df['Datetime'], y=df['Price'], mode='lines', name='Price', line=dict(color='gray')))

fig1.add_trace(go.Scatter(
    x=entry_long['Datetime'], y=entry_long['Price'], mode='markers',
    name='Entry (Long)', marker=dict(color='green', symbol='triangle-up', size=10),
    hovertemplate='Entry (Long)<br>%{x}<br>$%{y:.2f}'
))
fig1.add_trace(go.Scatter(
    x=entry_short['Datetime'], y=entry_short['Price'], mode='markers',
    name='Entry (Short)', marker=dict(color='purple', symbol='triangle-down', size=10),
    hovertemplate='Entry (Short)<br>%{x}<br>$%{y:.2f}'
))
fig1.add_trace(go.Scatter(
    x=exit_long['Datetime'], y=exit_long['Price'], mode='markers',
    name='Exit (Long)', marker=dict(color='orange', symbol='x', size=10),
    hovertemplate='Exit (Long)<br>%{x}<br>$%{y:.2f}'
))
fig1.add_trace(go.Scatter(
    x=exit_short['Datetime'], y=exit_short['Price'], mode='markers',
    name='Exit (Short)', marker=dict(color='red', symbol='x', size=10),
    hovertemplate='Exit (Short)<br>%{x}<br>$%{y:.2f}'
))

if show_drawdown:
    drawdown = (df['Portfolio_Value'] / df['Portfolio_Value'].cummax()) - 1
    fig1.add_trace(go.Scatter(
        x=df['Datetime'], y=drawdown, mode='lines', name='Drawdown',
        line=dict(color='orange', dash='dot'), yaxis='y2'
    ))
    fig1.update_layout(yaxis2=dict(
        title="Drawdown", overlaying='y', side='right', showgrid=False, range=[-1, 0]
    ))

fig1.update_layout(title=f"{asset} Price with Entry/Exit Signals", xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig1, use_container_width=True)

# ========================
# 📌 SECTION 2: STRATEGY VS BUY & HOLD
# ========================
st.header("📊 Strategy vs Buy & Hold")

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df['Datetime'], y=df['Portfolio_Value'], mode='lines', name='Strategy'))
fig2.add_trace(go.Scatter(x=df['Datetime'], y=buy_hold, mode='lines', name='Buy & Hold', line=dict(dash='dot')))
fig2.update_layout(title=f"{asset} Portfolio Value vs Buy & Hold", xaxis_title="Date", yaxis_title="Portfolio Value ($)")
st.plotly_chart(fig2, use_container_width=True)

final_val = df['Portfolio_Value'].iloc[-1]
buy_hold_val = buy_hold.iloc[-1]
sharpe = df['Daily_Return'].mean() / df['Daily_Return'].std() * (252**0.5)
max_dd = ((df['Portfolio_Value'] / df['Portfolio_Value'].cummax()) - 1).min()

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Final Value", f"${final_val:,.2f}")
col2.metric("📊 Buy & Hold", f"${buy_hold_val:,.2f}")
col3.metric("⚖️ Sharpe", f"{sharpe:.2f}")
col4.metric("📉 Max Drawdown", f"{max_dd*100:.2f}%")

# ========================
# 📌 SECTION 3: BTC vs ETH Strategy Comparison
# ========================
st.header("📈 BTC vs ETH Strategy Comparison")

fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=btc_df['Datetime'], y=btc_df['Portfolio_Value'], name='BTC Strategy'))
fig3.add_trace(go.Scatter(x=eth_df['Datetime'], y=eth_df['Portfolio_Value'], name='ETH Strategy'))
fig3.update_layout(title="BTC vs ETH Strategy Comparison", xaxis_title="Date", yaxis_title="Portfolio Value ($)")
st.plotly_chart(fig3, use_container_width=True)
