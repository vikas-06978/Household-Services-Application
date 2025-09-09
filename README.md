# Household Services Application

The Household Services Application is a full-stack web platform for booking and managing home services like cleaning, repairs, and tuition. It supports role-based access for Admins, Customers, and Professionals. The system includes features like subscriptions, portfolio uploads, reporting, and background task handling using Celery and Redis.

---

## Features

- Role-based dashboards (Admin, Customer, Professional)
- Complete service request lifecycle with real-time status updates
- Customer subscription model with premium-only features
- Professional portfolio uploads (PDF)
- HTML email reports sent monthly to customers via Mailhog
- Daily Google Chat notifications to professionals for pending service requests
- Admin can export PDF reports of completed services
- PDF reports stored locally and available for download
- Clean and responsive user interface with light/dark mode support
- Asynchronous background processing using Celery and Redis

---

## Tech Stack

**Frontend:** Vue.js, Bootstrap  
**Backend:** Flask, SQLite, SQLAlchemy  
**Asynchronous Tasks:** Celery, Redis  
**Email Service:** Flask-Mail with Mailhog (for local testing)  
**PDF Generation:** FPDF  
**Deployment:** Localhost

---

## Project Structure

The project is divided into two main parts – the backend (Flask + Celery) and the frontend (Vue.js). The backend takes care of all the APIs, background tasks, and data handling, while the frontend focuses on the user interface. Here’s a quick breakdown:
Backend (Flask)

    main.py – Entry point of the backend, where the Flask app starts.

    routes.py – Contains all API routes for different functionalities.

    models.py – Database models that define how the data is structured.

    tasks.py – Celery tasks for background jobs like scheduling and notifications.

    config.py – Configuration file for environment, database, and other settings.

    servigo_scheduler.yaml – Scheduler file for automating recurring jobs.

    uploads/ – Stores user portfolio files (like documents or images).

    reports/ – Stores system-generated PDF reports.

Frontend (Vue.js)

    public/ – Holds static files (like base HTML, logos, etc.).

    src/ – Core Vue app files.

        components/ – Reusable Vue components for the UI.

        assets/ – Frontend assets like stylesheets and images.

Project Root

    22f1001805_household_Report.pdf – Project report for reference/academic submission.

    package.json – Lists the dependencies and scripts for the frontend.

    package-lock.json – Ensures version consistency for dependencies.

    README.md – Documentation file with project details.



---

## How to Run the Project

### Frontend (Vue.js)

1. Open terminal and run:
```bash
cd frontend
npm install
npm run serve

Visit the frontend at: http://localhost:8080

cd backend
python main.py

Flask backend runs at: http://localhost:5000

Redis Server
Start the Redis server before using Celery:
sudo service redis-server start

Celery Worker
Run the Celery worker to process background tasks:
cd backend
celery -A tasks.celery_app worker --loglevel=info

Celery Beat
Start the scheduler to run periodic tasks:
cd backend
celery -A tasks.celery_app beat --loglevel=info

Mailhog (Local Email Viewer)
Start Mailhog and visit:
http://localhost:8025

```

## Key Functionalities
- Monthly HTML Email Reports
- Customers receive a monthly summary email styled with HTML
- Includes the number of services used, payments made, and subscription activity
- Emails are sent using Flask-Mail through Celery
- Viewed via Mailhog (local environment)
- Daily Google Chat Notifications
- Every day, professionals with pending service requests receive a message via Google Chat
- Implemented using Google Chat Webhook and Celery Beat
- Keeps professionals updated without opening the app
- Admin PDF Export
- Admins can export a detailed PDF report of completed services
- Includes service name, status, assigned professional, customer, and reviews
- PDFs are stored in the backend/reports/ folder for download


## Notes
- This project does not use a virtual environment or requirements.txt. Install dependencies manually.
- SQLite is used for local development.
- Portfolio PDFs are stored under uploads/
- Monthly reports are generated and saved under reports/
- Celery Beat scheduling is defined in servigo_scheduler.yaml

