import json
import folium
from folium.plugins import MarkerCluster
import requests
from requests.auth import HTTPBasicAuth

def polyline_to_folium(polyline: list):
    return [(c['lat'], c['lon']) for c in polyline]

def get_center(zoneID, track):
    params = (
        ('zoneID', zoneID), # ZoneID Mainz: 3898, eva: 8000240
        ('track', str(track)),
        ('sector', 'A'),
    )

    response = requests.get('https://maps-test.reisenden.info/rimapsapi/0.7/station/platform/position', headers=headers, params=params)
    s = response.content.decode()
    j = json.loads(s) 
    center = j['center']
    return (center['lat'], center['lon'])

def add_track_polygon(track, map):
    params = (
        ('zoneID', '3898'), # ZoneID Mainz: 3898, eva: 8000240
        ('track', str(track)),
        ('sector', 'A'),
    )

    response = requests.get('https://maps-test.reisenden.info/rimapsapi/0.7/station/platform/position', 
                            headers=headers, params=params)
    s = response.content.decode()
    j = json.loads(s)
    try:
        multipol = j['geometry']['coordinates']
        center = j['center']
        c_coords = (center['lat'], center['lon'])
        folium.Marker(c_coords, str(track)).add_to(map)
        coords = [(c[1], c[0]) for c in multipol[0][0]]
        folium.Polygon(coords, tooltip = str(track)).add_to(map)
    except KeyError:
        return

if __name__ == "__main__":    
    headers = {
        'accept': 'application/json',
        'Authorization': '',
    }
    with open('stations_all.json', 'r') as f:
        stations_all = json.load(f)#      
    
#    params = (
#        ('provider', 'DB'),
#    )
#
#    response = requests.get('https://maps-test.reisenden.info/rimapsapi/0.7/station/list/all',
#                            headers=headers, params=params)
#    stations_all = json.loads(response.content.decode())
    stations = stations_all['stations']
    mainz = [s for s in stations if s['name'] == 'Mainz Hbf'][0]
    position = mainz['position']
    mainz_coords = [position['lat'], position['lon']]
    my_map = folium.Map(location = mainz_coords, zoom_start = 16)
    
    # Zeichne Bahnsteige
    for track in range(1, 8):
        add_track_polygon(track, my_map)
    
#   Routing:

#    params = (
#        ('zoneID', '3898'),
#        ('fromTrack', '1'),
#        ('fromSector', 'B'),
#        ('toTrack', '5'),
#        ('toSector', 'C'),
#        ('handicapped', 'true'),
#    )
#    
#    response = requests.get('https://maps-test.reisenden.info/rimapsapi/0.7/station/routing/indoor/byplatform', headers=headers, params=params)
#  
  
    mainz_eingang = [50.00082, 8.25833]  # Eingang West

    coords_pl5 = get_center('3898', 5) # Bahnsteig Gleis 5
    params = (
        ('zoneID', '3898'),
        ('fromLevel', 'GROUND_FLOOR'),
        ('fromLon', mainz_eingang[1]),
        ('fromLat', mainz_eingang[0]),
        ('toLevel', 'GROUND_FLOOR'),
        ('toLon', coords_pl5[1]),
        ('toLat', coords_pl5[0]),
        ('handicapped', 'true'),
    )
    
    response = requests.get('https://maps-test.reisenden.info/rimapsapi/0.7/station/routing/indoor/byposition', headers=headers, params=params)  
            
    j = json.loads(response.content.decode())
    path = []
    for seg in j['segments']:
        path += polyline_to_folium(seg['polyline'])
    folium.PolyLine(path, f"{j['length']} m", color='red').add_to(my_map)
    
# Get departures:   
params = (
    ('timeEnd', '2020-11-15T00:00:00Z'),
    ('filterTransports', ''),
)
response = requests.get('https://innoapi-k8s01-dev-fcd.reisenden.info/2.14/boards/boards/public/departure/8000240,', headers=headers, params=params)  

#folium.Marker(location=mainz_eingang, popup='Start', color="red").add_to(my_map)
my_map.save('mainz.html')