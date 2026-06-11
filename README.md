# Django eCommerce Web Application

A full-featured eCommerce web application built with **Django**, designed to provide a smooth online shopping experience for users and a manageable admin interface for store owners.

This project demonstrates practical knowledge of **backend development, database design, authentication & Authirozation, shopping cart logic, order processing, and Implemetation OWASP Top10 Security improvement ** using Django.

---

## Features

- User registration with Kavenegar OTP, Safe login and Forget Password 
- Product listing and product detail pages
- Home Page Mega Menu
- Category-based product filtering
- Shopping cart management
- Add to cart / remove from cart
- Checkout workflow
- Zarinpal Payment System implementation
- Order placement
- User profile and order history
- Admin dashboard for managing Users, products, categories, orders and blogs
- Responsive design for desktop and mobile devices
- MySql Data-Base Architectury Design



## Tech Stack

**Backend**
- Django
- Python

**Frontend**
- HTML
- CSS
- Bootstrap / Tailwind / JavaScript *(choose what applies)*

**Database**
- MySQL DataBase


## Security Features

**Security Improvement based on OWASP Top 10 Bugs**

- XSS (Cross-Site Scripting)
- SQLi (SQL Injection)
- Command Injection
- Bussines Logic Vulnerabilities
- IDOR
- Race Condition in Payment Workflow
- CSRF
- SSRF
- Information Disclosure



## Installation

- 1.Clone the repository

```

git clone https://github.com/Ataeskandarifar/Django-E-Commerce-Shop.git
cd Django-E-Commerce-Shop

```

- 2.Create and activate a virtual environment

```
python3 -m venv venv
source venv/bin/activate

```

- 3. Install dependencies

```
pip install -r requirements.txt

```

- 4. Apply migrations

```
python manage.py migrate

```

- 5. Create a superuser

```
python manage.py createsuperuser

```

- 6. Run the development server

```
python manage.py runserver

```


## Learning Outcomes
This project helped me strengthen my understanding of:

- Django project structure and app organization
- Models, views, templates, and URL routing
- User authentication and authorization
- Database relationships and migrations
- CRUD functionality
- Session/cart handling
- Zarinpal Payment Architectury
- Web Application Security implementations
- Used Arvan Cloud CDN to get Better Loading Speed & non-accessible Server IP
- Deployable web application architecture


## Author

Ata Eskandarifar

- GitHub: https://github.com/AtaEskandarifar
