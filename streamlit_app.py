import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import math

# Load ZIP code data from the provided Excel file
data = pd.read_excel('ShippingZoneHeatmapConceptV1_multi-ZIP_copilot.xlsx')

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points
    on the Earth specified in decimal degrees.
    """
    R = 3959.87433  # Radius of the Earth in miles
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon1 - lon2)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    a = math.sin(dLat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dLon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def determine_zone(distance):
    """
    Determine the shipping zone based on the distance.
    """
    if distance <= 50:
        return 'Zone 1'
    elif distance <= 150:
        return 'Zone 2'
    elif distance <= 300:
        return 'Zone 3'
    elif distance <= 600:
        return 'Zone 4'
    elif distance <= 1000:
        return 'Zone 5'
    elif distance <= 1400:
        return 'Zone 6'
    elif distance <= 1800:
        return 'Zone 7'
    else:
        return 'Zone 8'

def get_marker_color(zone):
    """
    Get the marker color based on the shipping zone.
    """
    colors = {
        'Zone 1': '#7b004c',
        'Zone 2': '#d6006d',
        'Zone 3': '#ed40a9',
        'Zone 4': '#ff5100',
        'Zone 5': '#ff9e18',
        'Zone 6': '#008996',
        'Zone 7': '#00707a',
        'Zone 8': '#b8bfc5'
    }
    return colors.get(zone, 'gray')  # Default to gray if the zone is not in the dictionary

def process_zip_codes(input_zip_codes, data):
    """
    Process the input ZIP codes and calculate the shipping zones.
    """
    for user_zip in input_zip_codes:
        if user_zip in data['ZIP Code'].values:
            user_lat = data.loc[data['ZIP Code'] == user_zip, 'Latitude'].iloc[0]
            user_lon = data.loc[data['ZIP Code'] == user_zip, 'Longitude'].iloc[0]

            for index, row in data.iterrows():
                zip_lat = row['Latitude']
                zip_lon = row['Longitude']
                distance = haversine(user_lat, user_lon, zip_lat, zip_lon)
                data.at[index, 'Calculated Shipping Zone'] = determine_zone(distance)
        else:
            st.error(f"ZIP Code {user_zip} not found in the dataset.")
    return data

def create_map(processed_data):
    """
    Create a folium map with markers for each ZIP code.
    """
    initial_location = [processed_data['Latitude'].iloc[0], processed_data['Longitude'].iloc[0]]
    map = folium.Map(location=initial_location, zoom_start=10)

    for index, row in processed_data.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"ZIP Code: {row['ZIP Code']}\nShipping Zone: {row['Calculated Shipping Zone']}",
            icon=folium.Icon(color=get_marker_color(row['Calculated Shipping Zone']))
        ).add_to(map)

    return map

# Streamlit app layout
st.title("Shipping Zone Heatmap Web Application")
st.write("Enter up to six 5-digit ZIP codes to generate a shipping zone heatmap.")

# Input form for ZIP codes
zip_codes = []
for i in range(6):
    zip_code = st.text_input(f"Enter ZIP Code {i+1}", max_chars=5)
    if zip_code:
        if zip_code.isdigit() and len(zip_code) == 5:
            zip_codes.append(zip_code)
        else:
            st.error("Only 5-digit ZIP codes are accepted")

if st.button("Analyze"):
    if zip_codes:
        processed_data = process_zip_codes(zip_codes, data.copy())
        map_ = create_map(processed_data)
        folium_static(map_)
