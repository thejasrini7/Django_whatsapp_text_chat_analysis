# WhatsApp Django Project - Setup and Running Guide

## Prerequisites
- Python 3.13 or higher
- pip (Python package installer)

## Setup Instructions

### 1. Install Required Dependencies
The project requires several Python packages to run properly. Install them using:

```bash
pip install Django python-dotenv whitenoise requests google-generativeai
```

### 2. Database Migration
Navigate to the project directory and run migrations:

```bash
cd c:\Users\Srika\Downloads\whatsapp_django\whatsapp_django
python manage.py migrate
```

### 3. Create a Superuser (Optional)
To access the Django admin interface:

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user.

### 4. Running the Project
Start the development server:

```bash
python manage.py runserver
```

Or simply double-click the `run_project.bat` file.

### 5. Access the Application
Open your web browser and go to:
- Main Application: http://127.0.0.1:8000/
- Admin Interface: http://127.0.0.1:8000/admin/
- Health Check: http://127.0.0.1:8000/health/

## Features
- WhatsApp chat analysis and visualization
- Group event tracking
- Sentiment analysis
- Study report generation
- Export functionality

## Troubleshooting
1. If you encounter import errors, make sure all dependencies are installed
2. If the database is corrupted, delete `db.sqlite3` and re-run migrations
3. For Gemini API errors, ensure you have a valid API key in your `.env` file

## Project Structure
- `chatapp/` - Main application with views, models, and analysis logic
- `media/chat_files/` - Sample WhatsApp chat files
- `templates/chatapp/` - HTML templates
- `static/` - CSS and JavaScript files