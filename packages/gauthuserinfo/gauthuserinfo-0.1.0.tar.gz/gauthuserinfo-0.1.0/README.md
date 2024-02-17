# GAuthUserInfo

GAuthUserInfo is a Python package designed to simplify the process of fetching user information from Google using OAuth2. It provides a convenient way to integrate Google authentication into your applications and retrieve user details.

## Installation

You can install the package using pip:

```bash
pip install gauthuserinfo
```
## Usage
```python

from gauthuserinfo import get_user_info

# Replace 'your_access_token' with the actual access token obtained through OAuth2.
access_token = 'your_access_token'

user_info = get_user_info(access_token)

if "error" in user_info:
    print(f"Error: {user_info['message']}")
else:
    print("Request successful!")
    print("User Info:")
    print(user_info)
```
## Features
- **Simplified Integration**: Easily integrate Google OAuth2 authentication into your Python applications.
- **User Information Retrieval**: Retrieve detailed user information, including name, email, and other relevant details.
- **Error Handling**: The package includes error handling to provide meaningful messages in case of issues.

## Dependencies
The package relies on the following external libraries:

- **requests**: HTTP library for making requests.

## Contributing
Contributions to GAuthUserInfo are welcome! If you encounter any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.