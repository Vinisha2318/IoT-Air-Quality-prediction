import requests
import pandas as pd
import time
import warnings
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime
warnings.filterwarnings("ignore")

# ======================
# CONFIGURATION
# ======================
READ_API_KEY = "JUR7KMA0KI8GO6IC"
WRITE_API_KEY = "OT2YATM8H0R4STMZ"
CHANNEL_ID = "3330006"

READ_URL = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}&results=100"
WRITE_URL = "https://api.thingspeak.com/update"

print(" AQI Prediction System Started...\n")

# ======================
# STEP 1: FETCH DATA
# ======================
def get_data():
    response = requests.get(READ_URL)
    data = response.json()

    records = []

    for entry in data['feeds']:
        try:
            temp = float(entry['field1'])
            humidity = float(entry['field2'])
            gas = float(entry['field3'])
            aqi = float(entry['field4'])

            timestamp = entry['created_at']  # ✅ timestamp added

            records.append([temp, humidity, gas, aqi, timestamp])
        except:
            continue

    df = pd.DataFrame(records, columns=['temp', 'humidity', 'gas', 'aqi', 'time'])
    return df

# ======================
# STEP 2: TRAIN MODEL
# ======================
df = get_data()

if len(df) < 10:
    print("⚠ Not enough data to train model")
    exit()

X = df[['temp', 'humidity', 'gas']]
y = df['aqi']

model = RandomForestRegressor(
    n_estimators=150,
    max_depth=6,
    random_state=42
)

model.fit(X, y)

print("Model trained successfully\n")

# ======================
# STEP 3: LIVE LOOP
# ======================
while True:
    try:
        df = get_data()

        if len(df) == 0:
            print("⚠ No data received")
            time.sleep(10)
            continue

        # latest row
        row = df.iloc[-1]

        # timestamp
        time_taken = row['time']

        # optional: format time nicely
        time_taken = datetime.strptime(time_taken, "%Y-%m-%dT%H:%M:%SZ")
        time_taken = time_taken.strftime("%d-%m-%Y %H:%M:%S")

        # prediction
        predicted_aqi = model.predict([[row['temp'], row['humidity'], row['gas']]])[0]
        predicted_aqi = round(predicted_aqi, 2)

        actual_aqi = row['aqi']

        # =========================
        # STATUS CLASSIFICATION
        # =========================
        if predicted_aqi <= 50:
            status_num = 1
            status_text = "Good"
        elif predicted_aqi <= 100:
            status_num = 2
            status_text = "Moderate"
        elif predicted_aqi <= 200:
            status_num = 3
            status_text = "Poor"
        elif predicted_aqi <= 300:
            status_num = 4
            status_text = "Very Poor"
        else:
            status_num = 5
            status_text = "Hazardous"

        # =========================
        # OUTPUT DISPLAY
        # =========================
        print(f" Time: {time_taken}")
        print(f" Temp: {row['temp']}")
        print(f" Humidity: {row['humidity']}")
        print(f" Gas: {row['gas']}")
        print(f" Actual AQI: {actual_aqi}")
        print(f" Predicted AQI: {predicted_aqi}")
        print(f" Status: {status_text}")
        print("-" * 40)

        # =========================
        # SEND TO THINGSPEAK
        # =========================
        payload = {
            'api_key': WRITE_API_KEY,
            'field5': predicted_aqi,
            'field6': status_num
        }

        requests.get(WRITE_URL, params=payload)
        print("Sent to ThingSpeak\n")

        # delay (ThingSpeak limit safe)
        time.sleep(20)

    except Exception as e:
        print("❌ Error:", e)
        time.sleep(10)