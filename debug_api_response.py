#!/usr/bin/env python3
"""
Debug API response format
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def debug_api_response():
    """Debug the API response format."""
    
    # Register a driver
    driver_data = {
        "first_name": "Debug",
        "last_name": "Driver",
        "email": "debug@example.com",
        "phone": "+1234567899",
        "password": "password123",
        "role": "driver"
    }
    
    driver_response = requests.post(f"{BASE_URL}/auth/register", json=driver_data)
    if driver_response.status_code != 200:
        print(f"Driver registration failed: {driver_response.text}")
        return
    
    driver_auth = driver_response.json()
    driver_token = driver_auth["access_token"]
    driver_headers = {"Authorization": f"Bearer {driver_token}"}
    
    # Register a passenger
    passenger_data = {
        "first_name": "Debug",
        "last_name": "Passenger",
        "email": "debug2@example.com",
        "phone": "+1234567898",
        "password": "password123",
        "role": "passenger"
    }
    
    passenger_response = requests.post(f"{BASE_URL}/auth/register", json=passenger_data)
    if passenger_response.status_code != 200:
        print(f"Passenger registration failed: {passenger_response.text}")
        return
    
    passenger_auth = passenger_response.json()
    passenger_token = passenger_auth["access_token"]
    passenger_headers = {"Authorization": f"Bearer {passenger_token}"}
    
    # Driver goes online
    requests.put(f"{BASE_URL}/drivers/status", json={"status": "online"}, headers=driver_headers)
    
    # Passenger requests a ride
    ride_data = {
        "pickup": "Nairobi CBD",
        "destination": "Jomo Kenyatta Airport",
        "pickup_latitude": -1.2921,
        "pickup_longitude": 36.8219,
        "destination_latitude": -1.3192,
        "destination_longitude": 36.9278,
        "ride_type": "standard",
        "estimated_fare": 150.0,
        "notes": "Debug ride"
    }
    
    ride_response = requests.post(f"{BASE_URL}/rides/request", json=ride_data, headers=passenger_headers)
    if ride_response.status_code != 200:
        print(f"Ride request failed: {ride_response.text}")
        return
    
    ride = ride_response.json()
    ride_id = ride["id"]
    
    # Get ride requests
    requests_response = requests.get(f"{BASE_URL}/drivers/requests", headers=driver_headers)
    if requests_response.status_code == 200:
        requests_data = requests_response.json()
        print("Ride requests response:")
        print(json.dumps(requests_data, indent=2, default=str))
    else:
        print(f"Get ride requests failed: {requests_response.text}")

if __name__ == "__main__":
    debug_api_response()
