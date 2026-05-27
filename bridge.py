import requests
import time
import csv

# --- CONFIGURATION ---
WRITE_API_KEY = "OT2YATM8H0R4STMZ"
CHANNEL_URL = "https://api.thingspeak.com/update"
CSV_FILE_NAME = "sensor_data.csv"
UPDATE_INTERVAL = 30

def stream_data():
    print(" Starting IoT Gateway...")
    
    while True:   
        try:
            with open(CSV_FILE_NAME, mode='r') as file:
                reader = csv.reader(file)
                
                # Skip header
                next(reader)

                for row in reader:
                    if len(row) >= 4:
                        field1 = row[0].strip()  # Temp
                        field2 = row[1].strip()  # Humidity
                        field3 = row[2].strip()  # Gas
                        field4 = row[3].strip()  # AQI

                        print(f"\n Sending: T={field1}, H={field2}, G={field3}, AQI={field4}")

                        payload = {
                            'api_key': WRITE_API_KEY,
                            'field1': field1,
                            'field2': field2,
                            'field3': field3,
                            'field4': field4
                        }


                        try:
                            response = requests.get(CHANNEL_URL, params=payload, timeout=10)
                            
                            if response.status_code == 200:
                                print(f" Sent! Entry ID: {response.text}")
                            else:
                                print(f" Error: {response.status_code}")

                        except Exception as e:
                            print(f" Connection failed: {e}")

                       # print(f" Waiting {UPDATE_INTERVAL}s...\n")
                        time.sleep(UPDATE_INTERVAL)

        except FileNotFoundError:
            print(f" File not found: {CSV_FILE_NAME}")
            break

        except Exception as e:
            print(f" Unexpected Error: {e}")
            break

if __name__ == "__main__":
    stream_data()