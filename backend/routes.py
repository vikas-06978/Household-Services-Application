from flask import current_app
from flask import Blueprint, request, jsonify, send_file
from sqlalchemy import func
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, get_jwt_identity,verify_jwt_in_request
from models import Customer, PendingUser, Professional, RequestStatus, ServiceRequest, SubscriptionPayment, User, UserRole, db, Service

import os
import io
import json
from flask_cors import cross_origin,CORS

from datetime import datetime, timedelta
import pytz


routes = Blueprint("routes", __name__)
bcrypt = Bcrypt()

india_tz = pytz.timezone("Asia/Kolkata")

# Role-Based Access Control only authentic one can login
def role_required(role):
    """Check if the current user has the correct role."""
    current_user = json.loads(get_jwt_identity())  # Decode JSON string
    if current_user["role"] != role:
        return jsonify({"error": f"Unauthorized access. Only {role.capitalize()}s can access this page."}), 403
    return None  


# Signup Route to register
@routes.route("/api/signup", methods=["POST"])
@cross_origin()
def signup():

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    role = request.form.get("role", "customer")
    phone = request.form.get("phone")
    address = request.form.get("address")
    zip_code = request.form.get("zip_code")

    service_type = request.form.get("service_type")
    experience_years = request.form.get("experience_years")


    portfolio_filename = None
    if role.upper() == "PROFESSIONAL":
        if "portfolio_file" in request.files:
            file = request.files["portfolio_file"]
            if file and file.filename.endswith(".pdf"):
                filename = secure_filename(file.filename)
                upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")

                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                portfolio_filename = filename

            else:
                return jsonify({"message": "Invalid portfolio file."}), 400

    # Check if user already exists in users table
    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing_user:
        return jsonify({"message": "Username or email already exists. Please log in or use a different one."}), 400

    
    if not all([first_name, last_name, username, email, password, phone, address, zip_code]):
        return jsonify({"message": "All fields are required."}), 400

    try:
        new_user = User(
            username=username,
            email=email,
            password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
            role=UserRole(role),
            is_active=False  
        )
        db.session.add(new_user)
        db.session.flush()  

        new_pending_user = PendingUser(
            user_id=new_user.id,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
            zip_code=zip_code,
            role=role
        )

        # print("Received service_type:", service_type)

        # professional-specific details 
        if role == "PROFESSIONAL":
            new_pending_user.service_type = service_type
            new_pending_user.experience_years = experience_years
            new_pending_user.portfolio_link = portfolio_filename

        db.session.add(new_pending_user)
        db.session.commit()

        return jsonify({"message": "Signup successful! Pending admin approval."}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error registering user", "error": str(e)}), 500

# Login Route
@routes.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    selected_role = data.get("role")

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Username does not exist"}), 401

    if not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Incorrect password"}), 401

    if user.role.name != selected_role:
        return jsonify({"error": "Incorrect role selection. Please select the correct role."}), 401

    if user.is_blocked:
        return jsonify({"error": "Your account has been blocked. Contact support."}), 403

    if not user.is_active and user.role.name != "ADMIN":
        return jsonify({"error": "Your account is pending admin approval."}), 403

    token = create_access_token(identity=json.dumps({"id": user.id, "role": user.role.name}))
    response_data = {
        "token": token,
        "role": user.role.name,
        "username": user.username,
        "registered_on": user.registered_on.strftime("%Y-%m-%d %H:%M:%S"),
        "is_active": user.is_active,
        "is_blocked": user.is_blocked,
    }

    if user.role.name == "PROFESSIONAL":
        professional = Professional.query.filter_by(user_id=user.id).first()
        if professional:
            response_data["professional_id"] = professional.id
        else:
            response_data["professional_id"] = None
        print(" PROFESSIONAL LOGIN DETECTED!")
        print("User ID:", user.id)
        print("Professional ID:", response_data["professional_id"])

    elif user.role.name == "CUSTOMER":
        customer = Customer.query.filter_by(user_id=user.id).first()
        if customer:
            response_data["customer_id"] = customer.id
        else:
            response_data["customer_id"] = None
        print(" CUSTOMER LOGIN DETECTED!")
        print("User ID:", user.id)
        print("Customer ID:", response_data["customer_id"])

    print(" API LOGIN RESPONSE:", response_data)
    return jsonify(response_data), 200


# Secure User Details Route 
@routes.route("/api/user/<username>", methods=["GET", "OPTIONS"])
@cross_origin()
@jwt_required()
def get_user_details(username):
    if request.method == "OPTIONS":
        response = jsonify({"message": "CORS Preflight OK"})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        return response, 200

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_data = {
        "username": user.username,
        "role": user.role.name,
        "registered_on": user.registered_on.strftime("%Y-%m-%d %H:%M:%S") if user.registered_on else "N/A",
        "email" : user.email
    }

    if user.role == UserRole.CUSTOMER:
        customer = Customer.query.filter_by(user_id=user.id).first()
        if customer:
            user_data.update({
                "full_name": customer.full_name,
                "address": customer.address,
                "zip_code": customer.zip_code,
                "phone": customer.phone,
                "email":user.email,
            })

    elif user.role == UserRole.PROFESSIONAL:
        professional = Professional.query.filter_by(user_id=user.id).first()
        if professional:
            user_data.update({
                "full_name": professional.full_name,
                "service_type": professional.service_type,  
                "experience_years": professional.experience_years,
                "portfolio_link": professional.portfolio_link,
                "average_rating": professional.average_rating,
                "address": professional.address,
                "zip_code": professional.zip_code,
                "phone": professional.phone,
            })
        else:
            print(f" No professional record found for user {username}")

    return jsonify(user_data), 200


@routes.route("/api/<path:path>", methods=["OPTIONS"])
@cross_origin()
def options_handler(path):
    return jsonify({"message": "CORS preflight successful"}), 200


# Admin Routes
@routes.route("/api/admin/dashboard", methods=["GET"])
@jwt_required()
def admin_dashboard():
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error
    return jsonify({"message": "Welcome to the Admin Dashboard!"})

# Admin Search
@routes.route("/api/admin/search", methods=["GET"])
@jwt_required()
def admin_search():
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error
    return jsonify({"message": "Admin Search Page!"})

# Admin Summary
@routes.route("/api/admin/summary", methods=["GET"])
@jwt_required()
def admin_summary():
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error

    total_users = db.session.query(User).count()
    total_professionals = db.session.query(User).filter(User.role == "PROFESSIONAL").count()
    pending_requests = db.session.query(ServiceRequest).filter(ServiceRequest.status == "REQUESTED").count()

    # Revenue from commissions on completed service requests:
    total_commission = db.session.query(db.func.sum(ServiceRequest.commission_amount)) \
                         .filter(ServiceRequest.status == "COMPLETED").scalar() or 0

    # Revenue from subscription fees:
    total_subscription = db.session.query(db.func.sum(SubscriptionPayment.amount)).scalar() or 0

    total_revenue = total_commission + total_subscription

    return jsonify({
        "total_users": total_users,
        "total_professionals": total_professionals,
        "pending_requests": pending_requests,
        "total_revenue": total_revenue
    }), 200


# Customer Routes
@routes.route("/api/customer/dashboard", methods=["GET"])
@jwt_required()
def customer_dashboard():
    auth_error = role_required("CUSTOMER")
    if auth_error:
        return auth_error
    return jsonify({"message": "Welcome to the Customer Dashboard!"})

# Customer Search
@routes.route("/api/customer/search", methods=["GET"])
@jwt_required()
def customer_search():
    auth_error = role_required("CUSTOMER")
    if auth_error:
        return auth_error
    return jsonify({"message": "Customer Search Page, search what you looking for!"})

# Customer Summary
@routes.route("/api/customer/summary", methods=["GET"])
@jwt_required()
def customer_summary():
    auth_error = role_required("CUSTOMER")
    if auth_error:
        return auth_error
    return jsonify({"message": "Customer Summary Page!"})

# Professional Routes
@routes.route("/api/professional/dashboard", methods=["GET"])
@jwt_required()
def professional_dashboard():
    auth_error = role_required("PROFESSIONAL")
    if auth_error:
        return auth_error
    return jsonify({"message": "Welcome to the Professional Dashboard!"})

# Professional Search
@routes.route("/api/professional/search", methods=["GET"])
@jwt_required()
def professional_search():
    auth_error = role_required("PROFESSIONAL")
    if auth_error:
        return auth_error
    return jsonify({"message": "Professional Search Page!"})

# Professional Summary
@routes.route("/api/professional/summary", methods=["GET"])
@jwt_required()
def professional_summary():
    auth_error = role_required("PROFESSIONAL")
    if auth_error:
        return auth_error
    return jsonify({"message": "Professional Summary Page!"})

CORS(routes)  

@routes.route("/api/admin/pending_users", methods=["GET"])
@jwt_required()
def get_pending_users():
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error

    role_input = request.args.get("role")
    role = role_input.upper() if role_input else None

    print("role", role)

    if role not in ["CUSTOMER", "PROFESSIONAL", None]: 
        return jsonify({"error": "Invalid role specified"}), 400
    
    print("role",role)
    # Convert role to Enum 
    role_enum = UserRole[role.upper()] if role else None 
    print("role_enum", role_enum)

    query = PendingUser.query
    print("pending_users role",PendingUser.role == role_enum )
   
    if role_enum:
        query = query.filter(PendingUser.role == role_enum)  


    pending_users = query.all()
    # print("Pending_users", pending_users)

    
    # print(f"Fetching pending users with role: {role_enum}")
    # print(f"Users Found: {pending_users}")

    result = []
    for user in pending_users:
        user_data = {
            "id": user.id,
            "user_id": user.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "address": user.address,
            "zip_code": user.zip_code,
            "request_date": user.request_date.strftime("%Y-%m-%d %H:%M:%S"),
            "role": user.role.name  # Convert Enum to string
        }
        
        if user.role == UserRole.PROFESSIONAL:
            user_data.update({
                "service_type": user.service_type,
                "experience_years": user.experience_years,
                "portfolio_link": user.portfolio_link,
                "average_rating": user.average_rating
            })
        
        result.append(user_data)

    return jsonify(result), 200

# Approve User
@routes.route("/api/admin/approve_user/<int:pending_user_id>", methods=["POST"])
@jwt_required()
@cross_origin() 
def approve_user(pending_user_id):
    # Admin-only check
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error

    # Fetch the pending user by user_id
    pending_user = PendingUser.query.get(pending_user_id)
    if not pending_user:
        return jsonify({"error": "User not found in pending approvals"}), 404

    # Activate the main User record
    user = User.query.get(pending_user.user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.is_active = True

    # Move data to the respective table
    if pending_user.role == UserRole.CUSTOMER:
        new_customer = Customer(
            user_id=pending_user.user_id,
            full_name = pending_user.first_name + pending_user.last_name,
            phone=pending_user.phone,
            address=pending_user.address,
            zip_code=pending_user.zip_code
        )
        db.session.add(new_customer)

    elif pending_user.role == UserRole.PROFESSIONAL:
        new_professional = Professional(
            user_id=pending_user.user_id,
            full_name = pending_user.first_name + pending_user.last_name,
            address=pending_user.address,
            phone=pending_user.phone,
            zip_code=pending_user.zip_code,
            service_type=pending_user.service_type,
            experience_years=pending_user.experience_years,
            portfolio_link=pending_user.portfolio_link,
            average_rating=pending_user.average_rating
        )
        db.session.add(new_professional)
    else:
        return jsonify({"error": "Invalid role"}), 400

    # Remove from pending_users
    db.session.delete(pending_user)

    # Commit all changes
    db.session.commit()

    return jsonify({"message": f"{pending_user.role.name} approved successfully!"}), 200


# Reject User
@routes.route("/api/admin/reject_user/<int:pending_user_id>", methods=["POST", "OPTIONS"])
@cross_origin()
@jwt_required()
def reject_user(pending_user_id):
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error
    
    # Fetch pending user
    pending_user = PendingUser.query.get(pending_user_id)
    if not pending_user:
        return jsonify({"error": "User not found in pending approvals"}), 404

    # Fetch user from users table and delete 
    user = User.query.get(pending_user.user_id)
    if user:
        db.session.delete(user)

    # Remove pending user from pending_users table
    db.session.delete(pending_user)
    
    # Commit changes
    db.session.commit()

    return jsonify({"message": "User rejected and removed from the system"}), 200


# User status
def check_user_status():
    """Middleware to check if the user is blocked."""
    try:
        verify_jwt_in_request()
        current_user = json.loads(get_jwt_identity())  # Decode identity JSON
        user = User.query.get(current_user["id"])

        if user.is_blocked:
            return jsonify({"error": "Your account has been blocked. Logging out..."}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 403


# Before Request
@routes.before_request
def before_request_func():
    if request.method == "OPTIONS":
        return  

    # Allowing public endpoints 
    if (request.path.startswith("/api/public/") or 
        request.path.startswith("/api/login") or 
        request.path.startswith("/api/signup")):
        return

    # For all other endpoints, checking the user's status (requires JWT)
    status = check_user_status()
    if status:
        return status

# Block user
@routes.route("/api/admin/block_user/<int:user_id>", methods=["POST"])
@jwt_required()
def block_user(user_id):
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.is_blocked = True
    db.session.commit()

    return jsonify({"message": f"User {user.username} has been blocked!"}), 200


# Unblock user
@routes.route("/api/admin/unblock_user/<int:user_id>", methods=["POST"])
@jwt_required()
def unblock_user(user_id):
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.is_blocked = False
    db.session.commit()

    return jsonify({"message": f"User {user.username} has been unblocked!"}), 200


# Manage users
@routes.route("/api/admin/manage_users", methods=["GET"])
@jwt_required()
def get_managed_users():
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error

    # all customers joined with their user
    customer_rows = db.session.query(Customer, User).join(User, Customer.user_id == User.id).all()

    # all professionals joined with their user
    professional_rows = db.session.query(Professional, User).join(User, Professional.user_id == User.id).all()

    results = []

    for (cust, usr) in customer_rows:
        results.append({
            "id": cust.id,           
            "user_id": usr.id,       
            "name": cust.full_name,
            "role": usr.role.name,   # "CUSTOMER"
            "is_active": usr.is_active,
            "is_blocked": usr.is_blocked,
            "zip_code": cust.zip_code,
            "email": usr.email,

        })

    for (prof, usr) in professional_rows:
        results.append({
            "id": prof.id,           
            "user_id": usr.id,       
            "name": prof.full_name,
            "role": usr.role.name,   # "PROFESSIONAL"
            "is_active": usr.is_active,
            "is_blocked": usr.is_blocked,
            "zip_code": prof.zip_code,
            "email": usr.email,

        })

    return jsonify(results), 200



@routes.route("/api/admin/toggle_active/<int:user_id>", methods=["POST"])
@jwt_required()
def toggle_active(user_id):

    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Toggle the is_active flag: True will become False and vice-versa
    user.is_active = not user.is_active
    db.session.commit()

    status = "active" if user.is_active else "inactive"
    return jsonify({"message": f"User {user.username} is now {status}."}), 200


# Create Service
@routes.route("/api/admin/services", methods=["POST"])
@jwt_required()
def create_service():
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error

    data = request.get_json() or {}
    title = data.get("title")
    description = data.get("description")
    category = data.get("category")
    price = data.get("price", 0.0)

    if not title:
        return jsonify({"error": "Service title is required"}), 400

    new_service = Service(
        title=title,
        description=description,
        category=category,
        price=price
    )
    db.session.add(new_service)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

    return jsonify({
        "message": f"Service '{new_service.title}' created successfully!",
        "service_id": new_service.id
    }), 201


@routes.route("/api/admin/services", methods=["GET"])
@jwt_required()
def get_all_services():
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error

    services = Service.query.all()
    result = []
    for s in services:
        result.append({
            "id": s.id,
            "title": s.title,
            "description": s.description,
            "category": s.category,
            "price": s.price,
            "created_at": s.created_at.isoformat()
        })

    return jsonify(result), 200

# Update Service
@routes.route("/api/admin/services/<int:service_id>", methods=["PUT"])
@jwt_required()
def update_service(service_id):
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error

    service = Service.query.get_or_404(service_id)
    data = request.get_json() or {}

    service.title = data.get("title", service.title)
    service.description = data.get("description", service.description)
    service.category = data.get("category", service.category)
    service.price = data.get("price", service.price)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

    return jsonify({"message": f"Service '{service.title}' updated successfully!"}), 200

# Delete Service
@routes.route("/api/admin/services/<int:service_id>", methods=["DELETE"])
@jwt_required()
def delete_service(service_id):
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error

    service = Service.query.get_or_404(service_id)
    db.session.delete(service)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

    return jsonify({"message": f"Service '{service.title}' deleted successfully!"}), 200

# Get Public service
@routes.route("/api/public/services", methods=["GET"])
@cross_origin()
def get_public_services():
    services = Service.query.all()
    result = []
    
    for s in services:
        professionals = Professional.query.filter_by(service_type=s.id).all()
        
        professionals_data = [
            {
                "id": p.id,
                "name": p.full_name,
                "experience_years": p.experience_years,
                "phone": p.phone
            }
            for p in professionals
        ]
        
        result.append({
            "id": s.id,
            "title": s.title,
            "description": s.description,
            "category": s.category,
            "price": s.price,
            "created_at": s.created_at.isoformat(),
            "professionals": professionals_data  # Include professionals in response
        })
    
    return jsonify(result), 200


# Customer & professional requests 
def has_active_request(customer_id, professional_id):
    active_statuses = ["REQUESTED", "ACCEPTED", "IN_PROGRESS", "WORK_DONE"]
    return ServiceRequest.query.filter_by(customer_id=customer_id, professional_id=professional_id).filter(ServiceRequest.status.in_(active_statuses)).first()

# Request service
@routes.route('/request_service', methods=['POST'])
def request_service():
    data = request.json
    customer_id = data['customer_id']
    professional_id = data['professional_id']
    service_id= data['service_id']
    desired_date_str = data['desired_service_date']
    
    if has_active_request(customer_id, professional_id):
        return jsonify({"error": "You already have an active request with this professional."}), 400

    from datetime import datetime
    desired_date = None
    if desired_date_str:
        desired_date = datetime.strptime(desired_date_str, "%Y-%m-%d")

    new_request = ServiceRequest(
        customer_id=customer_id,
        professional_id=professional_id,
        service_id=service_id,
        desired_service_date=desired_date,
        status="REQUESTED"
    )
    db.session.add(new_request)
    db.session.commit()
    return jsonify({"message": "Service request sent successfully!", "request_id": new_request.id}), 201

# Cancel Request
@routes.route('/cancel_request', methods=['POST'])
def cancel_request():
    data = request.json
    request_id = data['request_id']
    
    service_request = ServiceRequest.query.get(request_id)
    if not service_request or service_request.status != "REQUESTED":
        return jsonify({"error": "Cancellation not allowed."}), 400
    
    service_request.status = "CANCELED"
    db.session.commit()
    return jsonify({"message": "Request canceled successfully."})

# Accept Request
@routes.route('/accept_request', methods=['POST'])
def accept_request():
    data = request.json
    request_id = data['request_id']
    
    service_request = ServiceRequest.query.get(request_id)
    if not service_request or service_request.status != "REQUESTED":
        return jsonify({"error": "Request is no longer available."}), 400
    
    service_request.status = "ACCEPTED"
    db.session.commit()
    return jsonify({"message": "Request accepted successfully."})

# Reject Request
@routes.route('/reject_request', methods=['POST'])
def reject_request():
    data = request.json
    request_id = data['request_id']
    
    service_request = ServiceRequest.query.get(request_id)
    if not service_request or service_request.status != "REQUESTED":
        return jsonify({"error": "Request is no longer available."}), 400
    
    service_request.status = "REJECTED"
    db.session.commit()
    return jsonify({"message": "Request rejected successfully."})

# Progress
@routes.route('/mark_in_progress', methods=['POST'])
def mark_in_progress():
    data = request.json
    request_id = data['request_id']
    
    service_request = ServiceRequest.query.get(request_id)
    if not service_request or service_request.status != "ACCEPTED":
        return jsonify({"error": "Request cannot be updated."}), 400
    
    service_request.status = "IN_PROGRESS"
    db.session.commit()
    return jsonify({"message": "Work marked as in progress."})

# Work-Done
@routes.route('/mark_work_done', methods=['POST'])
def mark_work_done():
    data = request.json
    request_id = data['request_id']
    
    service_request = ServiceRequest.query.get(request_id)
    if not service_request or service_request.status != "IN_PROGRESS":
        return jsonify({"error": "Request cannot be updated."}), 400
    
    service_request.status = "WORK_DONE"
    db.session.commit()
    return jsonify({"message": "Work marked as done. Awaiting payment."})


# Payment
@routes.route('/customer/payment/<int:request_id>', methods=['POST', 'OPTIONS'])
@cross_origin()
@jwt_required()
def process_payment(request_id):

    service_request = ServiceRequest.query.get(request_id)

    if not service_request or service_request.status != RequestStatus.WORK_DONE:
        return jsonify({"error": "Payment cannot be processed."}), 400

    claims = get_jwt()
    try:
        sub_data = json.loads(claims.get("sub", "{}"))
    except Exception as e:
        print("Error parsing JWT sub field:", e)
        return jsonify({"error": "Some internal server error."}), 500

    # Check that the role from the token is CUSTOMER.
    if sub_data.get("role", "").upper() != "CUSTOMER":
        return jsonify({"error": "Not authorized."}), 403

    # Calculate commission: 10% of the service's price
    commission_rate = 0.10
    if not service_request.service:
        return jsonify({"error": "Service not found. Cannot process commission."}), 404

    service_cost = service_request.service.price or 0
    commission = service_cost * commission_rate

    # Update service request fields
    service_request.commission_amount = commission
    service_request.status = RequestStatus.COMPLETED
    service_request.payment_status = "COMPLETED"
    db.session.commit()

    return jsonify({
        "message": "Payment successful. Request completed.",
        "commission_charged": commission
    }), 200


# Rating
@routes.route('/customer/rate/<int:request_id>', methods=['POST', 'OPTIONS'])
@cross_origin()
@jwt_required()
def submit_rating(request_id):
    try:
        # Getting JWT claims and parsing the "sub" field
        claims = get_jwt()
        try:
            sub_data = json.loads(claims.get("sub", "{}"))
        except Exception as e:
            print("Error parsing JWT sub field:", e)
            return jsonify({"error": "Internal server error."}), 500

        if sub_data.get("role", "").upper() != "CUSTOMER":
            return jsonify({"error": "Not authorized."}), 403

        data = request.get_json()
        rating = data.get("rating")
        remarks = data.get("remarks", "")

        try:
            rating = float(rating)
            if rating < 1 or rating > 5:
                return jsonify({"error": "Invalid rating. Must be between 1 and 5."}), 400
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid rating value."}), 400

        print(" sub_data:", sub_data)
        user_id = sub_data.get("id")
        print(" user_id from token:", user_id)

        # Joining with Customer to ensure the service request belongs to this customer.
        service_request = (
            ServiceRequest.query
            .join(Customer, ServiceRequest.customer_id == Customer.id)
            .filter(
                ServiceRequest.id == request_id,
                Customer.user_id == user_id
            )
            .first()
        )
        print(" Found service_request:", service_request)

        if not service_request:
            return jsonify({"error": "Service request not found."}), 404

        # Using request_date as a fallback for checking edit period.
        if service_request.request_date:
            from datetime import datetime
            days_since_request = (datetime.now() - service_request.request_date).days
            if days_since_request > 15:
                return jsonify({"error": "Edit period expired (15 days)."}), 403

        # Updating rating and remarks
        service_request.rating = rating
        service_request.remarks = remarks
        db.session.commit()
        print(" Rating saved for service_request:", service_request.id)

        # Recalculating professional's average rating (unchanged)
        professional_id = service_request.professional_id
        print(" professional_id:", professional_id)
        if professional_id:
            from sqlalchemy import func
            avg_rating = db.session.query(func.avg(ServiceRequest.rating)) \
                                   .filter(
                                       ServiceRequest.professional_id == professional_id,
                                       ServiceRequest.rating != None
                                   ).scalar()
            print(" Calculated avg_rating:", avg_rating)
            if avg_rating is not None:
                professional = Professional.query.get(professional_id)
                if professional:
                    professional.average_rating = float(avg_rating)
                    db.session.commit()
                    print(" Updated professional average_rating to:", avg_rating)
                else:
                    print(" Professional not found for id:", professional_id)

        return jsonify({
            "message": "Rating and review submitted successfully.",
            "updated_rating": service_request.rating,
            "updated_remarks": service_request.remarks
        }), 200

    except Exception as e:
        print("Error processing rating:", e)
        return jsonify({"error": "Error processing rating", "details": str(e)}), 500

# Rating History
@routes.route("/customer/rating_history", methods=["GET", "OPTIONS"])
@cross_origin()
@jwt_required()
def rating_history():
    if request.method == "OPTIONS":
        resp = jsonify({"message": "CORS Preflight OK"})
        resp.headers.update({
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Authorization, Content-Type"
        })
        return resp, 200

    # Extracting user info from JWT
    claims = get_jwt()
    try:
        sub_data = json.loads(claims.get("sub", "{}"))
    except Exception as e:
        print("Error parsing JWT sub field:", e)
        return jsonify({"error": "Internal server error."}), 500

    role = sub_data.get("role", "").upper()
    user_id = sub_data.get("id")
    if not user_id:
        return jsonify({"error": "No user ID found in token."}), 400

    result = []

    if role == "CUSTOMER":
        # For customers, fetch the service requests (with ratings) that they submitted.
        service_requests = (
            db.session.query(ServiceRequest, Professional.full_name.label("professional_name"))
            .join(Customer, ServiceRequest.customer_id == Customer.id)
            .join(Professional, ServiceRequest.professional_id == Professional.id)
            .filter(Customer.user_id == user_id)
            .filter(ServiceRequest.rating != None)
            .all()
        )
        for (sr, pro_name) in service_requests:
            editable = False
            if sr.completion_date:
                days_since_completion = (datetime.utcnow() - sr.completion_date).days
                editable = days_since_completion <= 15
            result.append({
                "request_id": sr.id,
                "professional_name": pro_name,
                "rating": sr.rating,
                "remarks": sr.remarks,
                "completed_on": sr.completion_date.isoformat() if sr.completion_date else None,
                "editable": editable
            })

    elif role == "PROFESSIONAL":
        professional = Professional.query.filter_by(user_id=user_id).first()
        if not professional:
            return jsonify({"error": "Professional record not found."}), 404

        
        # Joining with Customer to get the customer's name and with Service to get the service title.
        service_requests = (
            db.session.query(ServiceRequest, Customer.full_name.label("customer_name"), Service.title.label("service_title"))
            .join(Customer, ServiceRequest.customer_id == Customer.id)
            .join(Service, ServiceRequest.service_id == Service.id)
            .filter(ServiceRequest.professional_id == professional.id)
            .filter(ServiceRequest.rating != None)
            .all()
        )
        for (sr, cust_name, svc_title) in service_requests:
            result.append({
                "request_id": sr.id,
                "customer_name": cust_name,
                "service_title": svc_title,
                "rating": sr.rating,
                "remarks": sr.remarks,
                "completed_on": sr.completion_date.isoformat() if sr.completion_date else None,
                # Professionals might not need an "editable" flag; adjust as needed.
            })
    else:
        return jsonify({"error": "Not authorized."}), 403

    return jsonify(result), 200


# Completing Request
@routes.route('/customer/complete/<int:request_id>', methods=['POST', 'OPTIONS'])
@cross_origin()
@jwt_required()
def complete_request(request_id):
    # Get JWT claims and parse the "sub" field to get user info.
    claims = get_jwt()
    try:
        sub_data = json.loads(claims.get("sub", "{}"))
    except Exception as e:
        print("Error parsing JWT sub field:", e)
        return jsonify({"error": "Internal server error."}), 500

    # Ensure the role is CUSTOMER.
    if sub_data.get("role", "").upper() != "CUSTOMER":
        return jsonify({"error": "Not authorized."}), 403

    user_id = sub_data.get("id")

    # Retrieve the service request by joining with the Customer table.
    service_request = (
        ServiceRequest.query
        .join(Customer, ServiceRequest.customer_id == Customer.id)
        .filter(
            ServiceRequest.id == request_id,
            Customer.user_id == user_id
        )
        .first()
    )

    if not service_request:
        return jsonify({"error": "Service request not found."}), 404

    # Checking that the payment_status is already COMPLETED,
    # Also that a rating has been submitted, before marking as complete.
    # We'll simply update the service_status to COMPLETED.
    service_request.service_status = "COMPLETED"
    
    india_tz = pytz.timezone("Asia/Kolkata")
    service_request.completion_date = datetime.now(india_tz)
    db.session.commit()

    return jsonify({"message": "Request marked as completed."}), 200

# Get Request
@routes.route("/get_requests", methods=["GET"])
@cross_origin()
def get_requests():
    customer_id = request.args.get("customer_id")
    professional_id = request.args.get("professional_id")  
    status = request.args.get("status")

    # Joining with Service and optionally with Professional
    query = ServiceRequest.query \
        .join(Service, ServiceRequest.service_id == Service.id) \
        .outerjoin(Professional, ServiceRequest.professional_id == Professional.id)

    # Filtering by customer 
    if customer_id:
        query = query.filter(ServiceRequest.customer_id == customer_id)

    # Filtering by professional 
    if professional_id:
        query = query.filter(ServiceRequest.professional_id == professional_id)

    # Filtering by status 
    if status:
        query = query.filter(ServiceRequest.status == status)

    requests = query.all()

    for req in requests:
        # print(f"DEBUG: Request ID -> {req.id}, Professional ID -> {req.professional_id}")
        professional_name = req.professional.full_name if req.professional else "N/A"
        # print(f"DEBUG: professional_name -> {professional_name}")

    # Returning JSON response
    return jsonify([
        {
            "id": req.id,
            "customer_id": req.customer_id,
            "customer_name": req.customer.full_name if req.customer else "N/A",
            "professional_id": req.professional_id,
            "service_id": req.service_id,
            "service_title": req.service.title if req.service else "N/A",
            "service_price": req.service.price if req.service else "N/A",
            "professional_name": req.professional.full_name if req.professional else "N/A",
            "status": req.status.value if isinstance(req.status, RequestStatus) else str(req.status),
            "request_date": req.request_date.isoformat() if req.request_date else None,
            "customer_zip_code": req.customer.zip_code if req.customer else "N/A",
            "customer_address": req.customer.address if req.customer else "N/A",
            "professional_zip_code": req.professional.zip_code if req.professional else "N/A",
            "professional_address": req.professional.address if req.professional else "N/A",
            "completion_date": req.completion_date.isoformat() if req.completion_date else None,
            "remarks": req.remarks or "N/A",
            "rating": req.rating if req.rating is not None else "Not Rated",
            "payment_status": req.payment_status,
            "desired_service_date": req.desired_service_date.isoformat() if req.desired_service_date else None,
            
        }
        for req in requests
    ])


# Update Request status
@routes.route("/update_request_status", methods=["POST", "OPTIONS"])
@cross_origin()  # Ensures CORS for POST/OPTIONS
def update_request_status():
   
    data = request.json
    request_id = data.get("request_id")
    new_status = data.get("new_status")

    if not request_id or not new_status:
        return jsonify({"error": "Missing request_id or new_status"}), 400

    # Fetching the ServiceRequest from DB
    serv_req = ServiceRequest.query.get(request_id)
    if not serv_req:
        return jsonify({"error": "Request not found"}), 404

    # Updating status
    serv_req.status = new_status

    db.session.commit()

    return jsonify({"message": f"Request {request_id} updated to {new_status}"}), 200

# Subscription status
@routes.route('/api/customer/subscription_status', methods=['GET'])
@cross_origin()
@jwt_required()
def subscription_status():
    # Parsing JWT claims to get user info
    claims = get_jwt()
    try:
        sub_data = json.loads(claims.get("sub", "{}"))
    except Exception as e:
        print("Error parsing JWT sub field:", e)
        return jsonify({"error": "Internal server error."}), 500

    user_id = sub_data.get("id")
    if not user_id:
        return jsonify({"error": "User ID missing in token."}), 400

    # Fetching the customer record
    customer = Customer.query.filter_by(user_id=user_id).first()
    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    # Checking if they ever paid for subscription
    has_paid = SubscriptionPayment.query.filter_by(user_id=user_id).first() is not None

    return jsonify({
        "subscription_status": customer.subscription_status or "none",
        "subscription_expiry": customer.subscription_expiry.isoformat() if customer.subscription_expiry else None,
        "has_paid": has_paid
    }), 200

# Subscription
@routes.route('/api/customer/subscribe', methods=['POST', 'OPTIONS'])
@cross_origin()
@jwt_required()
def subscribe():
    claims = get_jwt()
    try:
        sub_data = json.loads(claims.get("sub", "{}"))
    except Exception as e:
        print("Error parsing JWT sub field:", e)
        return jsonify({"error": "Internal server error."}), 500

    if sub_data.get("role", "").upper() != "CUSTOMER":
        return jsonify({"error": "Not authorized."}), 403

    user_id = sub_data.get("id")
    data = request.get_json()
    amount = data.get("amount", 20.0)

    if not amount:
        return jsonify({"error": "Amount is required."}), 400

    new_payment = SubscriptionPayment(user_id=user_id, amount=amount)
    db.session.add(new_payment)

    # Updating customer table
    customer = Customer.query.filter_by(user_id=user_id).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    customer.subscription_status = "active"
    customer.subscription_expiry = datetime.utcnow() + timedelta(days=30)

    db.session.commit()

    return jsonify({
        "message": "Hurray!, you're subscribed now. Enjoy all new features",
        "subscription_status": customer.subscription_status,
        "subscription_expiry": customer.subscription_expiry.isoformat()
    }), 200

# Getting All Professionals
@routes.route("/api/admin/professionals", methods=["GET"])
@jwt_required()
def get_all_professionals():
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error

    professionals = Professional.query.all()
    result = []
    for pro in professionals:
        result.append({
            "id": pro.id,
            "full_name": pro.full_name,
            "zip_code": pro.zip_code,
            "address": pro.address,
            "experience_years": pro.experience_years,
            "average_rating": pro.average_rating
        })
    return jsonify(result), 200

# Getting All Customers
@routes.route("/api/admin/customers", methods=["GET"])
@jwt_required()
def get_all_customers():
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error

    customers = Customer.query.all()
    result = []
    for c in customers:
        result.append({
            "id": c.id,
            "full_name": c.full_name,
            "address": c.address,
            "zip_code": c.zip_code
        })
    return jsonify(result), 200

# Getting All Service Request
@routes.route("/api/admin/service_requests", methods=["GET"])
@jwt_required()
def get_all_service_requests():
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error

    requests = ServiceRequest.query.all()
    result = []
    for req in requests:
        result.append({
            "id": req.id,
            "customer_id": req.customer_id,
            "professional_id": req.professional_id,
            "service_id": req.service_id,
            "service_title": req.service.title if req.service else None,
            # status is an Enum, convert to string
            "status": req.status if isinstance(req.status, str) else req.status.value,
            "remarks": req.remarks,
            "rating": req.rating,
            "request_date": req.request_date.isoformat() if req.request_date else None,
            "completion_date": req.completion_date.isoformat() if req.completion_date else None,
        })
    return jsonify(result), 200

# Fetching Service Request by it's status
@routes.route("/api/admin/service_requests_by_status", methods=["GET"])
@jwt_required()
def service_requests_by_status():
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error

    from sqlalchemy import func
    # Grouping by status
    status_counts = db.session.query(
        ServiceRequest.status, func.count(ServiceRequest.id)
    ).group_by(ServiceRequest.status).all()

    # Using the internal statuses as keys 
    possible_statuses = ["REQUESTED", "ACCEPTED", "IN_PROGRESS", "WORK_DONE", "COMPLETED", "REJECTED"]
    counts_map = {s: 0 for s in possible_statuses}

    # Populating counts_map with actual counts 
    for (status_val, count) in status_counts:
        
        if hasattr(status_val, "value"):
            status_val = status_val.value

        status_val = status_val.upper()
        if status_val in counts_map:
            counts_map[status_val] = count

    # Defining a mapping from backend status to display names
    label_map = {
        "REQUESTED": "Pending",
        "ACCEPTED": "Accepted",
        "IN_PROGRESS": "In Progress",
        "WORK_DONE": "Work Done",
        "COMPLETED": "Completed",
        "REJECTED": "Rejected"
    }

    # Building final arrays in desired order using the mapping
    final_labels = [label_map[s] for s in possible_statuses]
    final_data = [counts_map[s] for s in possible_statuses]

    return jsonify({"labels": final_labels, "data": final_data}), 200


# Professional Rating Distribution
@routes.route("/api/admin/professional_ratings_distribution", methods=["GET"])
@jwt_required()
def professional_ratings_distribution():
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error

    professionals = Professional.query.all()

    # Bins for rating distribution
    bins = {
        "1-2": 0,
        "2-3": 0,
        "3-4": 0,
        "4-5": 0
    }

    for pro in professionals:
        rating = pro.average_rating or 0.0
        if 1 <= rating < 2:
            bins["1-2"] += 1
        elif 2 <= rating < 3:
            bins["2-3"] += 1
        elif 3 <= rating < 4:
            bins["3-4"] += 1
        elif 4 <= rating <= 5:
            bins["4-5"] += 1
        # If rating < 1 or rating > 5, handle or ignore as needed.

    labels = list(bins.keys())    # ["1-2", "2-3", "3-4", "4-5"]
    data = list(bins.values())    # [2, 5, 10, 8]

    return jsonify({"labels": labels, "data": data}), 200

# User status
@routes.route("/api/admin/user_stats", methods=["GET"])
@jwt_required()
def user_stats():
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error

    # Counting active/blocked customers
    active_customers = db.session.query(User).filter(
        User.role == UserRole.CUSTOMER,
        User.is_blocked == False
    ).count()

    blocked_customers = db.session.query(User).filter(
        User.role == UserRole.CUSTOMER,
        User.is_blocked == True
    ).count()

    # Counting active/blocked professionals
    active_pros = db.session.query(User).filter(
        User.role == UserRole.PROFESSIONAL,
        User.is_blocked == False
    ).count()

    blocked_pros = db.session.query(User).filter(
        User.role == UserRole.PROFESSIONAL,
        User.is_blocked == True
    ).count()

    labels = ["Active Customers", "Blocked Customers", "Active Pros", "Blocked Pros"]
    data = [active_customers, blocked_customers, active_pros, blocked_pros]

    return jsonify({"labels": labels, "data": data}), 200

# Service Overview
@routes.route("/api/admin/services_overview", methods=["GET"])
@jwt_required()
def services_overview():
    auth_error = role_required("ADMIN")
    if auth_error:
        return auth_error

    from sqlalchemy import func

    # Counting requests for each service
    service_counts = db.session.query(
        Service.title, func.count(ServiceRequest.id)
    ).join(ServiceRequest, Service.id == ServiceRequest.service_id) \
     .group_by(Service.id).all()

    # service_counts is [(title, count), ...]
    labels = []
    data = []
    for title, count in service_counts:
        labels.append(title)
        data.append(count)

    return jsonify({"labels": labels, "data": data}), 200

# Service Request by status
@routes.route("/api/customer/service_requests_stats", methods=["GET"])
@jwt_required()
def customer_service_requests_stats():
    auth_error = role_required("CUSTOMER")
    if auth_error:
        return auth_error

    # Extract user info from JWT
    claims = get_jwt()
    sub_data = json.loads(claims.get("sub", "{}"))
    user_id = sub_data.get("id")

    # Get customer ID from user ID
    customer = Customer.query.filter_by(user_id=user_id).first()
    if not customer:
        return jsonify({"labels": [], "data": []}), 200

    # Count service requests by status for this customer
    from sqlalchemy import func
    status_counts = db.session.query(
        ServiceRequest.status, func.count(ServiceRequest.id)
    ).filter(ServiceRequest.customer_id == customer.id) \
     .group_by(ServiceRequest.status).all()

    # Add REQUESTED here to show as "Pending" later
    possible_statuses = ["REQUESTED", "ACCEPTED", "IN_PROGRESS", "WORK_DONE", "REJECTED", "COMPLETED"]
    counts_map = {status: 0 for status in possible_statuses}

    for (status_val, count_val) in status_counts:
        if hasattr(status_val, "value"):
            status_val = status_val.value
        status_val = status_val.upper()
        if status_val in counts_map:
            counts_map[status_val] = count_val

    # Friendly display labels for frontend
    label_map = {
        "REQUESTED": "Pending",
        "ACCEPTED": "Accepted",
        "IN_PROGRESS": "In Progress",
        "WORK_DONE": "Work Done",
        "REJECTED": "Rejected",
        "COMPLETED": "Completed"
    }

    labels = [label_map[status] for status in possible_statuses]
    data = [counts_map[status] for status in possible_statuses]

    return jsonify({"labels": labels, "data": data}), 200


# Service Overview
@routes.route("/api/customer/services_overview", methods=["GET"])
@jwt_required()
def customer_services_overview():

    auth_error = role_required("CUSTOMER")
    if auth_error:
        return auth_error

    claims = get_jwt()
    sub_data = json.loads(claims.get("sub", "{}"))
    user_id = sub_data.get("id")

    customer = Customer.query.filter_by(user_id=user_id).first()
    if not customer:
        return jsonify({"labels": [], "data": []}), 200

    # Counting how many times each service was requested by this customer
    from sqlalchemy import func
    service_counts = db.session.query(
        Service.title, func.count(ServiceRequest.id)
    ).join(ServiceRequest, Service.id == ServiceRequest.service_id) \
     .filter(ServiceRequest.customer_id == customer.id) \
     .group_by(Service.id).all()

    labels = []
    data = []
    for (title, count_val) in service_counts:
        labels.append(title)
        data.append(count_val)

    return jsonify({"labels": labels, "data": data}), 200

# Request status for professional
@routes.route("/api/professional/requests_by_status", methods=["GET"])
@jwt_required()
def professional_requests_by_status():
    professional_id = request.args.get("professional_id")
    if not professional_id:
        return jsonify({"error": "Missing professional_id"}), 400

    from sqlalchemy import func
    status_counts = db.session.query(
        ServiceRequest.status, func.count(ServiceRequest.id)
    ).filter(ServiceRequest.professional_id == professional_id) \
     .group_by(ServiceRequest.status).all()

    # Include all possible statuses (REQUESTED shown as "Pending")
    possible_statuses = ["REQUESTED", "IN_PROGRESS", "WORK_DONE", "COMPLETED", "REJECTED"]
    counts_map = {status: 0 for status in possible_statuses}

    for status_val, count in status_counts:
        if hasattr(status_val, "value"):
            status_val = status_val.value
        status_val = status_val.upper()
        if status_val in counts_map:
            counts_map[status_val] = count

    # Display-friendly labels
    label_map = {
        "REQUESTED": "Pending",
        "IN_PROGRESS": "In Progress",
        "WORK_DONE": "Work Done",
        "COMPLETED": "Completed",
        "REJECTED": "Rejected"
    }

    labels = [label_map[status] for status in possible_statuses]
    data = [counts_map[status] for status in possible_statuses]

    return jsonify({"labels": labels, "data": data}), 200


# Service Overview 
@routes.route("/api/professional/services_overview", methods=["GET"])
@jwt_required()
def professional_services_overview():
    professional_id = request.args.get("professional_id")
    if not professional_id:
        return jsonify({"error": "Missing professional_id"}), 400

    # Joining ServiceRequest with Service, group by Service.id
    service_counts = db.session.query(
        Service.title, func.count(ServiceRequest.id)
    ).join(Service, ServiceRequest.service_id == Service.id) \
     .filter(ServiceRequest.professional_id == professional_id) \
     .group_by(Service.id).all()

    labels = []
    data = []
    for title, count in service_counts:
        labels.append(title)
        data.append(count)

    return jsonify({"labels": labels, "data": data}), 200


# Downloading Portfolio 
from flask import send_from_directory, current_app

@routes.route('/uploads/<filename>', methods=['GET'])
@cross_origin(origins="*")  # Explicitly enabling CORS for this route
def download_pdf(filename):
    uploads_dir = current_app.config.get("UPLOAD_FOLDER", "uploads")

    # print(f"Serving: {uploads_dir}/{filename}") 
    return send_from_directory(uploads_dir, filename, as_attachment=False)

# Exporting-closed-service-request
@routes.route("/api/export-closed-service-requests", methods=["POST"])
@cross_origin()
@jwt_required()
def start_export_job():
    """
    Triggering the CSV export job asynchronously using Celery.
    """
    # from tasks import export_closed_service_requests  # local import to avoid circular dependency
    from tasks import export_completed_services
    task = export_completed_services.delay()
    return jsonify({
        "jobId": task.id,
        "message": "Export job started. You will be notified when complete."
    })


@routes.route("/api/export-status", methods=["GET"])
@cross_origin()  # Ensure CORS headers are included
@jwt_required()
def export_status():
    """
    Check the status of the export job and, if complete, return a download URL.
    """
    from tasks import export_completed_services  # local import
    job_id = request.args.get("jobId")
    if not job_id:
        return jsonify({"message": "Job ID is required"}), 400

    task = export_completed_services.AsyncResult(job_id)
    if task.state == "SUCCESS":
        # task.result is expected to be a dict with keys 'csv' and 'pdf'
        result = task.result  
        # Choose the PDF file for download (adjust if you need CSV instead)
        pdf_path = result.get("pdf")
        if not pdf_path:
            return jsonify({"message": "Export completed but no file found."}), 500
        download_url = f"/download/{os.path.basename(pdf_path)}"
        return jsonify({
            "jobId": job_id,
            "status": task.state,
            "downloadUrl": download_url
        })
    else:
        return jsonify({
            "jobId": job_id,
            "status": task.state
        })


@routes.route("/download/<filename>", methods=["GET"])
@cross_origin()
@jwt_required()
def download_report(filename):
    file_path = os.path.join(current_app.config.get("REPORTS_STORAGE", os.getcwd()), filename)
    if not os.path.exists(file_path):
        return ("File not found on server", 404)
    response = send_file(file_path, as_attachment=True, download_name=filename)
    return response



@routes.route("/api/requests/<int:request_id>", methods=["PUT", "OPTIONS"])
@cross_origin(origins="*")
@jwt_required()
def update_request(request_id):
    # Handle the preflight OPTIONS request
    if request.method == "OPTIONS":
        response = jsonify({"message": "CORS Preflight OK"})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "PUT, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        return response, 200

    # Retrieving the current user from the JWT token.
    current_user = get_jwt_identity()

    # If current_user is a string, parse it as JSON.
    if isinstance(current_user, str):
        try:
            current_user = json.loads(current_user)
        except Exception as e:
            return jsonify({"error": "Invalid token identity format"}), 400

    # Extracting user id from the token (user id from the User table).
    if isinstance(current_user, dict):
        user_id = current_user.get("id")
    else:
        try:
            user_id = int(current_user)
        except ValueError:
            return jsonify({"error": "Invalid user identity"}), 400

    # Looking up the Customer record for the logged-in user.
    customer = Customer.query.filter_by(user_id=user_id).first()
    if not customer:
        return jsonify({"error": "Customer record not found for this user."}), 403

    # Retrieving the service request.
    req = ServiceRequest.query.get_or_404(request_id)

    # Comparing the customer id from the request with the Customer record's id.
    if req.customer_id != customer.id:
        return jsonify({"error": "User is not the owner of this request."}), 403

    
    # print("DEBUG: Request status is:", req.status)

    if hasattr(req.status, 'value'):
        request_status = req.status.value.upper().strip()
    else:
        request_status = str(req.status).upper().strip()

    if request_status not in ["REQUESTED", "PENDING"]:
        return jsonify({"error": "Cannot edit this request at its current stage."}), 403

    # Getting the JSON payload from the request.
    data = request.get_json()
    new_date_str = data.get("desired_service_date")

    if new_date_str:
        try:
            # Parsing the date assuming the format "YYYY-MM-DD"
            new_date = datetime.strptime(new_date_str, "%Y-%m-%d")
            req.desired_service_date = new_date
        except Exception as e:
            return jsonify({"error": f"Invalid date format. Expected YYYY-MM-DD. {str(e)}"}), 400

    db.session.commit()
    return jsonify({"message": "Request updated successfully"}), 200

# Delete Request
@routes.route("/api/requests/<int:request_id>", methods=["DELETE"])
@cross_origin()
@jwt_required()
def delete_request(request_id):
    """
    Delete the service request from the database.
    This endpoint deletes the specific service request (identified by request_id)
    only if its status is "REQUESTED" (i.e., pending).
    """
    sr = ServiceRequest.query.get(request_id)
    
    if not sr:
        return jsonify({"error": "Request not found"}), 404
    
    print("Service Request Status:", repr(sr.status))

    # Only allow deletion if the request is in the "REQUESTED" status.
    if sr.status != RequestStatus.REQUESTED:
        return jsonify({"error": "Only pending requests can be canceled."}), 400

    db.session.delete(sr)
    db.session.commit()

    return jsonify({"message": "Request deleted successfully."}), 200


# Export Service History
from fpdf import FPDF

export_bp = Blueprint('export_bp', __name__)

@export_bp.route('/api/customer/export_service_history', methods=['GET'])
@cross_origin()
def export_service_history():
    customer_id = request.args.get('customer_id')
    if not customer_id:
        return jsonify({'error': 'Missing customer_id'}), 400

    # Fetching completed requests for the customer
    completed_requests = ServiceRequest.query.filter_by(
        customer_id=customer_id,
        status='COMPLETED'
    ).all()

    if not completed_requests:
        return jsonify({'error': 'No completed requests found.'}), 404

    # Generating PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Service History Report", ln=True, align="C")
    pdf.ln(10)

    for req in completed_requests:
        service = Service.query.get(req.service_id)
        customer = Customer.query.get(req.customer_id)
        professional = Professional.query.get(req.professional_id)

        pdf.cell(200, 10, txt=f"Request ID: {req.id}", ln=True)
        pdf.cell(200, 10, txt=f"Service: {service.title if service else 'N/A'}", ln=True)
        pdf.cell(200, 10, txt=f"Professional: {professional.full_name if professional else 'N/A'}", ln=True)
        pdf.cell(200, 10, txt=f"Customer: {customer.full_name if customer else 'N/A'}", ln=True)
        pdf.cell(200, 10, txt=f"Price: $. {service.price}", ln=True)
        pdf.cell(200, 10, txt=f"Requested On: {req.request_date.strftime('%d-%m-%Y') if req.request_date else 'N/A'}", ln=True)
        pdf.cell(200, 10, txt=f"Completed On: {req.completion_date.strftime('%d-%m-%Y') if req.completion_date else 'N/A'}", ln=True)
        pdf.cell(200, 10, txt="------------------------------", ln=True)
        pdf.ln(4)

    # Serving PDF as a downloadable file
    pdf_output = pdf.output(dest='S').encode('latin1')  # Getting PDF content as bytes
    buffer = io.BytesIO(pdf_output)
    buffer.seek(0)

    filename = f"service_history_{customer_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')


# Assuming you're using a blueprint for customer routes
customer_bp = Blueprint("customer_bp", __name__)

# Cancel Subscription
@customer_bp.route("/api/customer/cancel_subscription", methods=["POST"])
@jwt_required()
def cancel_subscription():
    try:
        raw_identity = get_jwt_identity()
        print("Raw identity from token:", raw_identity)
        identity = json.loads(raw_identity)
    except Exception as e:
        return jsonify({"error": "Invalid token identity format"}), 400

    user_id = identity.get("id")
    role = identity.get("role")

    if role != "CUSTOMER":
        return jsonify({"error": "Only customers can cancel subscriptions"}), 403

    customer = Customer.query.filter_by(user_id=user_id).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    if customer.subscription_status != "active":
        return jsonify({"error": "You don't have an active subscription"}), 400

    # Deactivating subscription
    customer.subscription_status = "inactive"
    customer.subscription_expiry = None
    db.session.commit()

    return jsonify({"message": "Subscription cancelled successfully!"}), 200

# Activate Subscription
@customer_bp.route("/api/customer/activate_subscription", methods=["POST"])
@jwt_required()
def activate_subscription():

    identity = get_jwt_identity()

    if isinstance(identity, str):
        identity = json.loads(identity)

    user_id = identity.get("id")

    customer = Customer.query.filter_by(user_id=user_id).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    customer.subscription_status = "active"
    customer.subscription_expiry = datetime.utcnow() + timedelta(days=30)
    db.session.commit()

    return jsonify({"message": "Subscription activated", "subscription_expiry": customer.subscription_expiry})
