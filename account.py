import streamlit as st
import login
import requests
import json
from datetime import datetime

def delete_firebase_user(id_token: str) -> dict:
    """Delete user account from Firebase."""
    try:
        firebase_config = login.firebase_config
        api_key = firebase_config["apiKey"]
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:delete?key={api_key}"
        
        payload = {
            "idToken": id_token
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": "Account deleted successfully"
            }
        else:
            error_data = response.json()
            return {
                "success": False,
                "error": error_data.get("error", {}).get("message", "Account deletion failed")
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def app():
    """Account management page."""
    st.title("👤 Account Management")
    
    # Get current user from login module
    user_info = login.get_current_user()
    
    if not user_info:
        st.error("User information not available. Please login again.")
        if st.button("Go to Login"):
            login.logout()
        return
    
    # User Information Section
    st.markdown("### 📋 User Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Username:** {user_info['username']}")
        st.info(f"**Email:** {user_info['email']}")
    
    with col2:
        st.info(f"**Role:** {user_info['role'].title()}")
        if user_info['login_time']:
            login_time = user_info['login_time'].strftime("%Y-%m-%d %H:%M:%S")
            st.info(f"**Last Login:** {login_time}")
    
    st.markdown("---")
    
    # Session Information Section
    st.markdown("### 📊 Session Information")
    
    # Calculate session duration
    if user_info['login_time']:
        session_duration = datetime.now() - user_info['login_time']
        duration_str = str(session_duration).split('.')[0]  # Remove microseconds
    else:
        duration_str = "Unknown"
    
    session_info_data = {
        "Session Duration": duration_str,
        "Authentication Method": "Firebase",
        "Session Status": "Active ✅" if login.check_authentication() else "❌ Expired",
        "User ID": st.session_state.get('user_id', 'N/A')[:8] + "..." if st.session_state.get('user_id') else 'N/A'
    }
    
    for key, value in session_info_data.items():
        st.info(f"**{key}:** {value}")
    
    st.markdown("---")
    
    # Security Information
    st.markdown("### 🔒 Security Information")
    
    security_info = {
        "Authentication Provider": "Firebase",
        "Login Method": "Email/Password",
        "Account Verification": "Verified ✅" if st.session_state.get('user_id') else "Not Verified",
        "Two-Factor Authentication": "Not Enabled"
    }
    
    for key, value in security_info.items():
        st.info(f"**{key}:** {value}")
    
    # Security recommendations
    st.markdown("##### 🛡️ Security Recommendations")
    st.markdown("""
    - Use a strong, unique password
    - Don't share your login credentials
    - Log out from public computers
    - Contact admin if you notice suspicious activity
    """)
    
    st.markdown("---")
    
    # Debug Information (only for admins)
    if user_info['role'] == 'admin':
        st.markdown("### 👨‍💼 Admin Information")
        
        with st.expander("Session State Details"):
            # Filter out sensitive information
            safe_session_state = {}
            for key, value in st.session_state.items():
                if key not in ['id_token', 'refresh_token', 'messages']:  # Don't show sensitive tokens
                    if isinstance(value, datetime):
                        safe_session_state[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        safe_session_state[key] = str(value)
            
            st.json(safe_session_state)
        
        with st.expander("User Data from Login Module"):
            st.json(user_info)
        st.markdown("---")

    # Account Actions Section
    st.markdown("### ⚙️ Account Actions")

    if st.button("🗑️ Delete Account", use_container_width=True, type="secondary"):
        st.session_state.show_delete_confirmation = True
    
    # Delete Account Confirmation
    if st.session_state.get("show_delete_confirmation", False):
        st.markdown("---")
        st.error("⚠️ **DANGER ZONE - Delete Account**")
        
        st.markdown("""
        **This action will permanently:**
        - Delete your Firebase account
        - Remove all your data
        - Revoke access to this application
        - Cannot be undone or reversed
        """)
        
        # Confirmation input
        st.markdown("**Type your email address to confirm deletion:**")
        confirmation_email = st.text_input(
            "Email confirmation", 
            placeholder=f"Type {user_info['email']} to confirm",
            key="delete_confirmation_email"
        )
        
        col_confirm, col_cancel = st.columns(2)
        
        with col_confirm:
            # Only enable confirm button if email matches
            email_matches = confirmation_email == user_info['email']
            confirm_delete = st.button(
                "🗑️ DELETE ACCOUNT", 
                use_container_width=True, 
                type="primary",
                disabled=not email_matches
            )
            
            if confirm_delete and email_matches:
                # Get the ID token for deletion
                id_token = st.session_state.get('id_token')
                
                if id_token:
                    with st.spinner("Deleting account from Firebase..."):
                        result = delete_firebase_user(id_token)
                    
                    if result["success"]:
                        st.success("✅ Account deleted successfully!")
                        st.info("Your Firebase account has been permanently deleted.")
                        st.balloons()
                        
                        # Clear session and redirect to login
                        login.logout()
                    else:
                        st.error(f"❌ Account deletion failed: {result['error']}")
                        st.info("Please try again or contact support if the problem persists.")
                else:
                    st.error("❌ Unable to delete account: No valid authentication token found.")
                    st.info("Please log out and log back in, then try again.")
        
        with col_cancel:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_delete_confirmation = False
                if "delete_confirmation_email" in st.session_state:
                    del st.session_state.delete_confirmation_email
                st.rerun()
        
        # Show email match status
        if confirmation_email:
            if email_matches:
                st.success("✅ Email confirmed - deletion enabled")
            else:
                st.warning("⚠️ Email doesn't match - please type your exact email address")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        🔒 Your data is secured with Firebase Authentication<br>
    </div>
    """, unsafe_allow_html=True)