# RevLine - Car Parts E-Commerce Platform

RevLine is a comprehensive online car parts shop focused on vehicle compatibility. Our platform features a searchable product catalog, intelligent compatibility system to prevent incorrect orders, seamless checkout process, and multilingual support for a global audience.

## 🚀 Features

- **Vehicle Compatibility System**: Smart filtering to ensure customers order the right parts for their vehicles
- **Multilingual Support**: Available in English, Spanish, and Georgian
- **User Account Management**: Registration, login, profile management, and order history
- **Shopping Cart & Wishlist**: Persistent cart with wishlist functionality
- **Comprehensive Checkout**: Multi-step checkout with billing, shipping, and payment processing
- **Product Catalog**: Advanced search and filtering for automotive parts
- **Admin Dashboard**: Custom admin interface for managing products, orders, and users
- **Responsive Design**: Mobile-first design with Bootstrap 5
- **RESTful API**: Built with Django REST Framework
- **Caching**: Redis-powered caching for optimal performance

## 🛠️ Tech Stack

### Backend
- **Django 4.2.7** - Python web framework
- **Django REST Framework** - API development
- **PostgreSQL** - Primary database
- **Redis** - Caching and session storage
- **Celery** - Asynchronous task processing

### Frontend
- **Bootstrap 5** - CSS framework
- **Django Crispy Forms** - Enhanced form rendering
- **JavaScript** - Interactive components

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Gunicorn** - WSGI server
- **WhiteNoise** - Static file serving
- **Nginx** - Reverse proxy (production)

### Third-party Services
- **Stripe** - Payment processing
- **AWS S3** - File storage (production)
- **PostgreSQL** - Database

## 🌍 Supported Languages

- **English** (default) - `http://revline.com/`
- **Spanish** - `http://revline.com/es/`
- **Georgian** - `http://revline.com/ka/`

Users can switch languages through the dropdown menu in the navigation bar. All interface elements are fully translated.

## 📋 Prerequisites

- **Docker** and **Docker Compose** (recommended)
- OR **Python 3.12+**, **PostgreSQL 15+**, and **Redis 7+**
- **Git** for version control

## 🚀 Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd revline
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file with your configuration (see Environment Variables section below).

3. **Build and start services**
   ```bash
   docker-compose up --build
   ```

4. **Run initial setup**
   ```bash
   # Run migrations
   docker-compose exec web python manage.py migrate
   
   # Create superuser
   docker-compose exec web python manage.py createsuperuser
   
   # Load initial data (optional)
   docker-compose exec web python manage.py loaddata checkout/fixtures/shipping_methods.json
   
   # Populate sample data with brands, categories, and products (optional)
   docker-compose exec web python manage.py populate_sample_data
   
   # Compile translation messages
   docker-compose exec web python manage.py compilemessages
   ```

5. **Access the application**
   - Web application: http://localhost:8000
   - Admin panel: http://localhost:8000/admin
   - API: http://localhost:8000/api/

## 🔧 Local Development Setup

1. **Clone and setup virtual environment**
   ```bash
   git clone <repository-url>
   cd revline
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup database**
   ```bash
   # Install PostgreSQL and create database
   createdb revline_db
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your local configuration
   ```

5. **Run migrations and setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py loaddata checkout/fixtures/shipping_methods.json
   python manage.py compilemessages
   
   # Populate sample data with brands, categories, and products (optional)
   python manage.py populate_sample_data
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

## ⚙️ Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration
DB_NAME=revline_db
DB_USER=revline_user
DB_PASSWORD=revline_pass
DB_HOST=db
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://redis:6379/1

# Email Configuration (Production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password

# AWS S3 Configuration (Production)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Payment Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

## 🏗️ Project Structure

```
revline/
├── accounts/          # User management and authentication
├── cart/             # Shopping cart and wishlist functionality
├── checkout/         # Order processing and payment
├── config/           # Django project settings and URLs
├── locale/           # Translation files
├── media/            # User-uploaded files
├── products/         # Product catalog and management
├── shop/             # Core shop functionality and views
├── static/           # Static assets (CSS, JS, images)
├── templates/        # HTML templates
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── manage.py
```

## 🌐 Managing Translations

### Adding a New Language

1. **Add language to settings**
   ```python
   # config/settings.py
   LANGUAGES = [
       ('en', 'English'),
       ('es', 'Español'),
       ('ka', 'ქართული'),
       ('fr', 'Français'),  # New language
   ]
   ```

2. **Generate message files**
   ```bash
   docker-compose exec web python manage.py makemessages -l fr
   ```

3. **Translate strings**
   Edit `locale/fr/LC_MESSAGES/django.po` and add translations.

4. **Compile messages**
   ```bash
   docker-compose exec web python manage.py compilemessages
   ```

### Updating Existing Translations

1. **Extract new translatable strings**
   ```bash
   docker-compose exec web python manage.py makemessages -a
   ```

2. **Edit translation files**
   Update files in `locale/<language_code>/LC_MESSAGES/django.po`

3. **Compile messages**
   ```bash
   docker-compose exec web python manage.py compilemessages
   ```

## 🔌 API Endpoints

The application provides a RESTful API accessible at `/api/`:

- `GET /api/products/` - List products
- `GET /api/products/{id}/` - Product details
- `GET /api/categories/` - Product categories
- `POST /api/cart/add/` - Add item to cart
- `GET /api/orders/` - User orders (authenticated)

## 📊 Sample Data

Populate database with sample data (5 brands, 10 categories, 50 products):
```bash
python manage.py populate_sample_data
# Docker: docker-compose exec web python manage.py populate_sample_data
```

## 🧪 Testing

```bash
# Run tests
docker-compose exec web python manage.py test

# Run specific app tests
docker-compose exec web python manage.py test shop

# Run with coverage
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
```

## 🚀 Production Deployment

### Environment Setup

1. **Set production environment variables**
   ```env
   DEBUG=0
   SECRET_KEY=your-production-secret-key
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

2. **Use production database and Redis**
   ```env
   DB_HOST=your-production-db-host
   REDIS_URL=your-production-redis-url
   ```

3. **Configure static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

### Docker Production

```yaml
# docker-compose.prod.yml
version: '3.9'
services:
  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    environment:
      - DEBUG=0
    # ... other production configurations
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Run tests**
   ```bash
   docker-compose exec web python manage.py test
   ```
5. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
6. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

## 📝 Development Guidelines

- Follow PEP 8 style guide for Python code
- Write tests for new features
- Update documentation when adding new features
- Use meaningful commit messages
- Ensure all tests pass before submitting PRs

## 🐛 Troubleshooting

### Common Issues

**Database connection errors**
```bash
docker-compose down
docker-compose up --build
```

**Permission errors with media files**
```bash
sudo chown -R $USER:$USER media/
```

**Translation not appearing**
```bash
docker-compose exec web python manage.py compilemessages
```

### Logs

View application logs:
```bash
docker-compose logs web
docker-compose logs db
docker-compose logs redis
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

**RevLine** - Simplifying automotive parts shopping with smart compatibility and global reach.
