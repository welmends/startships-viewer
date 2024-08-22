# Starships Viewer

**Starships Viewer** is an application developed with FastAPI and Next.js that allows you to view information about Star Wars starships and manufacturers based on https://swapi.dev. The application provides endpoints for authentication and data queries, using JWT for security and MongoDB for storage.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Running Locally](#running-locally)
- [Usage](#usage)
- [Endpoints](#endpoints)
- [Contributing](#contributing)
- [License](#license)
- [Screenshots](#screenshots)

## Features

- **Authentication**: Login with JWT for secure access to endpoints.
- **Starships**: Query information about starships with support for pagination and filters.
- **Manufacturers**: List all available manufacturers in the database.
- **Celery**: An asynchronous task is triggered daily to update the BFF API database.

## Technologies Used

- **FastAPI**: Framework for building the API.
- **Uvicorn**: ASGI server to run the FastAPI application.
- **Pymongo**: MongoDB client for database interactions.
- **bcrypt**: Library for password hashing.
- **fastapi-jwt-auth**: Library for JWT authentication.
- **Celery/Beat/Redis**: Async processing.
- **MongoDB**: NoSQL database for data storage.

## Running locally

1. **Clone the repository:**

   ```bash
   git clone https://github.com/welmends/startships-viewer.git
   cd startships-viewer
   ```

2. **Run everything with docker-compose:**

   ```bash
   make
   ```

3. **Open the web app:**

   Checkout the web app in your browser: http://localhost:3000.

4. **Use the default user:**

   - Username: `admin`
   - Password: `admin`

5. **You can also take a look at the docs:**

   You can also take a look at the docs generated with OpenAPI: http://localhost:8000/docs.

## Usage

- **Authentication:** Send a POST request to `/api/login` with user credentials to obtain a JWT token.
- **Starships Query:** Use the `/api/starships` endpoint to list starships. You can apply filters and pagination.
- **Manufacturers Query:** Use the `/api/manufacturers` endpoint to list all manufacturers.

## Endpoints

- **POST /api/login**

  - **Description:** Authenticate a user and receive a JWT token.
  - **Request Body:** `{ "username": "string", "password": "string" }`
  - **Response:** `{ "access_token": "string" }`

- **GET /api/starships**

  - **Description:** Retrieve a list of starships with optional filters and pagination.
  - **Query Parameters:**
    - `page` (optional, default: 1): Page number for pagination.
    - `page_size` (optional, default: 10): Number of items per page.
    - `manufacturer` (optional): Filter by manufacturer name.
  - **Response:** `{ "next": "integer or null", "previous": "integer or null", "results": "array of starship objects" }`

- **GET /api/manufacturers**
  - **Description:** Retrieve a list of all manufacturers.
  - **Response:** `{ "results": "array of manufacturer names" }`

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure that your code follows the project’s coding style and includes appropriate tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Screenshots

<img width="1507" alt="Screenshot 1" src="https://github.com/user-attachments/assets/bbefff1c-ba9b-4a1e-a82b-a3b8c38881c1">

<img width="1507" alt="Screenshot 2" src="https://github.com/user-attachments/assets/5598b198-1105-4370-9289-e8dd05586c6c">
