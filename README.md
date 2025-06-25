# Django E-commerce API

A robust and extensible E-commerce REST API built with Django and Django REST Framework (DRF). This project includes user registration and login with email verification, product and category management, Stripe payment integration, and product review functionality.

## Features

### User Management
- Custom user model with email authentication
- User registration with email confirmation
- JWT-based login and logout
- Password reset functionality
- Authenticated user profile endpoint

### Products & Categories
- CRUD operations for categories and products
- Product filtering, search, and pagination

### Shopping Cart & Orders
- Add, remove, and view cart items
- Create orders from the cart
- Stripe checkout integration
- Stock management after payment

### Reviews
- Users can submit and view product reviews
- Authenticated creation and public viewing

### Additional Features
- Book titles scraper from https://books.toscrape.com (bonus)

## Tech Stack
- Django 5.2.3
- Django REST Framework
- JWT Authentication with SimpleJWT
- Stripe Payment API
- SQLite (development database)
- Render for deployment (recommended)



## Setup Instructions
'''
1.Clone the repository:

   ```bash
    git clone  https://github.com/MH-Rokon/ecommerce_api.git
   cd django-ecommerce-api




2.Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate       # Linux/macOS
venv\Scripts\activate          # Windows




3.Install dependencies:
pip install -r requirements.txt


4.onfigure environment variables:
Add Stripe API keys and email settings in your .env file or directly in settings.py




5.Run migrations and start the development server:
python manage.py migrate
python manage.py runserver


6.Run tests to verify:
python manage.py test