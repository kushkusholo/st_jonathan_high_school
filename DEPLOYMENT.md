# 🌐 Deployment Guide

## Deploying St. Jonathan High School Chatbot Online

This guide explains how to deploy the chatbot so parents can access it from anywhere on the internet.

---

## Option 1: Heroku (FREE - Recommended for Beginners)

### Requirements
- Heroku account (free at https://www.heroku.com/)
- Git installed (https://git-scm.com/)

### Steps

**1. Create Heroku Account**
- Go to https://www.heroku.com/
- Sign up for free account
- Verify email

**2. Install Heroku CLI**
- Download from https://devcenter.heroku.com/articles/heroku-cli
- Install and restart terminal

**3. Prepare Project**

Add a `Procfile` in root directory:
```
web: gunicorn app:app
```

Update `requirements.txt`:
```
Flask==3.0.2
Werkzeug==3.0.2
gunicorn==20.1.0
```

Modify `app.py` last line:
```python
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
```

**4. Deploy**

```bash
# Login to Heroku
heroku login

# Initialize git repository
git init
git add .
git commit -m "Initial commit"

# Create Heroku app
heroku create your-app-name

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

**5. Access**
Your app will be available at: `https://your-app-name.herokuapp.com`

### Note
- Heroku free tier goes to sleep after 30 minutes of inactivity
- For production, consider paid plans
- Free tier is great for testing

---

## Option 2: PythonAnywhere (FREE - Great for Schools)

### Requirements
- PythonAnywhere account (free at https://www.pythonanywhere.com/)
- Your project files uploaded

### Step-by-Step Deployment Guide

**1. Create PythonAnywhere Account**
- Go to https://www.pythonanywhere.com/
- Click "Pricing & signup" → "Create a Beginner account" (FREE)
- Fill in your details and verify email
- Login to your dashboard

**2. Upload Your Project Files**
- In PythonAnywhere dashboard, go to **Files** tab
- Click **"Upload a file"** or **"Open bash console here"**
- Upload your entire `school_chatbot` folder
- Or use git clone if you prefer:
```bash
git clone https://github.com/yourusername/your-repo-name.git
```

**3. Set Up Virtual Environment**
- Go to **Consoles** tab → **"Bash"**
- Create and activate virtual environment:
```bash
cd school_chatbot
python3.10 -m venv venv
source venv/bin/activate
```

**4. Install Dependencies**
```bash
pip install -r requirements.txt
```

**5. Set Up Database**
- PythonAnywhere uses SQLite by default (perfect for our app)
- Run this to create the database:
```bash
python app.py
```
- Press Ctrl+C after it starts (this creates the database)
- The database file `school.db` will be created

**6. Configure Environment Variables**
- In PythonAnywhere dashboard, go to **Variables** section
- Add these environment variables:
```
SECRET_KEY=your-secure-random-secret-here
ADMIN_PASSWORD=your-admin-password
DEBUG=False
OPENAI_API_KEY=your-openai-key-if-using-ai
TWILIO_ACCOUNT_SID=your-twilio-sid-if-using-whatsapp
TWILIO_AUTH_TOKEN=your-twilio-token-if-using-whatsapp
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890
```

**7. Create Web App**
- Go to **Web** tab
- Click **"Add a new web app"**
- Choose **"Flask"**
- Select **Python 3.10**
- Set **"/home/yourusername/school_chatbot"** as source code directory
- Set **"app:app"** as application

**8. Configure WSGI File**
- In the Web tab, click on the **WSGI configuration file** link
- Replace the content with:
```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/school_chatbot'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['SECRET_KEY'] = 'your-secure-random-secret-here'
os.environ['ADMIN_PASSWORD'] = 'your-admin-password'
os.environ['DEBUG'] = 'False'
# Add other environment variables as needed

# Import your Flask app
from app import app as application
```

**9. Set Up Static Files**
- In Web tab, scroll to **Static files** section
- Add static file mapping:
  - URL: `/static/`
  - Directory: `/home/yourusername/school_chatbot/static`

**10. Reload Web App**
- Click the **green "Reload" button** in Web tab
- Your app should now be live!

**11. Access Your App**
- Your app will be available at: `https://yourusername.pythonanywhere.com`
- Test all features:
  - Main chatbot: `https://yourusername.pythonanywhere.com/`
  - Admin login: `https://yourusername.pythonanywhere.com/admin/login`
  - User registration: `https://yourusername.pythonanywhere.com/auth/register`

### PythonAnywhere Specific Notes

**Free Tier Limitations:**
- 512MB storage
- CPU usage limits
- No custom domains (use pythonanywhere.com subdomain)

**Database Setup:**
- SQLite works perfectly on PythonAnywhere
- Database persists between reloads
- No additional configuration needed

**File Uploads:**
- Use the web interface for small files
- Use SCP/SFTP for large files
- Or use git for version control

**Environment Variables:**
- Set in the Web tab → Variables section
- Or in WSGI file as shown above
- Never hardcode sensitive data

**Logs and Debugging:**
- Check **Web** tab → **Server log** for errors
- Use **Consoles** tab → **Bash** to test commands
- Run `python app.py` in console to test locally

**Upgrading to Paid:**
- If you need more resources, upgrade to paid plans
- Starts at $5/month for more storage and CPU
- Allows custom domains

### Troubleshooting PythonAnywhere

| Issue | Solution |
|-------|----------|
| Import errors | Check virtual environment activation |
| Database errors | Ensure database file permissions |
| Static files not loading | Verify static file mappings |
| 500 errors | Check server logs in Web tab |
| App not starting | Verify WSGI configuration |
| Environment variables | Set in Web tab Variables section |

### Backup Strategy for PythonAnywhere

- Use git for version control
- Download database file regularly
- Export chat logs periodically
- Keep environment variables documented

### Performance Tips

- PythonAnywhere free tier is sufficient for school use
- Monitor CPU usage in dashboard
- Clear old logs to save space
- Use efficient database queries

---

## Option 3: Google Cloud (PAID - More Reliable)

### Requirements
- Google Cloud account
- Credit card for billing
- Cloud SDK installed

### Steps

**1. Create Project**
```bash
gcloud projects create st-jonathan-chatbot
gcloud config set project st-jonathan-chatbot
```

**2. Update app.py**
```python
# At the top, add this after imports
import os
if not os.environ.get('DEBUG'):
    DEBUG = False
```

**3. Create app.yaml**
```yaml
runtime: python39
entrypoint: gunicorn -b :$PORT app:app
env: standard

env_variables:
  DEBUG: "False"
```

**4. Deploy**
```bash
gcloud app deploy
```

**5. Access**
Your app will be at: `https://st-jonathan-chatbot.appspot.com`

---

## Option 4: AWS Elastic Beanstalk (MODERATE - Scalable)

### Requirements
- AWS account
- AWS CLI installed

### Steps (Brief)
```bash
# Initialize Elastic Beanstalk
eb init -p python-3.9 st-jonathan-chatbot

# Create environment
eb create st-jonathan-env

# Deploy
eb deploy

# Open in browser
eb open
```

---

## Option 5: DigitalOcean Droplet (MODERATE - Full Control)

### Requirements
- DigitalOcean account
- SSH knowledge
- $5+/month

### Brief Setup
1. Create Ubuntu Droplet
2. SSH into server
3. Install Python, Git, Nginx
4. Clone repository
5. Configure Gunicorn
6. Set up Nginx reverse proxy
7. Configure SSL/TLS (free with Let's Encrypt)

---

## Important Considerations Before Deploying

### Security

**Add Authentication:**
```python
# Simple password protection
from flask import session, render_template_string

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == os.environ.get('ADMIN_PASSWORD'):
            session['logged_in'] = True
            return redirect('/')
    return render_template('login.html')
```

**Use Environment Variables:**
```python
import os

# Load from environment, not hardcoded
SCHOOL_PHONE = os.environ.get('SCHOOL_PHONE', '+256325516717')
DEBUG_MODE = os.environ.get('DEBUG', 'False') == 'True'
```

**Add HTTPS:**
- Always use HTTPS in production
- Get free SSL from Let's Encrypt
- Most platforms include this

### Performance

- Use CDN for static files (CSS, JS)
- Enable gzip compression
- Cache frequently accessed FAQs
- Monitor server resources

### Backup

- Automated backups of FAQs
- Regular backup of chat logs
- Version control (GitHub)
- Disaster recovery plan

### Monitoring

- Set up error logging (Sentry)
- Monitor uptime (UptimeRobot)
- Track analytics (Google Analytics)
- Alert notifications

---

## Post-Deployment Checklist

- [ ] Test all chatbot features
- [ ] Verify FAQ loading
- [ ] Check school contact display
- [ ] Test on mobile devices
- [ ] Verify SSL/HTTPS works
- [ ] Check performance/load times
- [ ] Set up backups
- [ ] Configure monitoring
- [ ] Document deployment
- [ ] Share URL with parents

---

## Sharing with Parents

Once deployed, share the URL:

**Email Template:**
```
Subject: New School Communication Tool - St. Jonathan High School

Dear Parents and Guardians,

St. Jonathan High School is excited to introduce our new Parent Portal Chatbot!

Use this tool to get instant answers to frequently asked questions about:
✓ Admissions and enrollment
✓ School fees and payments
✓ Academic calendar and holidays
✓ School facilities and programs
✓ Extracurricular activities
✓ School policies

Access it here: [YOUR_DEPLOYMENT_URL]

For urgent matters, please call us directly at +256325516717

Best regards,
St. Jonathan High School Administration
```

---

## Troubleshooting Deployment

| Issue | Solution |
|-------|----------|
| App won't start | Check error logs, verify dependencies |
| FAQs not loading | Verify file paths, check permissions |
| Slow loading | Add caching, optimize database queries |
| 500 errors | Check server logs, verify configuration |
| HTTPS issues | Verify SSL certificate, check configuration |

---

## Cost Comparison

| Platform | Cost | Pros | Cons |
|----------|------|------|------|
| Heroku | FREE (limited) | Easy, good for testing | Goes to sleep, slower |
| PythonAnywhere | FREE (limited) | Simple setup | Limited storage |
| Google Cloud | $0-50/mo | Scalable, reliable | Requires setup |
| DigitalOcean | $5+/mo | Full control, fast | Requires Linux knowledge |
| AWS | $5-100+/mo | Enterprise-grade | Complex setup |

---

## Recommended Setup

For **St. Jonathan High School**, I recommend:

1. **Development**: Local machine (current setup)
2. **Testing**: PythonAnywhere (free, easy)
3. **Production**: DigitalOcean or AWS (reliable, scalable)

---

## Next Steps

1. Choose deployment platform
2. Follow platform-specific steps
3. Test thoroughly
4. Set up monitoring
5. Share URL with school community
6. Train administrators
7. Collect feedback
8. Iteratively improve

---

**For Support:**
- Consult platform-specific documentation
- Check deployment logs
- Contact technical support

**Need More Help?**
Visit: [Deployment Platform Documentation]

---

**Last Updated:** April 2024
