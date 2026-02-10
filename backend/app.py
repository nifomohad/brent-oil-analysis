from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from pathlib import Path
import json

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"

# Load Brent prices
df = pd.read_csv(DATA_DIR / "BrentOilPrices.csv")
df['Date'] = pd.to_datetime(df['Date'].astype(str).str.strip('"'), format='%d-%b-%y', errors='coerce', dayfirst=True)
mask = df['Date'].isna()
if mask.any():
    df.loc[mask, 'Date'] = pd.to_datetime(df.loc[mask, 'Date'].astype(str).str.strip('"'), format='%b %d, %Y', errors='coerce')
df = df.dropna(subset=['Date']).sort_values('Date').set_index('Date')
df['log_return'] = np.log(df['Price']).diff()
df['rolling_vol_30d'] = df['log_return'].rolling(30).std() * np.sqrt(252)

events = pd.read_csv(DATA_DIR / "events.csv", parse_dates=['Date'])

# Load change_points.json from Task 2
cp_path = ROOT / "change_points.json"
change_points = []
if cp_path.exists():
    with open(cp_path, 'r') as f:
        change_points = json.load(f)

@app.route('/api/prices')
def get_prices():
    start = request.args.get('start')
    end = request.args.get('end')
    df_slice = df.copy()
    if start: df_slice = df_slice[df_slice.index >= start]
    if end: df_slice = df_slice[df_slice.index <= end]
    return jsonify({
        "dates": df_slice.index.strftime('%Y-%m-%d').tolist(),
        "prices": df_slice['Price'].round(2).tolist(),
        "volatility": df_slice['rolling_vol_30d'].round(4).fillna(0).tolist()
    })

@app.route('/api/events')
def get_events():
    return jsonify(events.to_dict(orient='records'))

@app.route('/api/change_points')
def get_change_points():
    return jsonify(change_points)

@app.route('/')
def home():
    return jsonify({
        "status": "Backend is running",
        "message": "Use the API endpoints: /api/prices, /api/events, /api/change_points",
        "loaded": {
            "prices": len(df),
            "events": len(events),
            "change_points": len(change_points)
        }
    })


if __name__ == '__main__':
    print(f"Starting Flask on http://127.0.0.1:5000")
    print(f"Loaded {len(df)} prices, {len(events)} events, {len(change_points)} change points")
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print("Backend failed to start:", str(e))