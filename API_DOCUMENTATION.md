# Tradi Foodi API - Complete Exhaustive Documentation

This document serves as the absolute source of truth for all RESTful APIs available in the Tradi Foodi backend.

---

## Global Standards

### Base URL
`http://localhost:8000/api/`

### ID Conventions
The system uses a dual-ID structure:
1. **Internal ID (`id`)**: A hidden, auto-incrementing integer primary key used strictly for database relations.
2. **Public ID**: A unique, string-based identifier used for all API communication and frontend lookups.

| Entity | Public ID Name in Payload | Format | Example |
| :--- | :--- | :--- | :--- |
| **User** | `uid` | `USR-XXXXXXXXXX` | `USR-DD3B28FBC9` |
| **Category** | `cat_id` | `CXXXXXX` | `C3F4D3` |
| **Product** | `product_id` | `[Category-ID]-PXXXXXX` | `C3F4D3-P3GE47Y` |
| **Order** | `order_id` | `ORD-XXXXXXXXXX` | `ORD-06491AD35F` |
| **Review** | `review_id` | `REV-XXXXXXXXXX` | `REV-A1B2C3D4E5` |
| **OrderItem**| `item_id` | `ITM-XXXXXXXXXX` | `ITM-F1E2D3C4B5` |

**Important for Frontend**: The generic `id` field has been replaced with the specific ID names above (e.g., `uid`, `product_id`) in all JSON payloads to prevent confusion with internal database keys.

### Standard Response Format
Every endpoint (success or error) returns the following JSON structure:

```json
{
  "success": boolean,
  "status": number, // HTTP Status Code
  "message": "string",
  "data": object | array | null,
  "errors": object | null, // Detailed validation errors
  "meta": { // Present only in paginated list views
    "total": number,
    "page": number,
    "limit": number,
    "totalPages": number
  }
}
```

---

## 1. Authentication & Accounts (`/api/accounts/`)

### Register User
- **Endpoint**: `POST /register/`
- **Auth**: Public
- **Description**: Creates a new user. Returns JWT tokens on success.
- **Fields**: `email`, `first_name`, `last_name`, `phone`, `address`, `city`, `postal_code`, `password`, `password2`, `role` (`customer`, `seller`).
- **Note**: `phone`, `address`, and `city` are required for placing orders later.

### Login User
- **Endpoint**: `POST /login/`
- **Auth**: Public
- **Description**: Authenticates user via email/password. Returns JWT tokens.

### Get My Profile
- **Endpoint**: `GET /profile/`
- **Auth**: Authenticated (JWT)
- **Description**: Returns full profile details of the logged-in user.

### Update My Profile
- **Endpoint**: `PATCH /profile/`
- **Auth**: Authenticated (JWT)
- **Description**: Partially updates profile fields.

### Change Password
- **Endpoint**: `POST /changepassword/`
- **Auth**: Authenticated (JWT)
- **Description**: Changes password for the logged-in user.
- **Fields**: `password`, `password2`.

### Logout
- **Endpoint**: `POST /logout/`
- **Auth**: Authenticated (JWT)
- **Description**: Blacklists the provided refresh token.
- **Fields**: `refresh` (token string).

### Forgot Password - Step 1: Send Email
- **Endpoint**: `POST /send-reset-password-email/`
- **Auth**: Public
- **Description**: Sends a password reset link to the user's email.
- **Fields**: `email`.

### Forgot Password - Step 2: Reset
- **Endpoint**: `POST /reset-password/<uid>/<token>/`
- **Auth**: Public
- **Description**: Sets a new password using the token from the email.
- **Fields**: `password`, `password2`.

---

## 2. Categories (`/api/products/categories/`)

### List Categories
- **Endpoint**: `GET /`
- **Auth**: Public
- **Description**: Retrieves all categories with pagination support.

### Create Category
- **Endpoint**: `POST /`
- **Auth**: Admin or Seller Only
- **Fields**: `name`, `image`, `description`.

### Get Category Details
- **Endpoint**: `GET /<id>/`
- **Auth**: Public

### Update Category (Full)
- **Endpoint**: `PUT /<id>/`
- **Auth**: Admin or Seller Only

### Update Category (Partial)
- **Endpoint**: `PATCH /<id>/`
- **Auth**: Admin or Seller Only

### Delete Category
- **Endpoint**: `DELETE /<id>/`
- **Auth**: Admin or Seller Only

---

## 3. Products (`/api/products/`)

### List Products
- **Endpoint**: `GET /`
- **Auth**: Public
- **Features**:
  - **Pagination**: `page`, `limit`
  - **Filtering**: `category` (slug/ID), `min_price`, `max_price`, `rating`, `isAvailable`.
  - **Sorting**: `ordering` (`price`, `rating_avg`, `created_at`, `name`).
  - **Search**: `search` (name/description).

### Create Product
- **Endpoint**: `POST /`
- **Auth**: Admin or Seller Only
- **Fields**: `name`, `description`, `price`, `originalPrice`, `stock`, `category_id`, `images` (array), `ingredients` (array), `preparationTime`, `servingSize`, `sizes` (array), `color` (array), `isAvailable`.

### Get Product Details
- **Endpoint**: `GET /<id>/`
- **Auth**: Public
- **Data**: Includes calculated `rating` and `reviewCount`.

### Update Product (Full)
- **Endpoint**: `PUT /<id>/`
- **Auth**: Admin or Owner (The Seller who created it)

### Update Product (Partial)
- **Endpoint**: `PATCH /<id>/`
- **Auth**: Admin or Owner

### Delete Product
- **Endpoint**: `DELETE /<id>/`
- **Auth**: Admin or Owner

---

## 4. Product Reviews (`/api/products/<id>/reviews/`)

### List Product Reviews
- **Endpoint**: `GET /`
- **Auth**: Public
- **Description**: Returns all reviews for the specified product ID.

### Post a Review
- **Endpoint**: `POST /`
- **Auth**: Authenticated (JWT)
- **Constraint**: Only one review per user per product.
- **Fields**: `rating` (1-5), `comment`.

---

## 5. Orders (`/api/orders/`)

### Create Order
- **Endpoint**: `POST /`
- **Auth**: Authenticated (JWT)
- **Description**: Only authenticated users can create an order. The request must include updated or existing profile information in the `profile` object. This profile data will be saved to the user's permanent account profile before the order is created.
- **Payload**:
  ```json
  {
    "items": [
      {
        "product_id": "CAT-001-PRD-001",
        "quantity": 2,
        "size": "M", 
        "color": "Red"
      }
    ],
    "paymentMethod": "cod",
    "delivery_note": "Optional delivery instructions",
    "profile": {
      "first_name": "Abdur",
      "last_name": "Rahman",
      "email": "customer@example.com",
      "phone": "+8801700000000",
      "address": "House 12, Road 5, Dhanmondi",
      "city": "Dhaka",
      "postal_code": "1205"
    }
  }
  ```
- **Constraint**: 'COD' (Cash on Delivery) is the only supported payment method. All profile fields in the payload are required for a successful order.

### List My Orders
- **Endpoint**: `GET /`
- **Auth**: Authenticated (JWT)
- **Description**: 
  - Customers see only their own orders.
  - Admins and Sellers see ALL system orders.
- **Filtering**: `status`, `payment_status`, `total_amount` (min/max), `created_at`.

### Get Order Details
- **Endpoint**: `GET /<id>/`
- **Auth**: Authenticated (JWT)
- **Description**: Retrieves full items, status, and customer info (via relations) for a specific order.
- **Response Data**: Includes `id`, `customer_name`, `contact_number`, `deliveryAddress`, `deliveryCity`, `deliveryPostalCode`, `delivery_note`, `paymentMethod`, `totalPrice`, `status`, `items`, `created_at`.

### Update Order Status
- **Endpoint**: `PATCH /<id>/`
- **Auth**: Admin or Seller Only
- **Fields**: `status` (`pending`, `confirmed`, `preparing`, `delivered`, `cancelled`), `payment_status` (`pending`, `paid`, `failed`).

---

## 6. Schema & Documentation

### OpenAPI JSON Schema
- **Endpoint**: `GET /api/schema/`

### Swagger UI (Interactive)
- **Endpoint**: `GET /api/schema/swagger/`

### Redoc (Static)
- **Endpoint**: `GET /api/schema/redoc/`
