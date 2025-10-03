# WhatsApp Group Analytics - Deployment Guide

This guide provides comprehensive instructions for deploying the WhatsApp Group Analytics application to various platforms.

## Prerequisites

1. A GitHub account
2. A deployment platform account (Render, Heroku, or Docker hosting)
3. A Gemini API key (https://ai.google.dev/)

## Deployment Options

### Option 1: Render Deployment (Recommended)

1. Fork this repository to your GitHub account
2. Log in to your Render dashboard
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Configure the service:
   - Name: whatsapp-analytics
   - Region: Choose the region closest to your users
   - Branch: main (or your preferred branch)
   - Root Directory: whatsapp_django
   - Environment: Python
   - Build Command: `./build.sh`
   - Start Command: `gunicorn myproject.wsgi_render:application`

6. Add environment variables in the "Advanced" section:
   - PYTHON_VERSION: 3.11.0
   - DJANGO_SETTINGS_MODULE: myproject.settings_render
   - SECRET_KEY: Generate a secure secret key
   - GEMINI_API_KEY: Your Gemini API key
   - DEBUG: False

7. Click "Create Web Service"

### Option 2: Heroku Deployment

1. Fork this repository to your GitHub account
2. Log in to your Heroku dashboard
3. Click "New" → "Create new app"
4. Choose an app name and region
5. In the "Deploy" tab, connect your GitHub repository
6. Enable automatic deploys or deploy manually
7. In the "Settings" tab, add buildpacks:
   - heroku/python
8. In the "Settings" tab, add environment variables:
   - SECRET_KEY: Generate a secure secret key
   - GEMINI_API_KEY: Your Gemini API key
   - DEBUG: False

### Option 3: Docker Deployment

1. Build the Docker image:
   ```
   docker build -t whatsapp-analytics .
   ```

2. Run the container:
   ```
   docker run -p 8000:8000 -e SECRET_KEY="your-secret-key" -e GEMINI_API_KEY="your-gemini-api-key" whatsapp-analytics
   ```

3. Access the application at http://localhost:8000

## Environment Variables

The following environment variables need to be set:

- `SECRET_KEY`: Django secret key (generate a secure one)
- `GEMINI_API_KEY`: Your Gemini API key for AI features
- `DEBUG`: Set to `False` for production
- `DATABASE_URL`: For production, consider using a PostgreSQL database

## Health Check Endpoint

A `/health/` endpoint is available to verify application status:
- Returns JSON with status information
- Useful for monitoring and uptime checks
- Accessible at `/health/` path

## Troubleshooting

If you encounter issues:

1. Check the logs in your deployment platform dashboard
2. Ensure all environment variables are correctly set
3. Verify that your Gemini API key is valid and has sufficient quota
4. Check that the build process completes successfully

## Support

For additional support, refer to the documentation of your deployment platform:
- Render: https://render.com/docs
- Heroku: https://devcenter.heroku.com/
- Docker: https://docs.docker.com/