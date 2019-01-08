# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib.request import urlopen
import calendar
import requests
#import simplejson, urllib

apikey = '' # insert your google api key here

no_pages = 1

departure_time = calendar.timegm((2016,2,12,7,0,0))

destinations = {
                'Klatreverket,+Sandakerveien+24C,+0473+Oslo,+Norway': 45,
                'Lysaker+stasjon,+Bærum,+Norway': 50,
                'Brynseng+T,+Oslo,+Norway': 45,
                'Ringstabekk,+Bærum': 60}

search_params = {
    'new_prop': 'false',
    'from_price': 2500000,
    'to_price': 3500000,
    'from_area': 50,
    'to_area': 80,
    'published_age': '', #'published=1'
    'page': 1
}

searchtemp = "http://m.finn.no/realestate/homes/search.html?{published_age}&" \
          "location=0.20003&location=1.20003.20045&location=0.20061&location=1.20061.20528&location=1.20061.20507&" \
             "location=1.20061.20519&location=1.20061.20515&location=1.20061.20524&location=1.20061.20529&" \
             "location=1.20061.20527&location=1.20061.20523&location=1.20061.20522&location=1.20061.20518&" \
             "location=1.20061.20520&location=1.20061.20514&location=1.20061.20516&location=1.20061.20526&" \
             "location=1.20061.20532&location=1.20061.20510&location=1.20061.20530&location=1.20061.20509&" \
             "location=1.20061.20525&location=1.20061.20517&location=1.20061.20533&location=1.20061.20508&" \
             "location=1.20061.20531&location=1.20061.20521&" \
             "is_new_property={new_prop}&" \
             "price_collective_from={from_price}&price_collective_to={to_price}&" \
             "area_from={from_area}&area_to={to_area}&" \
             "page={page}"

def get_finn_properties(searchtemp):
    hits = []
    for no in range(1,no_pages+1):
        search_params['page'] = no
        searchurl = searchtemp.format(**search_params)
        print(searchurl)

        response = urlopen(searchurl)
        soup = BeautifulSoup(response)

        for div in soup.find_all('div', {'class' : 'flex-unit result-item'}):
            a = div.find_all('a',href=True)[0]
            link = a['href']
            adr_div = div.find_all('div',{'class': 'rightify d1 unoverflowify'})[0]
            if a.find_all('span', {'class': "fleft objectstatus sold"}):
                continue
            adr = a.find_all('span', {'class': "blockify ptt opaque"})[0].text
            hits.append([adr, link])
    return hits


def add_distance(props):
    maps_url = "https://maps.googleapis.com/maps/api/distancematrix/json?" \
               "origins={adr}&" \
               "destinations={dest}&" \
               "mode=transit&" \
               "departure_time={deptime}&" \
               "language=en-EN&sensor=false&" \
               "key={key}"
    for i,prop in enumerate(props):
        adr = prop[0]
        prop.append({})
        for dest in destinations.keys():
            params = {'adr': adr.replace(' ','+'), 'dest': dest, 'deptime': departure_time, 'key': apikey}
            url = maps_url.format(**params)
            resp = requests.get(url)
            j = resp.json()
            try:
                duration = j['rows'][0]['elements'][0]['duration']['value']
            except:
                duration = 999999
            prop[2][dest] = duration/60
    return props


props = get_finn_properties(searchtemp)
distance_props = add_distance(props)

filtered_props = []
for p in distance_props:
    if not [dest for dest in p[2].keys() if p[2][dest] > destinations[dest]]:
        filtered_props.append(p)

for hit in filtered_props:
    print(hit[0])
    print(hit[1])
    for k in hit[2].keys():
        print('\t'+k+": "+str(hit[2][k]))
    print('\n')

print('displayed ' + str(len(filtered_props)) + '/' + str(len(distance_props)))

# https://maps.googleapis.com/maps/api/distancematrix/json?origins=Bentsebrugata+18+B,+Oslo&destinations=Lilleakerveien+4,+Oslo,+Norway&mode=transit&departure_time=1455260400&language=en-EN&sensor=false&key=******
# url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false".format(str(orig_coord),str(dest_coord))
# result= simplejson.load(urllib.urlopen(url))
# driving_time = result['rows'][0]['elements'][0]['duration']['value']
