# Scalable Auth Microservice with FastAPI

## Introduction

This project provides a highly scalable authentication microservice built using FastAPI. It offers authentication functionalities for different types of users, including end-users, admins, clients, and sub-clients. The authentication system is based on the IAM (Identity and Access Management) architecture, allowing for flexible user management and permission configurations.

## Features

- **User Management**: Supports authentication and user creation for end-users via mobile number verification.
- **Admin Management**: Allows super admins to create and manage admin accounts for system administration.
- **Client Management**: Admins can create and manage client accounts, enabling them to access specific resources.
- **Sub-Client Management**: Both admins and clients can create and manage sub-client accounts, facilitating hierarchical access control.
- **Policy Management**: Provides a flexible policy creation system, allowing admins to define custom access policies for clients and sub-clients.

## Dependencies

- **FastAPI**: Web framework for building APIs with Python.
- **uvicorn**: ASGI server for running FastAPI applications.
- **passlib**: Library for password hashing.
- **pymongo**: MongoDB driver for Python.
- **motor**: Asynchronous MongoDB driver for Tornado or asyncio.
- **python-dotenv**: Library for managing environment variables from a .env file.
- **pydantic[email]**: Data validation and settings management using Python type annotations.
- **python-jose**: JSON Web Tokens (JWT) implementation in Python.
- **requests**: HTTP library for making requests in Python.
- **Docker**: Containerization platform for building, shipping, and running applications.

## API Endpoints

### Authentication

- **Send OTP**: `/auth/otp/sendotp/{number}` (POST)
  - Sends OTP to verify the user's mobile number authenticity.
- **Login or Create User**: `/auth/user/login/{number}/{otp}` (POST)
  - Verifies OTP and creates a new user account if it doesn't exist already.
- **Create Admin**: `/auth/admin/create` (POST)
  - Allows super admins to create admin accounts.
- **Login Admin**: `/auth/admin/login` (POST)
  - Allows admins to log in using OTP or username/password credentials.
- **Create Client**: `/auth/client/create` (POST)
  - Enables admins to create client accounts.
- **Login Client**: `/auth/client/login` (POST)
  - Allows clients to log in using OTP or username/password credentials.
- **Create Sub Client**: `/auth/subclient/create` (POST)
  - Allows admins and clients to create sub-client accounts.
- **Login Sub Client**: `/auth/subclient/login` (POST)
  - Allows sub-clients to log in using OTP or username/password credentials.

### Access Management

- **Set Refresh Key**: `/user/access/setrefreshkey/{new_key}` (POST)
  - Sets a new refresh key for renewing JWT tokens without verifying the mobile number.
- **Get Regenerated Token**: `/user/access/regeneratetoken/{refresh_key}` (POST)
  - Regenerates a new JWT token using a secret refresh key.

### Data Directory

- **All Places**: `/mapdirectory/places/all` (GET)
  - Retrieves all records of places such as EV-chargers and swap stations.

### Root

- **Root Endpoint**: `/` (GET)
  - Returns a successful response.

## Getting Started

1. Clone the repository: `git clone <repository-url>`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables: Create a `.env` file in the project root directory and specify the following variables:
   - `FAST2SMS_API_KEY`: Your API key from Fast2sms for sending OTPs.
   - `MONGO_DB_URI`: URI for connecting to your MongoDB database.
   - `JWT_SECRET`: Secret key for JWT token generation.
   - `REFRESH_KEY_SECRET`: Secret key for refreshing JWT tokens.
4. Obtain necessary API keys:
   - **Fast2sms**: Create an account on Fast2sms and obtain your API key for sending OTPs.
5. Replace the required API keys in the `.env` file with your own.


# Install dependencies
RUN pip install -r requirements.txt

# Command to run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Usage

- Access the API documentation and test the endpoints using Swagger UI or ReDoc.
- Integrate the authentication microservice into your applications to handle user authentication and access management efficiently.

## License

This project is licensed under the GNU General Public License (GPL). You are free to use, modify, and distribute the code under the terms of the license.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your enhancements or bug fixes.

---

Feel free to adjust and expand upon this README as needed. Let me know if there's anything else I can assist you with!
