# WhatsApp Django Analytics Project - Setup Guide

This project analyzes WhatsApp chat exports and provides detailed insights, summaries, and analytics.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

**For Windows:**
```bash
# Double-click setup.bat or run in command prompt:
setup.bat
```

**For Linux/Mac:**
```bash
python3 setup.py
```

### Option 2: Manual Setup

1. **Install Python 3.8+**
   - Download from [python.org](https://python.org)
   - Make sure to check "Add Python to PATH" during installation

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Activate Virtual Environment**
   - **Windows:** `venv\Scripts\activate`
   - **Linux/Mac:** `source venv/bin/activate`

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run Django Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Start the Server**
   ```bash
   python manage.py runserver
   ```

7. **Open in Browser**
   - Go to: http://127.0.0.1:8000

## 📁 Project Structure

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
├── setup.py               # Automated setup script
└── manage.py              # Django management script
```

## 🔧 Features

### Enhanced Summary Generation
- **Brief Reports**: Detailed analysis for short periods (7 days or less)
- **Weekly Reports**: Comprehensive weekly breakdowns with actual quotes
- **User Activity**: Individual participant analysis
- **Sentiment Analysis**: Emotional tone of conversations
- **Business Metrics**: Activity patterns and engagement

### Key Improvements for Short Periods
When analyzing 7 days or less, the system provides:
- **Exact Quotes**: Real message content in original language
- **Specific Details**: Names, dates, times, locations mentioned
- **Action Items**: Clear next steps and decisions
- **Resource Tracking**: Files, links, and documents shared
- **Question Analysis**: Questions asked and answers provided

## 📊 Usage

1. **Upload Chat Files**
   - Export WhatsApp chat as .txt file
   - Upload through the web interface

2. **Select Analysis Type**
   - Brief Summary: Quick overview
   - Weekly Summary: Detailed weekly breakdown
   - User Analysis: Individual participant insights
   - Sentiment Analysis: Emotional analysis

3. **Set Date Range**
   - Choose specific dates for analysis
   - Short periods (≤7 days) get enhanced detailed analysis

## 🛠️ Configuration

### Environment Variables (.env file)
```env
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Optional: Google Gemini API for enhanced AI features
GEMINI_API_KEY=your-gemini-api-key
```

### API Keys (Optional)
- **Google Gemini API**: For enhanced AI-powered summaries
  - Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
  - Add to .env file as `GEMINI_API_KEY=your-key`

## 🐛 Troubleshooting

### Common Issues

1. **Python not found**
   - Install Python 3.8+ from python.org
   - Make sure Python is added to PATH

2. **Permission errors**
   - Run command prompt as administrator (Windows)
   - Use `sudo` for system-wide installs (Linux/Mac)

3. **Port already in use**
   - Change port: `python manage.py runserver 8001`
   - Or kill process using port 8000

4. **Database errors**
   - Delete `db.sqlite3` and run migrations again
   - Check file permissions in project directory

### Dependencies Issues
If you encounter dependency conflicts:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 📈 Performance Tips

1. **Large Chat Files**
   - System handles up to 50,000 messages efficiently
   - For larger files, consider splitting by date ranges

2. **API Limits**
   - Gemini API has rate limits
   - System includes fallback analysis when API is unavailable

3. **Memory Usage**
   - Large files may require more RAM
   - Consider analyzing shorter date ranges for very large chats

## 🔒 Security Notes

- Default settings are for development only
- Change SECRET_KEY for production
- Set DEBUG=False for production
- Configure proper ALLOWED_HOSTS for production

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all dependencies are installed correctly
3. Check Django logs for specific error messages
4. Ensure Python version is 3.8 or higher

## 🎯 What's New

### Enhanced Analysis for Short Periods
- **Detailed Quotes**: Actual message content with context
- **Specific Insights**: Names, dates, and locations mentioned
- **Action Items**: Clear next steps and decisions
- **Resource Tracking**: Files and links shared
- **Question Analysis**: Questions and answers

### Improved User Experience
- Better formatting for reports
- More actionable insights
- Enhanced readability
- Specific recommendations

---

**Happy Analyzing! 🎉**

