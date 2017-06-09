from datadog import initialize, api
import requests
import time

options = {
	'api_key':'api',
	'app_key':'app'
}

initialize(**options)

while True:
    r = requests.get("http://api.pingstop.com/StopTime?") # WIP
    # Send service check to Datadog

    # Get stop data from our request
    stop_data = r.json()
    print(stop_data)

    # Get time to next bus
    # Send metric to Datadog

    # Get time to next scheduled bus
    # Send metric to Datadog

    # Ping every 60 seconds
    time.sleep(60 - time.time() % 60)