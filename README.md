# Exploring Flask for Web Development

This repository is a learning project aimed at exploring **Flask**, a lightweight and versatile web development framework. The project will evolve into a comprehensive tool for managing **users**, **vendors**, and **invoices**. 

### Features (Planned):
- User, vendor, and invoice management.
- Interactive dashboard with dynamic **graphs** and **plots** for data visualization.

Stay tuned for updates! Contributions and feedback are welcome. 🚀

# API Documentation

## 1. Get a User by ID

**Route**: `GET /api/v1/users/<int:id>`

- **Description**: This route retrieves a specific user by their unique `id`.
- **Parameters**:
  - `id` (int): The unique identifier for the user you want to retrieve.
  
- **Success Response**:
  - **Code**: `200 OK`
  - **Content**:
    ```json
    [
      {
        "id": 1,
        "username": "john_doe",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "date_created": "2024-01-01T12:00:00Z"
      }
    ]
    ```

- **Error Response**:
  - **Code**: `404 Not Found`
  - **Content**:
    ```json
    {
      "message": "User not found"
    }
    ```

---

## 2. Get All Users

**Route**: `GET /api/v1/users/`

- **Description**: This route retrieves a list of all users.
- **Parameters**: None.
  
- **Success Response**:
  - **Code**: `200 OK`
  - **Content**:
    ```json
    [
      {
        "id": 1,
        "username": "john_doe",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "date_created": "2024-01-01T12:00:00Z"
      },
      {
        "id": 2,
        "username": "jane_doe",
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "date_created": "2024-01-02T12:00:00Z"
      }
    ]
    ```

---

## Example Code

```python
from flask import Blueprint, request, jsonify
from database import get_user_by_id, get_all_users

# Blueprint for user-related API routes
user_blueprint = Blueprint('user_api', __name__, url_prefix='/api/v1/users')

# Route to get a user by ID
@user_blueprint.route('/<int:id>', methods=['GET'])
def get_user(id):
    user = get_user_by_id(id)
    if user:
        return jsonify([user.to_dict()])
    else:
        return jsonify({"message": "User not found"}), 404

# Route to get all users
@user_blueprint.route('/', methods=['GET'])
def all_users():
    users = get_all_users()
    return jsonify([user.to_dict() for user in users])
