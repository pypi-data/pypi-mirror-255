import requests, sys
def get_user_info(access_token):
    url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        return response.json()

    except requests.RequestException as e:
        return {
            "error": True,
            "message": f"Request failed: {str(e)}"
        }

def main():
    if len(sys.argv) != 2:
        print("Usage: gauthuserinfo <access_token>")
        sys.exit(1)

    access_token = sys.argv[1]
    result = get_user_info(access_token)
    print(result)
