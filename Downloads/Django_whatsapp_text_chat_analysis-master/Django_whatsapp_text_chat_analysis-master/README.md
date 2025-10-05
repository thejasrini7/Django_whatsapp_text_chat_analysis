# WhatsApp Chat Analysis Django Application

This Django application analyzes WhatsApp chat exports and provides detailed insights, summaries, and analytics.

## Features

- WhatsApp chat analysis and visualization
- Group event tracking
- Sentiment analysis
- Study report generation
- Export functionality
- AI-powered summaries using Google Gemini

## Deployment on Render

This application is configured for deployment on Render with the following settings:

### Environment Variables

Set these environment variables in your Render dashboard:

```
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=your-database-url  # For PostgreSQL on Render
ALLOWED_HOSTS=your-app-name.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com
GEMINI_API_KEY=your-gemini-api-key-here  # Optional for AI features
```

### Build Command

```
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

### Start Command

```
gunicorn myproject.wsgi:application --workers 2 --max-requests 1000 --max-requests-jitter 100 --bind 0.0.0.0:$PORT
```

## Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/thejasrini7/Django_whatsapp_text_chat_analysis.git
   cd Django_whatsapp_text_chat_analysis
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
whatsapp_django/
├── chatapp/                 # Main Django app
│   ├── models.py           # Database models
│   ├── views.py            # API endpoints and views
│   ├── summary_generator.py # AI-powered summary generation
│   ├── sentiment_analyzer.py # Sentiment analysis
│   ├── business_metrics.py  # Activity metrics
│   └── templates/          # HTML templates
├── myproject/              # Django project settings
├── media/                  # Uploaded chat files
├── static/                 # Static files (CSS, JS)
├── requirements.txt        # Python dependencies
└── manage.py              # Django management script
```

## API Endpoints

- `/` - Main application interface
- `/api/groups/` - Get list of chat groups
- `/api/summarize/` - Generate chat summary
- `/admin/` - Django admin interface
- `/health/` - Health check endpoint

## Configuration Files

- `myproject/settings.py` - Local development settings
- `myproject/settings_render.py` - Render deployment settings
- `myproject/wsgi.py` - WSGI configuration for deployment
- `gunicorn.conf.py` - Gunicorn configuration

## Requirements

- Python 3.8+
- Django 5.2+
- PostgreSQL (for production) or SQLite (for development)

## Troubleshooting

1. **Database errors**: Run `python manage.py migrate` to ensure database is set up
2. **Static files not loading**: Run `python manage.py collectstatic` 
3. **Gemini API errors**: Ensure `GEMINI_API_KEY` is set in environment variables
4. **Port binding issues**: Make sure to bind to `0.0.0.0:$PORT` on Render

## License

This project is open source and available under the MIT License.