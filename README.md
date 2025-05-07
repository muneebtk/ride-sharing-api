# Ride Sharing API

## Overview

The Ride Sharing API is a backend solution for a ride-sharing platform, built using Django and Django REST Framework (DRF). It provides features like user registration, ride management, driver assignment, and real-time ride tracking using WebSockets. This project is designed to simulate and support essential functionalities of a modern ride-sharing service.

---

## Features

1. **User Authentication**

   * User registration and login.
   * Token-based authentication using Simple JWT.

2. **Ride Management**

   * Create, track, and update ride requests.
   * Driver assignment and ride status updates.

3. **Real-time Location Tracking**

   * WebSocket-based real-time updates for ride locations.

4. **Driver Management**

   * Fetch available drivers based on proximity to the pickup location.

5. **Simulation**

   * Simulates real-time ride-tracking updates for testing purposes using Celery tasks.

6. **Geolocation Data Storage**

   * Uses PostgreSQL with the PostGIS extension to store and handle geolocation data efficiently.

---

## Prerequisites

Before running the API, ensure you have the following installed:

* Python 3.9+
* Django 4+
* PostgreSQL
* PostGIS extension for PostgreSQL
* Redis (version 5 or above, for Celery and WebSocket channels)
* Docker (optional, for containerized deployment)

---

## Installation and Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-repository/ride-sharing-api.git
   cd ride-sharing-api
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Setup the Database**

   * Create a PostgreSQL database with the PostGIS extension enabled.
   * Configure the database settings in `settings.py`.
   * Run migrations:

     ```bash
     python manage.py makemigrations
     ```
     ```bash
     python manage.py migrate
     ```

5. **Run the Development Server**

   ```bash
   python manage.py runserver
   ```

6. **Start Celery Worker and Beat**

   * Run Celery:

     ```bash
     celery -A ride_sharing worker --loglevel=info
     ```
   * Run Celery Beat for periodic tasks:

     ```bash
     celery -A ride_sharing beat --loglevel=info
     ```

7. **Setup Redis**

   * Ensure Redis is running for WebSocket and Celery functionalities.

---

## API Documentation

The API is documented in Postman. Access the documentation [here](https://documenter.getpostman.com/view/22016828/2sB2j7dpKA).

### Example Endpoints:

#### **User Registration**

* **Method:** POST
* **Endpoint:** `/api/users/register/`
* **Description:** Registers a new user.

#### **Ride Request**

* **Method:** POST
* **Endpoint:** `/api/rides/request/`
* **Description:** Creates a new ride request by specifying pickup and dropoff locations.

#### **Real-time Ride Tracking**

* **Method:** WebSocket
* **Endpoint:** `ws://<domain_name>/ws/ride-tracking/<ride_id>/`
* **Description:** Provides real-time location updates for a ride.

---

## Running Tests

Run the test suite to ensure all functionalities work as expected:

```bash
python manage.py test
```

---

## Deployment

For production, use Docker or a deployment platform like AWS, Azure, or Heroku. A sample `Dockerfile` and `docker-compose.yml` are included for containerized deployment.

---

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
