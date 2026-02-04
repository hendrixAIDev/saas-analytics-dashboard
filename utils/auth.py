"""Authentication utilities using Supabase."""
import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

def get_supabase_client() -> Client:
    """Initialize and return Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        st.error("⚠️ Supabase credentials not found. Please check your .env file.")
        st.stop()
    
    return create_client(url, key)

def login(email: str, password: str) -> bool:
    """Login user with email and password."""
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            st.session_state.user = response.user
            st.session_state.authenticated = True
            return True
        return False
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return False

def signup(email: str, password: str) -> bool:
    """Sign up new user and automatically log them in."""
    try:
        supabase = get_supabase_client()
        
        # Check if email confirmation is required (production mode)
        require_email_confirmation = os.getenv("REQUIRE_EMAIL_CONFIRMATION", "false").lower() == "true"
        
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            if require_email_confirmation:
                # Production: require email verification before login
                st.success("✅ Account created! Please check your email to verify before logging in.")
                return True
            else:
                # Development/staging: auto-login after signup
                # Check if user is already confirmed or if Supabase auto-confirmed
                if response.session:
                    # User was auto-confirmed, we have a session
                    st.session_state.user = response.user
                    st.session_state.authenticated = True
                    st.success("✅ Account created! You're now logged in.")
                    return True
                else:
                    # Try to sign in immediately (works if email confirmation is disabled in Supabase)
                    try:
                        login_response = supabase.auth.sign_in_with_password({
                            "email": email,
                            "password": password
                        })
                        if login_response.user:
                            st.session_state.user = login_response.user
                            st.session_state.authenticated = True
                            st.success("✅ Account created! You're now logged in.")
                            return True
                    except:
                        pass
                    
                    # Fallback: show verification message if auto-login failed
                    st.success("✅ Account created! Please check your email to verify, then log in.")
                    return True
        return False
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            st.error("❌ This email is already registered. Please log in instead.")
        else:
            st.error(f"Signup failed: {error_msg}")
        return False

def logout():
    """Logout current user."""
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
        st.session_state.authenticated = False
        st.session_state.user = None
    except Exception as e:
        st.error(f"Logout failed: {str(e)}")

def check_authentication() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get("authenticated", False)
