from dotenv import load_dotenv
from sqlalchemy import func
load_dotenv()

import os
import time
import uuid
import requests
import yaml
from datetime import timedelta
from fpdf import FPDF
from flask_mail import Message
from celery import Celery
from celery.utils.log import get_task_logger
from main import app, mail
from models import db, ServiceRequest, Professional, Customer

# YAML Schedule Loader file will be loading here
def load_custom_schedule(yaml_filename="servigo_scheduler.yaml"):

    base_dir = os.path.abspath(os.path.dirname(__file__))
    config_path = os.path.join(base_dir, yaml_filename)
    with open(config_path, "r") as stream:
        config = yaml.safe_load(stream)
    
    ops = config.get("operations", {})
    schedule_dict = {}
    try:
        from celery.schedules import crontab
    except ImportError:
        raise ImportError("Celery's crontab is required for cron scheduling.")
    
    for op_key, details in ops.items():
        func_identifier = details.get("operation")
        time_conf = details.get("time", {})
        retry_conf = details.get("retry", {})
        mode = time_conf.get("mode", "interval")
        if mode == "interval":
            secs = time_conf.get("interval_sec", 60)
            sched_value = timedelta(seconds=secs)
        elif mode == "cron":
            sched_value = crontab(
                minute=time_conf.get("minute", "*"),
                hour=time_conf.get("hour", "*"),
                day_of_month=time_conf.get("day_of_month", "*"),
                month_of_year=time_conf.get("month_of_year", "*"),
                day_of_week=time_conf.get("day_of_week", "*")
            )
        else:
            sched_value = timedelta(seconds=60)
        
        schedule_dict[op_key] = {
            "task": func_identifier,
            "schedule": sched_value,
            "options": {"max_retries": retry_conf.get("count", 1)}
        }
    return schedule_dict

# Seting up celery
celery_app = Celery(app.import_name, broker=app.config.get("CELERY_BROKER_URL", "redis://localhost:6379/0"))
celery_app.conf.result_backend = app.config.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
celery_app.conf.update({
    "imports": app.config.get("CELERY_IMPORTS", ["new_tasks"]),
    "beat_schedule": load_custom_schedule("servigo_scheduler.yaml")
})
logger = get_task_logger(__name__)


# Creating PDF Report to export completed service requests
def create_pdf_report(records, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Completed Service Requests Report", ln=True, align="C")
    pdf.ln(5)
    for rec in records:
        pdf.cell(0, 10, f"Service: {rec.service_id} | Customer: {rec.customer_id} | Pro: {rec.professional_id}", ln=True)
        req_date = rec.request_date.strftime("%Y-%m-%d %H:%M:%S") if rec.request_date else "N/A"
        comp_date = rec.completion_date.strftime("%Y-%m-%d %H:%M:%S") if rec.completion_date else "N/A"
        pdf.cell(0, 10, f"Requested: {req_date} | Completed: {comp_date}", ln=True)
        pdf.multi_cell(0, 10, f"Remarks: {rec.remarks or 'None'}")
        pdf.ln(5)
    pdf.output(output_path)
    return output_path

#  Exporting Completed Services Report in the pdf form
@celery_app.task(name="new_tasks.export_completed_services", bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def export_completed_services(self):
    with app.app_context():
        try:
            logger.info("Starting export of completed services...")
            completed_recs = ServiceRequest.query.filter(ServiceRequest.status == "COMPLETED").all()
            unique_base = f"completed_{uuid.uuid4().hex}"
            storage_dir = app.config.get("REPORTS_STORAGE", os.getcwd())
            csv_path = os.path.join(storage_dir, unique_base + ".csv")
            pdf_path = os.path.join(storage_dir, unique_base + ".pdf")
            # create_csv_file(completed_recs, csv_path)
            create_pdf_report(completed_recs, pdf_path)
            logger.info("Export successful. CSV: %s, PDF: %s", csv_path, pdf_path)
            return {"csv": csv_path, "pdf": pdf_path}
        except Exception as e:
            logger.error("Error during export: %s", e)
            raise self.retry(exc=e)

# Sending Webhook Notification to gchat
def send_webhook_notification(prof):
    webhook_url = ("https://chat.googleapis.com/v1/spaces/AAAAzl9y7FQ/messages?"
                   "key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=GHp586QhIL_og0rtD7DhegPQGFuELZMYzwhjx3Z51QE")
    payload = {"text": f"👋 Hi {prof.full_name}, you have pending service requests. Please check your dashboard."}
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        logger.info("Webhook sent to %s; status: %s", prof.full_name, response.status_code)
    except Exception as ex:
        logger.warning("Failed to send webhook to %s: %s", prof.full_name, ex)

# Notifying Professionals of Pending Requests 
@celery_app.task(name="new_tasks.notify_pending", bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def notify_pending(self):
    with app.app_context():
        try:
            logger.info("Checking for pending service requests...")
            pending_recs = ServiceRequest.query.filter(ServiceRequest.status == "REQUESTED").all()
            pro_ids = {rec.professional_id for rec in pending_recs if rec.professional_id}
            professionals = Professional.query.filter(Professional.id.in_(pro_ids)).all()
            for prof in professionals:
                send_webhook_notification(prof)
            logger.info("Notified %d professionals.", len(professionals))
            return f"Notified {len(professionals)} professionals."
        except Exception as err:
            logger.error("Error in notify_pending: %s", err)
            raise self.retry(exc=err)



def generate_summary_html(customer, service_counters, request_details_html, payment_summary):
    html_content = f"""
    <html>
      <head>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 20px; }}
          h2 {{ text-align: center; }}
          .summary-section {{ margin-top: 20px; }}
          table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
          th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
          th {{ background-color: #f2f2f2; }}
        </style>
      </head>
      <body>
        <h2>Hello {customer.full_name}, here is your Monthly Activity Report</h2>

        <div class="summary-section">
          <h3>Service Summary</h3>
          <ul>
            <li>Requested: {service_counters.get('requested', 0)}</li>
            <li>Accepted: {service_counters.get('accepted', 0)}</li>
            <li>Work Done: {service_counters.get('work_done', 0)}</li>
            <li>Completed: {service_counters.get('finalized_requests', 0)}</li>
          </ul>
        </div>

        <div class="summary-section">
          <h3>Service Request Details</h3>
          {request_details_html}
        </div>

        <div class="summary-section">
          <h3>Payment Summary</h3>
          <ul>{payment_summary}</ul>
        </div>

        <hr>
        <p style="font-size:12px;color:#888;">This is an automated monthly report from ServiGo.</p>
      </body>
    </html>
    """
    return html_content


# Dispatching Customer Summary Report as html Email -
@celery_app.task(name="new_tasks.dispatch_customer_summary", bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def dispatch_customer_summary(self):
    with app.app_context():
        try:
            logger.info("Generating customer summary reports...")
            customers = Customer.query.all()
            if not customers:
                logger.warning("No customers found.")
                return "No customers available."

            fallback_email = "vikasrathore.works@gmail.com"

            try:
                with mail.connect() as connection:
                    for user in customers:
                        service_counters = {
                            "requested": ServiceRequest.query.filter_by(customer_id=user.id, status="REQUESTED").count(),
                            "accepted": ServiceRequest.query.filter_by(customer_id=user.id, status="ACCEPTED").count(),
                            "work_done": ServiceRequest.query.filter_by(customer_id=user.id, status="WORK_DONE").count(),
                            "finalized_requests": ServiceRequest.query.filter_by(customer_id=user.id, status="COMPLETED").count()
                        }

                        requests = ServiceRequest.query.filter(
                            ServiceRequest.customer_id == user.id,
                            ServiceRequest.status.in_(["REQUESTED", "ACCEPTED", "WORK_DONE", "COMPLETED"])
                        ).all()

                        request_rows = ""
                        for req in requests:
                            professional = req.professional  
                            prof_name = getattr(professional, 'full_name', 'N/A')
                            prof_zip = getattr(professional, 'zip_code', 'N/A')
                            prof_addr = getattr(professional, 'address', 'N/A')
                            request_rows += f"""
                                <tr>
                                    <td>{req.status}</td>
                                    <td>{prof_name}</td>
                                    <td>{prof_zip}</td>
                                    <td>{prof_addr}</td>
                                </tr>
                            """

                        request_details_html = f"""
                        <table>
                        <tr>
                            <th>Status</th>
                            <th>Professional Name</th>
                            <th>Zip Code</th>
                            <th>Address</th>
                        </tr>
                        {request_rows or '<tr><td colspan="4">No service data available.</td></tr>'}
                        </table>
                        """

                        # Payment Summary to showcase customer
                        payments = db.session.query(
                            ServiceRequest.payment_status, func.count(ServiceRequest.id)
                        ).filter_by(customer_id=user.id).group_by(ServiceRequest.payment_status).all()

                        payment_summary = "".join(
                            f"<li>{status or 'Unknown'}: {count}</li>" for status, count in payments
                        ) or "<li>No payment data available.</li>"

                    
                        html_content = generate_summary_html(user, service_counters, request_details_html, payment_summary)


                        # Sending Email to customers
                        msg = Message(
                            subject=f"Monthly Service Report for {user.full_name}",
                            recipients=[getattr(user, "email", fallback_email)]
                        )
                        msg.html = html_content

                        if app.config.get("MAIL_SUPPRESS_SEND"):
                            logger.info("MAIL_SUPPRESS_SEND is True. Simulated sending email to %s", user.full_name)
                        else:
                            connection.send(msg)
                            logger.info("Summary email sent to %s", user.full_name)
                        time.sleep(1)

                logger.info("All customer summary reports has been dispatched.")
                return "Customer summaries dispatched."
            except ConnectionRefusedError as e:
                            logger.warning("SMTP server is not available: %s", e)
                            raise self.retry(exc=e)
        except Exception as exc:
            logger.error("Error dispatching customer summaries: %s", exc)
            raise self.retry(exc=exc)
