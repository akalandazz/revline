# RevLine

RevLine is an online car parts shop focused on vehicle compatibility. Our MVP features a searchable product catalog, a smart compatibility system to prevent wrong orders, and a seamless checkout. It's mobile-responsive, with user accounts for easy order tracking. Our mission is to simplify buying parts.

## Multilingual Support

RevLine supports multiple languages for a global audience:

- **English** (default) - `http://revline.com/`
- **Spanish** - `http://revline.com/es/`
- **Georgian** - `http://revline.com/ka/`

Users can switch languages through the dropdown menu in the navigation bar. All interface elements, including navigation, product descriptions, and call-to-action buttons, are fully translated.

### Managing Translations

To update translations or add new languages:

1. Generate message files: `python manage.py makemessages -l <language_code>`
2. Edit translations in `locale/<language_code>/LC_MESSAGES/django.po`
3. Compile messages: `python manage.py compilemessages`

*Note: Run these commands inside the Docker container using `docker-compose exec web <command>`*
