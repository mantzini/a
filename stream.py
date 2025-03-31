import requests
import json
import subprocess


# Define the API endpoint and the headers
url = "http://10.10.10.30:30900/api/v2.0.0.0/users/login"
headers = {
    "Authorization": "JWT 123",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Define the payload (data to be sent with the POST request)
payload = {
    "login": "1-2",
    "password": "azertyui",
    "application_type": "NOMADE_COPAEUROPE",
    "application_os": "ANDROID",
    "application_device_id": "db476e2c22303f44",
    "application_device_name": "any"
}

# Send the POST request and capture the response
response = requests.post(url, headers=headers, json=payload)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    response_json = response.json()

    # Extract the token
    token = response_json.get("token")

    # Check if the token was extracted
    if token:
        print("Token extracted successfully:", token)
    else:
        print("Failed to extract the token from the response.")
else:
    print(f"Request failed with status code {response.status_code}.")

url = "http://10.10.10.30:30900/api/v2.0.0.0/sessions/session-source-streams"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"JWT {token}",
    "Connection": "Keep-Alive"
}

#   POST payload
payload = {
    "application_id": 1,
    "session_sdp": "o=- 0 0 IN IP4 127.0.0.1 s=No Name c=IN IP4 127.0.0.1 t=0 0 a=tool:libavformat LIBAVFORMAT_VERSION m=video 9095 RTP/AVP 96 a=rtpmap:96 H264/90000 ",
    "user_login": "1-2",
    "user_password": "azertyui"
}

response = requests.post(url, headers=headers, json=payload)

port =""
# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    response_json = response.json()

    # Extract session_source_service_port and session_id
    port = response_json.get("session_source_service_port")
    session_id = response_json.get("session_id")

    if port and session_id:
        print(f">> Port: {port}")
        print(f">> Session_id: {session_id}")
    else:
        print("Error: Could not extract port or session_id from response.")
else:
    print(f"Request failed with status code {response.status_code}.")

# Define input file and RTP server address
input_file = "test.mp4"  # Replace with your video file path
rtp_address = "udp://10.10.10.30:" + str(port) +"?pkt_size=1316" 
#print (rtp_address + "\n")


ffmpeg_cmd = [
    "ffmpeg",
     "-f", "lavfi",  # Use LAVFI (Libavfilter virtual input)
    #"-loglevel", "debug",
    "-an",
    "-i", "testsrc=size=640x480:rate=25",  # Example: Generate a test video
    "-c:v", "libx265",  # Video codec (H.264)
    "-payload_type", "96",
    "-ssrc", str(session_id),  # Set SSRC directly from session_id
    "-f", "rtp",  # Output format
    rtp_address  # RTP address for video
]

# Run the FFmpeg command
process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Print FFmpeg logs (optional)
for line in process.stderr:
    print(line.decode(), end="")

# Wait for the process to finish (in case you need to handle it further)
process.wait()
