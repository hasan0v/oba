# OBA Smart Assistant - API Documentation

## Base URL

```
Development: http://localhost:8000/api/v1
Production: https://api.oba.az/api/v1
```

## Authentication

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

## Auth Endpoints

### Register User

```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "full_name": "İstifadəçi Adı",
  "phone": "+994501234567"
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "İstifadəçi Adı",
  "phone": "+994501234567",
  "points": 0,
  "tier": "bronze",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Login

```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Refresh Token

```http
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Get Current User

```http
GET /auth/me
```

**Headers:** Authorization required

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "İstifadəçi Adı",
  "phone": "+994501234567",
  "points": 1250,
  "tier": "silver",
  "badges": ["first_order", "reviewer"],
  "is_active": true
}
```

---

## Products Endpoints

### List Products

```http
GET /products
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | Page number |
| limit | int | 20 | Items per page (max 100) |
| category_id | int | - | Filter by category |
| min_price | float | - | Minimum price |
| max_price | float | - | Maximum price |
| sort_by | string | created_at | Sort field |
| order | string | desc | asc or desc |

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Samsung Galaxy A54",
      "description": "...",
      "price": 899.99,
      "discount_price": 799.99,
      "category_id": 1,
      "stock_quantity": 50,
      "images": ["url1", "url2"],
      "avg_rating": 4.5,
      "review_count": 23
    }
  ],
  "total": 150,
  "page": 1,
  "pages": 8
}
```

### Get Product

```http
GET /products/{id}
```

**Response (200):**
```json
{
  "id": 1,
  "name": "Samsung Galaxy A54",
  "description": "128GB RAM, 5G dəstəyi",
  "price": 899.99,
  "discount_price": 799.99,
  "category": {
    "id": 1,
    "name": "Smartfonlar"
  },
  "stock_quantity": 50,
  "images": ["url1", "url2"],
  "avg_rating": 4.5,
  "review_count": 23,
  "reviews": [...]
}
```

### Search Products

```http
GET /products/search
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | Yes | Search query |
| page | int | No | Page number |
| limit | int | No | Items per page |

### Get Recommendations

```http
GET /products/recommendations
```

**Headers:** Authorization required

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | int | 10 | Number of recommendations |

**Response (200):**
```json
{
  "items": [
    {
      "id": 15,
      "name": "...",
      "price": 299.99,
      "predicted_rating": 4.8,
      "reason": "Oxşar istifadəçilərin bəyəndiyi"
    }
  ]
}
```

### Get Deals

```http
GET /products/deals
```

Returns products with active discounts.

---

## Categories Endpoints

### List Categories

```http
GET /categories
```

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Elektronika",
      "icon": "devices",
      "product_count": 150,
      "children": [
        {
          "id": 2,
          "name": "Smartfonlar",
          "product_count": 45
        }
      ]
    }
  ]
}
```

---

## Cart Endpoints

### Get Cart

```http
GET /cart
```

**Headers:** Authorization required

**Response (200):**
```json
{
  "id": 1,
  "items": [
    {
      "id": 1,
      "product_id": 15,
      "product_name": "Samsung Galaxy A54",
      "quantity": 2,
      "unit_price": 799.99,
      "subtotal": 1599.98
    }
  ],
  "subtotal": 1599.98,
  "discount": 100.00,
  "total": 1499.98,
  "item_count": 2,
  "free_delivery_eligible": true
}
```

### Add to Cart

```http
POST /cart/items
```

**Request Body:**
```json
{
  "product_id": 15,
  "quantity": 2
}
```

### Update Cart Item

```http
PUT /cart/items/{item_id}
```

**Request Body:**
```json
{
  "quantity": 3
}
```

### Remove from Cart

```http
DELETE /cart/items/{item_id}
```

### Clear Cart

```http
DELETE /cart
```

---

## Orders Endpoints

### Create Order

```http
POST /orders
```

**Headers:** Authorization required

**Request Body:**
```json
{
  "shipping_address_id": 1,
  "payment_method": "card",
  "notes": "Zəng edin çatdırmazdan əvvəl"
}
```

**Response (201):**
```json
{
  "id": 1,
  "order_number": "OBA-2024-00001",
  "status": "pending",
  "items": [...],
  "subtotal": 1599.98,
  "shipping_cost": 0,
  "total": 1599.98,
  "points_earned": 160,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### List Orders

```http
GET /orders
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | Page number |
| status | string | - | Filter by status |

### Get Order

```http
GET /orders/{id}
```

### Cancel Order

```http
POST /orders/{id}/cancel
```

---

## Reviews Endpoints

### Create Review

```http
POST /products/{product_id}/reviews
```

**Request Body:**
```json
{
  "rating": 5,
  "comment": "Əla məhsul, tövsiyə edirəm!"
}
```

### List Product Reviews

```http
GET /products/{product_id}/reviews
```

---

## Complaints Endpoints

### Create Complaint

```http
POST /complaints
```

**Request Body:**
```json
{
  "order_id": 1,
  "category": "delivery",
  "subject": "Gecikmə",
  "description": "Sifariş 3 gün gecikmə ilə çatdırıldı"
}
```

### List My Complaints

```http
GET /complaints
```

### Get Complaint

```http
GET /complaints/{id}
```

---

## Gamification Endpoints

### Get Points History

```http
GET /users/points/history
```

**Response (200):**
```json
{
  "current_points": 1250,
  "tier": "silver",
  "next_tier": "gold",
  "points_to_next_tier": 750,
  "history": [
    {
      "id": 1,
      "points": 100,
      "type": "order",
      "description": "Sifariş #OBA-2024-00001",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Get Badges

```http
GET /users/badges
```

**Response (200):**
```json
{
  "earned": [
    {
      "id": "first_order",
      "name": "İlk Alış-veriş",
      "icon": "shopping_bag",
      "earned_at": "2024-01-15T10:30:00Z"
    }
  ],
  "available": [
    {
      "id": "big_spender",
      "name": "Böyük Alıcı",
      "description": "1000 AZN-dən çox xərcləyin",
      "progress": 65
    }
  ]
}
```

---

## Analytics Endpoints (Admin)

### Get Dashboard Stats

```http
GET /analytics/dashboard
```

**Headers:** Authorization (Admin) required

**Response (200):**
```json
{
  "total_revenue": 125000.00,
  "total_orders": 450,
  "total_users": 1200,
  "average_order_value": 277.78,
  "revenue_trend": [...],
  "top_products": [...],
  "category_distribution": [...]
}
```

### Get Demand Forecast

```http
GET /analytics/forecast/{product_id}
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| days | int | 30 | Forecast horizon |

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Yanlış sorğu formatı"
}
```

### 401 Unauthorized
```json
{
  "detail": "Token etibarsızdır və ya müddəti bitib"
}
```

### 403 Forbidden
```json
{
  "detail": "Bu əməliyyat üçün icazəniz yoxdur"
}
```

### 404 Not Found
```json
{
  "detail": "Resurs tapılmadı"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Etibarlı email daxil edin",
      "type": "value_error.email"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Daxili server xətası"
}
```

---

## Rate Limiting

API rate limits:
- **Anonymous**: 100 requests/minute
- **Authenticated**: 500 requests/minute
- **Admin**: 1000 requests/minute

Headers returned:
```
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 499
X-RateLimit-Reset: 1705312200
```

---

## Pagination

All list endpoints return paginated results:

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "pages": 8,
  "limit": 20
}
```

---

## Versioning

Current API version: **v1**

API version is included in the URL path. Breaking changes will result in a new version.
