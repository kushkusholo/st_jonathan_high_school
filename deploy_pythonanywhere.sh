# PythonAnywhere Deployment Script
# Run this in PythonAnywhere Bash console

#!/bin/bash

echo "🚀 Deploying St. Jonathan High School Chatbot to PythonAnywhere"

# Navigate to project directory
cd ~/school_chatbot

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3.10 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create database if it doesn't exist
if [ ! -f "school.db" ]; then
    echo "🗄️ Creating database..."
    python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database created!')"
fi

# Set proper permissions
echo "🔒 Setting permissions..."
chmod 644 static/admission_form.txt
chmod 644 data/faqs.json
chmod 644 logs/chat_logs.json

echo "✅ Deployment preparation complete!"
echo ""
echo "Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Add a new web app (Flask, Python 3.10)"
echo "3. Set source code directory to: /home/yourusername/school_chatbot"
echo "4. Set application to: app:app"
echo "5. Configure WSGI file as shown in DEPLOYMENT.md"
echo "6. Set static files mapping: /static/ -> /home/yourusername/school_chatbot/static"
echo "7. Add environment variables in Web tab"
echo "8. Click Reload"
echo ""
echo "Your app will be at: https://yourusername.pythonanywhere.com"