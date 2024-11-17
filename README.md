# sirius-back
Django backend for Sirius

---

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Running Tests](#running-tests)
- [API Documentation](#api-documentation)

---

## Introduction

`sirius-back` is a Django-based backend for the Sirius project.

---

## Installation

### Prerequisites

- Docker
- Docker Compose

### Steps


1. Clone the repository:

    ```bash
    git clone https://github.com/SiriusTeam7/sirius-back.git
    cd sirius-back
    ```

2. Copy the `.dev_env` file to `.env`:

    ```bash
    cp .dev_env .env
    ```

2. Build and run the Docker container:

    ```bash
    docker compose run sirius-back /bin/bash
    ```

3. In container shell, apply the database migrations:

    ```bash
    python manage.py migrate
    ```

4. Create a superuser:

    ```bash
    python manage.py createsuperuser
    ```

---

## Configuration

Configuration settings can be found in the `settings.py` file. You can customize the settings according to your needs, such as database configuration, installed apps, middleware, etc.

---

## Usage

### Running the Server

To start the development server, run:

```bash
docker-compose up
```

### Accessing the Admin Panel

You can access the Django admin panel at `http://127.0.0.1:9000/admin/` using the superuser credentials you created during installation.

### Stopping the Server

To stop the development server, press `Ctrl+C` in the terminal where `docker-compose up` is running

---

## Running Tests

To run the tests, use the following commands:

```bash
docker compose run sirius-back /bin/bash
python manage.py test
```

This command will execute all the tests defined in your Django application, including unit tests for serializers, services, and views.

---

## API Documentation

### Endpoints

- `/api/get-challenge/` - Generate a challenge for a student and course
- `/api/get-feedback/` - Generate feedback for a student's challenge answer

### Example Requests

#### Generate a Challenge for a Student and Course

**Endpoint:** `POST /api/get-challenge/`

**Request:**

```bash
curl -X POST http://127.0.0.1:8000/api/get-challenge/ -d '{"student_id": 1, "course_id": 1}' -H "Content-Type: application/json"
```

**Response:**

```json
{
    "challenge": "Generated challenge text"
}
```

#### Generate Feedback for a Student's Challenge Answer

**Endpoint:** `POST /api/get-feedback/`

**Request:**

```bash
curl -X POST http://127.0.0.1:8000/api/get-feedback/ -d '{"student_id": 1, "challenge_id": 1, "answer_type": "text", "answer_text": "This is my answer"}' -H "Content-Type: multipart/form-data"
```

**Response:**

```json
{
    "feedback": "Generated feedback text"
}
```

### Error Responses

All endpoints will return appropriate HTTP status codes and error messages in case of invalid requests or server errors. For example:

**Error Response:**

```json
{
    "error": "Challenge could not be generated."
}
```
