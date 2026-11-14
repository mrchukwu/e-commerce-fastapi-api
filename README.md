# 🛒 E-Commerce FastAPI API

A robust, production-ready backend infrastructure for an E-commerce platform, built with **FastAPI** and **PostgreSQL**. This API provides complete functionality for user authentication, product management, category organization, shopping carts, and address management.

## 📖 Table of Contents
- [🛒 E-Commerce FastAPI API](#-e-commerce-fastapi-api)
  - [📖 Table of Contents](#-table-of-contents)
  - [🎯 About the Project](#-about-the-project)
  - [💻 Tech Stack \& Tools](#-tech-stack--tools)
  - [📋 Prerequisites \& Requirements](#-prerequisites--requirements)
  - [🚀 Installation \& Setup](#-installation--setup)
  - [🏗️ Project Architecture \& Build Steps](#️-project-architecture--build-steps)
  - [🔌 API Endpoints](#-api-endpoints)
    - [🔐 Authentication (`/auth`)](#-authentication-auth)
    - [👤 Users (`/users`)](#-users-users)
    - [📦 Products (`/products`)](#-products-products)
    - [🗂️ Categories (`/categories`)](#️-categories-categories)
    - [🛒 Cart (`/cart`)](#-cart-cart)
    - [📍 Addresses (`/addresses`)](#-addresses-addresses)
  - [🔑 Environment Variables](#-environment-variables)

---

## 🎯 About the Project

This project is a fully functional E-commerce REST API designed to handle the core operations of an online store. It features secure JWT-based authentication, role-based access control, complex data relationships (users, products, categories, carts, and addresses), and comprehensive CRUD operations. 

The architecture follows a **Layered Design** (Router → Service → Repository → Model) ensuring separation of concerns, making the codebase highly maintainable, testable, and scalable.

---

## 💻 Tech Stack & Tools

**Core Technologies:**
*   **Language:** Python 3.10+
*   **Framework:** FastAPI (High-performance ASGI framework)
*   **Database:** PostgreSQL
*   **ORM:** SQLAlchemy 2.0 (using `Mapped` and `mapped_column`)
*   **Data Validation:** Pydantic v2 & `pydantic-settings`
*   **Authentication:** JWT (JSON Web Tokens) via `python-jose`
*   **Password Hashing:** `pwdlib` (with Argon2/Bcrypt)

**Tools Used:**
*   **Server:** Uvicorn (ASGI web server)
*   **Database Driver:** `psycopg2` / `psycopg`
*   **API Documentation:** Scalar / Swagger UI (Auto-generated)
*   **Version Control:** Git & GitHub

---

## 📋 Prerequisites & Requirements

Ensure you have the following installed on your machine:
*   Python 3.10 or higher
*   PostgreSQL installed and running
*   Git

You can install all Python dependencies using the provided `requirements.txt`:
```bash
pip install -r requirements.txt
```
*(Key dependencies include: `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `pydantic-settings`, `psycopg2-binary`, `python-jose`, `pwdlib`, `scalar-fastapi`)*

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mrchukwu/e-commerce-fastapi-api.git
   cd e-commerce-fastapi-api
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables:**
   Copy the `.env_example` file to create your own `.env` file:
   ```bash
   cp .env_example .env
   ```
   *(Open `.env` and fill in your PostgreSQL database URL and generate a secure Secret Key).*

5. **Create the Database:**
   Ensure PostgreSQL is running and the database specified in your `.env` exists. The tables will be automatically created when the app starts for the first time.

6. **Run the Application:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`.

7. **Access API Documentation:**
   *   **Scalar Docs:** `http://127.0.0.1:8000/scalar`
   *   **Swagger UI:** `http://127.0.0.1:8000/docs`

---

## 🏗️ Project Architecture & Build Steps

The project was built using a modular, domain-driven structure:

```text
app/
├── api/              # Main API router configuration
├── common/           # Shared utilities (price calculations, dependencies)
├── core/             # Configuration (settings), security (JWT, hashing)
├── database/         # Database connection, Base declarative class, session maker
├── modules/          # Feature-based modules
│   ├── address/      # Address models, schemas, repos, services, routers
│   ├── auth/         # Login/Register logic
│   ├── cart/         # Cart and CartItem logic
│   ├── category/     # Product categories
│   ├── products/     # Product catalog
│   └── users/        # User management
└── main.py           # FastAPI application entry point
```

**Build Steps Overview:**
1.  **Database Setup:** Configured SQLAlchemy engine and session management.
2.  **Models:** Created SQLAlchemy models (`User`, `Product`, `Category`, `Cart`, `Address`) with proper relationships and constraints.
3.  **Schemas:** Built Pydantic schemas for request validation and response serialization (e.g., `ProductCreate`, `CartRead`).
4.  **Security:** Implemented password hashing and JWT access token generation/decoding.
5.  **Repositories:** Built the data access layer to handle SQL queries.
6.  **Services:** Implemented business logic (e.g., validating stock, calculating cart totals, handling address defaults).
7.  **Routers:** Exposed the services as RESTful HTTP endpoints.

---

## 🔌 API Endpoints

All endpoints are prefixed with `/api/v1`. Protected routes require a `Bearer <token>` in the `Authorization` header.

### 🔐 Authentication (`/auth`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and receive a JWT access token |

**Example: Register User**
```json
POST /api/v1/auth/register
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

### 👤 Users (`/users`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/users/profile` | Get current logged-in user profile |
| `GET` | `/users` | (Admin only) List all users |
| `GET` | `/users/{user_id}` | Get a specific user |
| `PATCH` | `/users/{user_id}` | Update user details |

### 📦 Products (`/products`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/products` | List products (supports pagination & search) |
| `GET` | `/products/search` | Search products by name/brand/description |
| `GET` | `/products/{product_id}` | Get product details |
| `POST` | `/products` | Create a product |
| `PATCH` | `/products/{product_id}` | Update product partially |
| `DELETE` | `/products/{product_id}` | Delete a product |

**Example: Create Product**
```json
POST /api/v1/products/
{
  "name": "Dell XPS 15",
  "brand_name": "Dell",
  "model_no": "XPS15-2024",
  "description": "Premium laptop",
  "warrenty": "2 Years",
  "discount_percent": 10.0,
  "stock_quantity": 25,
  "price": 2199.99,
  "image_url": "https://example.com/laptop.jpg",
  "category_id": 1,
  "highlights": ["16GB RAM", "1TB SSD"],
  "additional_images": [],
  "specification": []
}
```

### 🗂️ Categories (`/categories`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/categories` | List all categories |
| `POST` | `/categories` | Create a new category |
| `GET` | `/categories/{id}` | Get category details |

### 🛒 Cart (`/cart`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/cart` | Get current user's active cart |
| `POST` | `/cart/items` | Add an item to the cart |
| `PATCH` | `/cart/items/{item_id}` | Update item quantity in cart |
| `DELETE` | `/cart/items/{item_id}` | Remove item from cart |

**Example: Add to Cart**
```json
POST /api/v1/cart/items
{
  "product_id": 1,
  "quantity": 2
}
```

### 📍 Addresses (`/addresses`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/addresses` | List all addresses for current user |
| `POST` | `/addresses` | Add a new address |
| `GET` | `/addresses/{id}` | Get a specific address |
| `PATCH` | `/addresses/{id}` | Update an address |
| `DELETE` | `/addresses/{id}` | Delete an address |

**Example: Create Address**
```json
POST /api/v1/addresses/
{
  "full_name": "Kennedy Chukwu",
  "phone_number": "+2348012345678",
  "address_line1": "12 Admiralty Way",
  "address_line2": "Lekki Phase 1",
  "city": "Lagos",
  "state": "Lagos",
  "postal_code": "106104",
  "country": "Nigeria",
  "is_default": true
}
```

---

## 🔑 Environment Variables

Create a `.env` file in the root directory. Refer to `.env_example`:

```env
# Database Credentials
DATABASE_URL=postgresql://postgres:password@localhost:5432/ecommerce_db

# Security
SECRET_KEY=your_super_secret_jwt_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# App Settings
APP_NAME=FastAPI Ecommerce
API_PREFIX=/api/v1
```

---
*Built with ❤️ using FastAPI.*