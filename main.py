from datadog import initialize, statsd
from datadog.api.constants import CheckStatus
import requests
import time

options = {
    'api_key':'api_key',         # your api key
    'app_key':'app_key'  # your app key
}

initialize(**options)

# Waterloo Municipality ID
Waterloo_municipalityId = '39CE69B3-7415-43E0-BBA8-E9BE9A1D88E5'

# Columbia/Phillip Southbound
stopId = '1093'


# Continuously ping GRT for data
while True:
    
    try:
        # Our API Request
        r = requests.get('https://api.pingstreet.ca/api/StopTime/?callback=&latitude=1&longitude=1&municipalityId=' + Waterloo_municipalityId + '&stopId=' + stopId)
	
        # Send service check to Datadog
        ## Figure out if the request succeeded
        if r.status_code == requests.codes.ok and r.text != 'null':
            status = CheckStatus.OK
        else:
            status = CheckStatus.CRITICAL

        ## Send the status to Datadog
        statsd.service_check(check_name='app.grt.status', status=status, message=str(r.status_code))

        # Convert the response to a JSON object
        stop_data = r.json()

        # iterate over every route
        for route in stop_data:
            
            # get route id
            routeId = route['routeId']

            # get the next scheduled bus
            next_bus_in_route = route['stopDetails'][0]

            # current time in seconds from midnight
            current_time = route['time']

            # time bus arrives in seconds from midnight
            arriving_time = next_bus_in_route['departure']

            # time bus is scheduled to arrive in seconds from midnight
            scheduled_time = next_bus_in_route['departureNonRealTime']

            # minutes until bus actually arrives
            bus_arrives_in_minutes = (arriving_time - current_time) / 60.0

            # minutes until bus is scheduled to arrive
            bus_scheduled_to_arrive_in_minutes = (scheduled_time - current_time) / 60.0

            # time difference between arriving and scheduled times in minutes
            difference_in_minutes = bus_arrives_in_minutes - bus_scheduled_to_arrive_in_minutes

            statsd.gauge('app.grt.' + routeId + '.arriving', bus_arrives_in_minutes)
            statsd.gauge('app.grt.' + routeId + '.scheduled', bus_scheduled_to_arrive_in_minutes)
            statsd.gauge('app.grt.' + routeId + '.difference', difference_in_minutes)

        # Request and send this data every 30 seconds
        time.sleep(30 - time.time() % 30)

    except requests.exceptions.RequestException as e:
        status = CheckStatus.CRITICAL
        statsd.service_check(check_name='app.grt.status', status=status, message=str(r.status_code))
        time.sleep(300)
