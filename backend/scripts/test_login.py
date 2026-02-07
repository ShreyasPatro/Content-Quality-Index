import requests

def test_login():
    url = "http://127.0.0.1:8000/api/v1/auth/login/access-token"
    # Content-Type: application/x-www-form-urlencoded (OAuth2 standard)
    data = {
        "username": "admin@example.com",
        "password": "password"
    }
    try:
        response = requests.post(url, data=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login()
