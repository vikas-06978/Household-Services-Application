from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import enum
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


# Setting up database and encryption
db = SQLAlchemy()
bcrypt = Bcrypt()

# Different roles users can have
class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"
    PROFESSIONAL = "PROFESSIONAL"

# All types of service requests statuses
class RequestStatus(enum.Enum):
    REQUESTED = "REQUESTED"
    ACCEPTED = "ACCEPTED"
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    WORK_DONE = "WORK_DONE"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    

# Payment status options
class PaymentStatus(enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# Main User model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.CUSTOMER.name)
    is_active = db.Column(db.Boolean, default=True)
    is_blocked = db.Column(db.Boolean, default=False)
    registered_on = db.Column(db.DateTime, default=datetime.now)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        print(f"Password hash set successfully for user '{self.username}'.")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} - Role: {self.role}>"


# Professional user details
class Professional(db.Model):
    __tablename__ = 'professionals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    experience_years = db.Column(db.Integer, nullable=False)
    portfolio_link = db.Column(db.String(255))
    average_rating = db.Column(db.Float, default=0.0)
    zip_code = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<Professional {self.full_name} - {self.service_type}>"


# Customer to store customer details
class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    subscription_status = db.Column(db.String(20), default="inactive")  
    subscription_expiry = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Customer {self.full_name} - ZIP: {self.zip_code}>"


# Details about services offered
class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Service {self.title} - ${self.price}>"



# Service Request table for storing request send by customers
class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, ForeignKey('services.id'), nullable=False)  
    customer_id = db.Column(db.Integer, ForeignKey('customers.id'), nullable=False)  
    professional_id = db.Column(db.Integer, ForeignKey('professionals.id'), nullable=True)  

    request_date = db.Column(db.DateTime, default=datetime.now)
    completion_date = db.Column(db.DateTime, nullable=True)
    desired_service_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum(RequestStatus), default=RequestStatus.REQUESTED.name)
    remarks = db.Column(db.String(200))
    rating = db.Column(db.Float, nullable=True)
    payment_status = db.Column(db.String(20), default="PENDING")
    commission_amount = db.Column(db.Float, nullable=True)


    service = relationship("Service", backref="service_requests")  
    customer = relationship("Customer", backref="service_requests")  
    professional = relationship("Professional", backref="service_requests")  

    def __repr__(self):
        return f"<ServiceRequest {self.id} - Status: {self.status}>"
    
# This table stores payment details
class SubscriptionPayment(db.Model):
    __tablename__ = 'subscription_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.now)

# Pending user table for storing pending users
class PendingUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    role = db.Column(db.Enum(UserRole), nullable=False)  
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)

    # Fields for Professionals Only
    service_type = db.Column(db.String(255), nullable=True)  
    experience_years = db.Column(db.Integer, nullable=True)  
    portfolio_link = db.Column(db.String(255), nullable=True)  
    average_rating = db.Column(db.Float, default=0.0, nullable=True)  

    request_date = db.Column(db.DateTime, default=datetime.now)  


# No need to sign up admin creating here
def create_admin_user():
    """Creating a default admin user if it doesn't exist"""
    with db.session.begin(): 
        admin_user = User.query.filter_by(username='admin', role=UserRole.ADMIN.name).first()
        if not admin_user:
            try:
                admin_user = User(
                    username='admin',
                    email="admin@example.com",
                    role=UserRole.ADMIN.name,
                    is_active=True,
                    password_hash=bcrypt.generate_password_hash("admin123").decode("utf-8")
                )
                db.session.add(admin_user)
                print("Admin user created successfully! Use username: 'admin' and password: 'admin123'")
            except Exception as e:
                db.session.rollback()
                print(f"Can't create admin some error has occured {e}")
        else:
            print("Admin user already exists.")
