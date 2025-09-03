import streamlit as st
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

firebase_config = {
  "apiKey": os.getenv("FIREBASE_API_KEY"),
  "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
  "projectId": os.getenv("FIREBASE_PROJECT_ID"),
  "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
  "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
  "appId": os.getenv("FIREBASE_APP_ID"),
  "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID")
}

# Validate that all required Firebase config values are loaded
required_config_keys = ["apiKey", "authDomain", "projectId", "storageBucket", "messagingSenderId", "appId"]
missing_keys = [key for key in required_config_keys if not firebase_config[key]]

if missing_keys:
    raise ValueError(f"Missing required Firebase configuration: {', '.join(missing_keys)}. Please check your .env file.")

def authenticate_with_firebase(email: str, password: str) -> dict:
    """Authenticate with Firebase REST API."""
    try:
        api_key = firebase_config["apiKey"]
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "error": response.json().get("error", {}).get("message", "Authentication failed")
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def firebase_sign_up(email: str, password: str) -> dict:
    """Sign up new user with Firebase REST API."""
    try:
        api_key = firebase_config["apiKey"]
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
        
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "error": response.json().get("error", {}).get("message", "Sign up failed")
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def send_reset_email(email: str) -> dict:
    """Send password reset email via Firebase REST API."""
    try:
        api_key = firebase_config["apiKey"]
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
        
        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": "Password reset email sent successfully!"
            }
        else:
            return {
                "success": False,
                "error": response.json().get("error", {}).get("message", "Failed to send password reset email")
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def login_page():
    """Display login page with sign-up and password reset options."""
    st.set_page_config(
        page_title="CPA - Authentication",
        page_icon="🔐",
        layout="centered"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background-color: white;
        }
        .login-title {
            color: #02ab21;
            font-size: 1.5rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown('<div class="login-title">Campaign Performance Assistant</div>', unsafe_allow_html=True)
        st.markdown('')
        
        # Initialize session state for tab selection
        if "auth_tab" not in st.session_state:
            st.session_state.auth_tab = "login"
        
        # Login Form
        if st.session_state.auth_tab == "login":
            st.markdown("##### 🔐 Login")
            
            with st.form("firebase_login_form"):
                email = st.text_input("Email", placeholder="Enter your email")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                login_submitted = st.form_submit_button("Login", use_container_width=True)
            
            if login_submitted:
                if email and password:
                    with st.spinner("Authenticating..."):
                        result = authenticate_with_firebase(email, password)
                    
                    if result["success"]:
                        user_data = result["data"]
                        
                        # Set session state
                        st.session_state.authenticated = True
                        st.session_state.user_email = user_data["email"]
                        st.session_state.username = user_data["email"].split("@")[0]
                        st.session_state.login_time = datetime.now()
                        st.session_state.user_id = user_data["localId"]
                        st.session_state.id_token = user_data["idToken"]
                        st.session_state.role = "admin" if is_admin_user(user_data["email"]) else "user"
                        
                        st.success("✅ Login successful!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ Login failed: {result['error']}")
                else:
                    st.error("Please enter both email and password")
            
            # Side by side navigation buttons
            col_signup, col_reset = st.columns(2)

            with col_signup:
                if st.button("Sign Up", use_container_width=True, type="secondary"):
                    st.session_state.auth_tab = "signup"
                    st.rerun()
            
            with col_reset:
                if st.button("Reset Password", use_container_width=True, type="secondary"):
                    st.session_state.auth_tab = "reset"
                    st.rerun()
            

        # Sign Up Form
        elif st.session_state.auth_tab == "signup":
            st.markdown("##### 📝 Create New Account")
            
            with st.form("firebase_signup_form"):
                new_email = st.text_input("Email", placeholder="Enter your email address")
                new_password = st.text_input("Password", type="password", placeholder="Create a password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                
                # Password requirements info
                st.info("Password must be at least 6 characters long")
                
                signup_submitted = st.form_submit_button("Create Account", use_container_width=True)
            
            if signup_submitted:
                if new_email and new_password and confirm_password:
                    if new_password == confirm_password:
                        if len(new_password) >= 6:
                            with st.spinner("Creating account..."):
                                result = firebase_sign_up(new_email, new_password)
                            
                            if result["success"]:
                                user_data = result["data"]
                                
                                # Automatically login the new user
                                st.session_state.authenticated = True
                                st.session_state.user_email = user_data["email"]
                                st.session_state.username = user_data["email"].split("@")[0]
                                st.session_state.login_time = datetime.now()
                                st.session_state.user_id = user_data["localId"]
                                st.session_state.id_token = user_data["idToken"]
                                st.session_state.role = "admin" if is_admin_user(user_data["email"]) else "user"
                                st.success("✅ Account created and logged in successfully!")
                                st.rerun()
                            else:
                                st.error(f"❌ Sign up failed: {result['error']}")
                        else:
                            st.error("Password must be at least 6 characters long")
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Please fill in all fields")
            
            # Back to login link
            if st.button("Back to Login", use_container_width=True, type="secondary"):
                st.session_state.auth_tab = "login"
                st.rerun()
        
        # Password Reset Form
        elif st.session_state.auth_tab == "reset":
            st.markdown("##### 🔄 Reset Password")
            
            with st.form("firebase_reset_form"):
                reset_email = st.text_input("Email", placeholder="Enter your registered email address")
                
                st.info("Enter your email address and we'll send you a link to reset your password.")
                
                reset_submitted = st.form_submit_button("Send Reset Link", use_container_width=True)
            
            if reset_submitted:
                if reset_email:
                    with st.spinner("Sending reset email..."):
                        result = send_reset_email(reset_email)
                    
                    if result["success"]:
                        st.success("✅ Password reset email sent!")
                        st.info("Please check your inbox and follow the instructions in the email to reset your password.")
                        st.markdown("**What's next?**")
                        st.markdown("""
                        1. Check your email inbox (and spam folder)
                        2. Click the reset link in the email
                        3. Follow the instructions to create a new password
                        4. Return here to login with your new password
                        """)
                    else:
                        st.error(f"❌ Failed to send reset email: {result['error']}")
                        st.info("Please make sure the email address is correct and that you have an account with us.")
                else:
                    st.error("Please enter your email address")
            
            # Back to login link
            if st.button("Back to Login", use_container_width=True, type="secondary"):
                st.session_state.auth_tab = "login"
                st.rerun()

    # Footer
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        🔒 Your data is secured with Firebase Authentication<br>
    </div>
    """, unsafe_allow_html=True)        

# Helper functions (unchanged)
def check_authentication():
    return st.session_state.get("authenticated", False)

def logout():
    auth_keys = ["authenticated", "user_email", "username", "login_time", "role", "user_id", "id_token", "auth_tab"]
    for key in auth_keys:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def get_current_user():
    if check_authentication():
        return {
            "username": st.session_state.get("username"),
            "email": st.session_state.get("user_email"),
            "role": st.session_state.get("role", "user"),
            "login_time": st.session_state.get("login_time")
        }
    return None

def is_admin_user(email: str) -> bool:
    admin_emails = [
        "lolof148@gmail.com",
        # Add your admin emails here
    ]
    return email in admin_emails

def update_user_role():
    """Update user role if they are admin."""
    user = get_current_user()
    if user and is_admin_user(user["email"]):
        st.session_state.role = "admin"

def ensure_valid_token():
    """Ensure the user has a valid session."""
    return check_authentication()