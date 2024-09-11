# Silent Steam

This project provides a simple RESTful API for managing educational assignments, classes, courses, and user accounts. The API is built with Django REST Framework and supports various operations through endpoints organized by resource type.

## Installation

1. Clone repo: `https://github.com/ddvuser/silent-steam.git`
2. Start Docker service: `systemctl start docker`
3. Run: `cd silent-steam && docker compose up`

## API Overview

The User API is accessible to everyone, allowing users to create accounts and manage their profiles. Courses can only be created by teachers, who have the authority to set up and manage their classes. Teachers can create Classrooms based on existing courses, whether those they have created themselves or other courses. They also have the capability to add students to these classrooms. Additionally, teachers can create Assignments for their classes. Students can submit their work through the Submissions API and view the assignments they need to complete. Grading is a restricted feature, reserved solely for teachers. Students can view only their own grades and submissions, ensuring that they have access to their personal performance data while maintaining privacy and security in the grading process.

## API Endpoints

### User Management

- Create User
  - `POST /api/user/create/`
  - Creates a new user account
- Manage User
  - `GET /api/user/me/`
  - Retirieves details of the currently authenticated user.
- Request Password Reset
  - `POST /api/user/request-password-reset`
  - Requests a password reset for the user.
- Reset Password
  - `POST /api/user/reset-password/<str:token>/`
  - Resets the password using a provided token.
- JWT Token Management
  - `POST /api/user/token/`
    - Obtains a new token pair (access and refresh.)
  - `POST /api/user/token/refresh/`
    - Refreshes the access token.
  
### Courses

- List Courses
  - `GET /api/courses/`
  - Retrieves a list of all courses.
- Retrieve, Update or Delete a Course
  - `GET /api/course/<pk>/`
  - `PUT /api/course/<pk>/`
  - `PATCH /api/course/<pk>/`
  - `DELETE /api/course/<pk>/`
  - Retrieves, updates, or deletes a specific course by its ID.
  
### Classrooms

- List Classrooms
  - `GET /api/classroom/`
  - Retrieves a list of all classrooms.
- Retrieve, Update or Delete a Classroom
  - `GET /api/classroom/<pk>/`
  - `PUT /api/classroom/<pk>/`
  - `PATCH /api/classroom/<pk>/`
  - `DELETE /api/classroom/<pk>/`
  - Retrieves, updates, or deletes a specific classroom by its ID.

### Assignments

- List Grades
  - `GET /api/assignment/`
  - Retrieves a list of all assignments.
- Retrieve, Update or Delete a Assignment
  - `GET /api/assignment/<pk>/`
  - `PUT /api/assignment/<pk>/`
  - `PATCH /api/assignment/<pk>/`
  - `DELETE /api/assignment/<pk>/`
  - Retrieves, updates, or deletes a specific assignment by its ID.

### Submissions

- List Submissions
  - `GET /api/grade/`
  - Retrieves a list of all submissions.
- Retrieve, Update or Delete a Submission
  - `GET /api/grade/<pk>/`
  - `PUT /api/grade/<pk>/`
  - `PATCH /api/grade/<pk>/`
  - `DELETE /api/grade/<pk>/`
  - Retrieves, updates, or deletes a specific submission by its ID.

### Grades

- List Grades
  - `GET /api/grade/`
  - Retrieves a list of all grades.
- Retrieve, Update or Delete a Grade
  - `GET /api/grade/<pk>/`
  - `PUT /api/grade/<pk>/`
  - `PATCH /api/grade/<pk>/`
  - `DELETE /api/grade/<pk>/`
  - Retrieves, updates, or deletes a specific grade by its ID.

## Authentication

- Token Authentication: application uses JWT (JSON Web Tokens) for authentication. Obtain a token by posting to `/api/user/token/` and include the token in the Authorization header as `Bearer <token>` for authenticated requests.

## Tech Stack

- Django
- PostgreSQL
- Django REST Framework
- Docker
- Swagger UI
- Flake8
