from datadog import initialize, statsd
from datadog.api.constants import CheckStatus
import requests
import time

Waterloo_municipalityId = '39CE69B3-7415-43E0-BBA8-E9BE9A1D88E5' # Waterloo Municipality ID
stopId = '1093'                                                  # Columbia/Phillip Southbound

options = {
	'api_key':'be1f2f552b4c72f3e16c27c4bf08e732',
	'app_key':'a9855a5b8adedda6d04b239bd7496a3f2c43597d'
}

initialize(**options)


while True:

    r = requests.get('https://api.pingstreet.ca/api/StopTime/?callback=&latitude=1&longitude=1&municipalityId=' + Waterloo_municipalityId + '&stopId=' + stopId) # WIP
    
    # Send service check to Datadog
    ## Figure out if the request succeeded
    if r.status_code == requests.codes.ok and r.text != 'null':
        status = CheckStatus.OK
    else:
        status = CheckStatus.CRITICAL

    ## Send the status to Datadog
    statsd.service_check(check_name='app.grt.status', status=status, message=str(r.status_code))

    # Get stop data from our request
    stop_data = r.json()

    # Get time to next bus
    for route in stop_data:
        routeId = route['routeId']
        current_time = route['time']

        next_bus_in_route = route['stopDetails'][0]

        arriving_time = next_bus_in_route['departure']
        scheduled_time = next_bus_in_route['departureNonRealTime']

        bus_arrives_in_minutes = (arriving_time - current_time) / 60.0
        bus_scheduled_to_arrive_in_minutes = (scheduled_time - current_time) / 60.0
        difference_in_minutes = bus_arrives_in_minutes - bus_scheduled_to_arrive_in_minutes

        print(routeId + str(bus_arrives_in_minutes) + ", " + str(bus_scheduled_to_arrive_in_minutes) + ", " + str(difference_in_minutes))

        statsd.gauge('app.grt.' + routeId + '.arriving', bus_arrives_in_minutes)
        statsd.gauge('app.grt.' + routeId + '.scheduled', bus_scheduled_to_arrive_in_minutes)
        statsd.gauge('app.grt.' + routeId + '.difference', difference_in_minutes)

    # Ping every 30 seconds
    time.sleep(30 - time.time() % 30)