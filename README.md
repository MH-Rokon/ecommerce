# Django E-commerce API

A robust and extensible E-commerce REST API built with Django and Django REST Framework (DRF). This project includes user registration and login with email verification, product and category management, Stripe payment integration, and product review functionality.

## Features

### ✅ User Management
- Custom user model with email authentication
- User registration with email confirmation
- JWT-based login and logout
- Password reset functionality
- Authenticated user profile endpoint

### ✅ Products & Categories
- CRUD operations for categories and products
- Product filtering, search, and pagination

### ✅ Shopping Cart & Orders
- Add, remove, and view cart items
- Create orders from the cart
- Stripe checkout integration
- Stock management after payment

### ✅ Reviews
- Users can submit and view product reviews
- Authenticated creation and public viewing

### ✅ Additional Features
- Book titles scraper from [Books to Scrape](https://books.toscrape.com) (Bonus)

## Tech Stack
- Django 5.2.3
- Django REST Framework
- JWT Authentication (SimpleJWT)
- Stripe API (Payment Integration)
- SQLite (Development Database)
- Render (Deployment)

## Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/MH-Rokon/ecommerce_api.git
cd ecommerce_api
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate       # For Linux/macOS
venv\Scripts\activate          # For Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the root directory and add your environment variables:

```
STRIPE_SECRET_KEY=your_key
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_password
```

Alternatively, add them directly in `settings.py` (not recommended for production).

5. **Apply migrations and start the server**

```bash
python manage.py migrate
python manage.py runserver
```

6. **Run tests (optional)**

```bash
python manage.py test
```



## License

This project is for educational and evaluation purposes.
