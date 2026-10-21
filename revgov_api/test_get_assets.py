import requests

url = "https://92.204.249.19:9091/api/v1/reusable-assets"
headers = {
    'accept': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3ODY1MjU2MzgsInN1YiI6IjIwIn0.JR67lS6zNk8CZ_1cHe7mz2HNt3AQmZxpS_-m3Iga95I'
}

response = requests.get(url, headers=headers, verify=False)
print("Status Code:", response.status_code)
print("Response Text:", response.text)
