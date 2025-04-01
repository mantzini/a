import requests
import os
import sys
import time
import rtp_utils 


SERVICE_IP = "10.10.10.30"
BASE_URL = f"http://{SERVICE_IP}:30900/api/v2.0.0.0"
SESSION_LIMIT = "20"
SESSION_SORT = "{\"id\":\"DESC\"}"

"""Logs in to the API and retrieves a JWT token."""
def login(username: str, password: str) -> str:
    url = f"{BASE_URL}/users/login"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "login": username,
        "password": password,
        "application_type": "NOMADE_COPAEUROPE",
        "application_os": "ANDROID",
        "application_device_id": "db476e2c22303f44",
        "application_device_name": "any"
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        token = response.json().get("token")
        if token:
            print("\n✅ Login successful! Token retrieved.\n")
            return token
        else:
            print("\n❌ Login failed: No token received.\n")
            return None
    except requests.RequestException as e:
        print(f"\n❌ Login request failed: {e}\n")
        return None

"""Fetches and displays session data with options to stream a session."""
def get_sessions(token: str, status: str = "active") -> None:
    url = f"{BASE_URL}/sessions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"JWT {token}",
        "Connection": "Keep-Alive"
    }
    params = {"status": status, "limit" : SESSION_LIMIT, "sort": SESSION_SORT}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        sessions = data.get("sessions", [])
        
        if not sessions:
            print("\n⚠️ No finished sessions found.\n")
            return
        
        print("\n📌 Available Sessions:")
        for idx, session in enumerate(sessions, start=1):
            print(f"{idx}.\tSession ID: {session['id']},\tCreated: {session['created_at']}, SDP Length: {len(session['sdp'])}")
        
        while True:
            print("\n🔽 Enter a session number to start streaming, or press Enter to return:")
            choice = input()
            
            if choice == "":
                return  # Return to main menu
            
            if choice.isdigit():
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(sessions):
                    send_session_to_stream(token, sessions[choice_idx]['id'])
                else:
                    print("\n❌ Invalid choice. Please try again.")
            else:
                print("\n❌ Invalid input. Enter a valid number or press Enter to go back.")
    
    except requests.RequestException as e:
        print(f"\n❌ Failed to retrieve sessions: {e}\n")

def send_session_to_stream(token: str, session_id: int) -> None:
    """Starts a streaming session for a given session ID."""
    url = f"{BASE_URL}/sessions/session-destination-streams"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"JWT {token}",
        "Connection": "Keep-Alive"
    }
    payload = {"session_id": session_id}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        #print("Response:", response.json())

        # inityally extract fields safely with default values
        decryption_key = data.get("session_decryption_key", "N/A")
        service_port = data.get("session_destination_service_port", "N/A")
        session_sdp = data.get("session_sdp", "N/A")
        service_ip = data.get("session_destination_service_ip", "N/A")
        service_protocol = data.get("session_destination_service_protocol", "N/A")

        # Display formatted session details
        print(f"\n📌 ***Streaming Session {session_id} Details:***")
        #print(f"🔹 Decryption Key: {decryption_key}")
        print(f"🔹 Service Port: {service_port}")
        #print(f"🔹 Session SDP: {session_sdp}")
        #print(f"🔹 Service IP: {service_ip}")
        print(f"🔹 Service Protocol: {service_protocol.upper()}\n")
        
        #start the RTP dummy data..
        rtp_utils.send_dummy_rtcp(service_ip, service_port, session_id, 56000)
        print(f"✅ Successfully started streaming session {session_id}!")
    except requests.RequestException as e:
        print(f"❌ Failed to start streaming session {session_id}: {e}")

def clear_screen():
    """Clears the terminal screen for better UI experience."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """Displays the menu options at the bottom of the terminal."""
    print("\n" + "=" * 50)
    print("📌 MENU - Select an option:")
    print("1️⃣  Login")
    print("2️⃣  Get Sessions")
    print("3️⃣  Exit")
    print("=" * 50)
    print("🔽 Choose an option: ", end="", flush=True)  # Keeps cursor in place

def main():
    """Main function to handle menu interactions."""
    token = None
    token = login("1-2", "azertyui") #TODO: Maybe remove this after testing?
    while True:
        clear_screen()
        show_menu()
        choice = input()
        
        if choice == "1":
            clear_screen()
            username = input("Enter username: ")
            password = input("Enter password: ")
            token = login(username, password)
        elif choice == "2":
            if not token:
                print("\n⚠️ Please login first!\n")
                time.sleep(2)
            else:
                get_sessions(token)
        elif choice == "3":
            print("\n👋 Exiting... Goodbye!\n")
            sys.exit(0)
        else:
            print("\n❌ Invalid choice! Please select a valid option.\n")
            time.sleep(1.5)

if __name__ == "__main__":
    main()
