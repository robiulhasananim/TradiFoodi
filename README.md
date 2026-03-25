# TradiFoodi API

TradiFoodi is a Django-based REST API for an e-commerce platform specializing in traditional food items. It provides functionalities for user account management, product cataloging, and order processing.

## 🚀 Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

- **Python**: 3.10 or higher
- **PostgreSQL**: Installed and running
- **pip**: Python package manager

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/TradiFoodi.git
    cd TradiFoodi
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables**:
    Copy the `sample.env` file to `.env` and fill in your details:
    ```bash
    cp sample.env .env
    ```
    - Update `SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, etc.

5.  **Run Database Migrations**:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Create a Superuser**:
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the Development Server**:
    ```bash
    python manage.py runserver
    ```
    The API will be available at `http://127.0.0.1:8000/`.

---

## 🛠️ Development Tools

This project uses several tools to maintain code quality:

- **Black**: Code formatting.
- **Isort**: Import sorting.
- **Flake8**: Linting.
- **Pre-commit**: Runs these tools before every commit.

### Set up Pre-commit Hooks:
```bash
pre-commit install
```

---

## 📖 API Documentation

The project includes interactive API documentation powered by `drf-spectacular`:

- **Swagger UI**: `http://127.0.0.1:8000/api/schema/swagger/`
- **Redoc**: `http://127.0.0.1:8000/api/schema/redoc/`
- **Schema**: `http://127.0.0.1:8000/api/schema/`

---

## 🏗️ Project Structure & Conventions

### App Structure
- **`account`**: User authentication, registration, and profile management.
- **`product`**: Category and product management.
- **`order`**: Ordering system, order items, and payment handling.
- **`utils`**: Common utility functions, helpers, and custom exceptions.

### Conventions
- **API Responses**: All API responses use a standardized format defined in `utils/helpers.py`.
- **Authentication**: JWT authentication is used for all protected endpoints.
- **Permissions**: Custom permissions are defined in `account/permission.py` to handle roles (`admin`, `seller`, `customer`).
- **Models**: Use `UUID` or descriptive IDs where appropriate.
- **Environment**: Use `python-decouple` for all configuration settings.
