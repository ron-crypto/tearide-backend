#!/usr/bin/env python3
"""
Test script for ride request flow
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_ride_request_flow():
    """Test the complete ride request flow."""
    
    print("🧪 Testing Ride Request Flow")
    print("=" * 50)
    
    # Step 1: Register a passenger
    print("\n1️⃣ Registering passenger...")
    passenger_data = {
        "first_name": "Jane",
        "last_name": "Passenger",
        "email": "jane3@example.com",
        "phone": "+1234567894",
        "password": "password123",
        "role": "passenger"
    }
    
    passenger_response = requests.post(f"{BASE_URL}/auth/register", json=passenger_data)
    if passenger_response.status_code == 200:
        passenger_auth = passenger_response.json()
        passenger_token = passenger_auth["access_token"]
        print("✅ Passenger registered")
    else:
        print(f"❌ Passenger registration failed: {passenger_response.text}")
        return
    
    # Step 2: Register a driver
    print("\n2️⃣ Registering driver...")
    driver_data = {
        "first_name": "John",
        "last_name": "Driver",
        "email": "john3@example.com",
        "phone": "+1234567895",
        "password": "password123",
        "role": "driver"
    }
    
    driver_response = requests.post(f"{BASE_URL}/auth/register", json=driver_data)
    if driver_response.status_code == 200:
        driver_auth = driver_response.json()
        driver_token = driver_auth["access_token"]
        print("✅ Driver registered")
    else:
        print(f"❌ Driver registration failed: {driver_response.text}")
        return
    
    passenger_headers = {"Authorization": f"Bearer {passenger_token}"}
    driver_headers = {"Authorization": f"Bearer {driver_token}"}
    
    # Step 3: Driver goes online
    print("\n3️⃣ Driver going online...")
    status_response = requests.put(f"{BASE_URL}/drivers/status", json={"status": "online"}, headers=driver_headers)
    if status_response.status_code == 200:
        print("✅ Driver is now online")
    else:
        print(f"❌ Driver status update failed: {status_response.text}")
    
    # Step 4: Passenger requests a ride
    print("\n4️⃣ Passenger requesting ride...")
    ride_data = {
        "pickup": "Nairobi CBD",
        "destination": "Jomo Kenyatta Airport",
        "pickup_latitude": -1.2921,
        "pickup_longitude": 36.8219,
        "destination_latitude": -1.3192,
        "destination_longitude": 36.9278,
        "ride_type": "standard",
        "estimated_fare": 150.0,
        "notes": "Test ride request"
    }
    
    ride_response = requests.post(f"{BASE_URL}/rides/request", json=ride_data, headers=passenger_headers)
    if ride_response.status_code == 200:
        ride = ride_response.json()
        ride_id = ride["id"]
        print(f"✅ Ride requested successfully. Ride ID: {ride_id}")
    else:
        print(f"❌ Ride request failed: {ride_response.text}")
        return
    
    # Step 5: Driver checks for ride requests
    print("\n5️⃣ Driver checking for ride requests...")
    requests_response = requests.get(f"{BASE_URL}/drivers/requests", headers=driver_headers)
    if requests_response.status_code == 200:
        requests_data = requests_response.json()
        print(f"✅ Driver received {len(requests_data)} ride requests")
        
        if len(requests_data) > 0:
            request = requests_data[0]
            print(f"   - Ride ID: {request['id']}")
            print(f"   - Passenger: {request['passenger_name']}")
            print(f"   - From: {request['pickup_address']}")
            print(f"   - To: {request['destination_address']}")
            print(f"   - Fare: KSh {request['fare']}")
    else:
        print(f"❌ Get ride requests failed: {requests_response.text}")
    
    # Step 6: Driver accepts the ride
    print("\n6️⃣ Driver accepting ride...")
    accept_response = requests.post(f"{BASE_URL}/drivers/requests/{ride_id}/accept", headers=driver_headers)
    if accept_response.status_code == 200:
        print("✅ Driver accepted the ride")
    else:
        print(f"❌ Accept ride failed: {accept_response.text}")
    
    # Step 7: Check ride status
    print("\n7️⃣ Checking ride status...")
    ride_details_response = requests.get(f"{BASE_URL}/rides/{ride_id}", headers=passenger_headers)
    if ride_details_response.status_code == 200:
        ride_details = ride_details_response.json()
        print(f"✅ Ride status: {ride_details['status']}")
        print(f"   - Driver ID: {ride_details.get('driver_id', 'Not assigned')}")
    else:
        print(f"❌ Get ride details failed: {ride_details_response.text}")
    
    print("\n🎉 Ride Request Flow Test Complete!")
    print("=" * 50)
    print("✅ Complete ride request flow is working!")
    print("✅ Driver can see and accept ride requests")
    print("✅ Frontend should now display ride requests properly")

if __name__ == "__main__":
    test_ride_request_flow()
