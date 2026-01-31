"""Authentication utilities using Supabase with cookie-based session persistence."""
import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import Optional
import json

load_dotenv()

# Cookie key for session persistence
SESSION_COOKIE_KEY = "saas_dashboard_session"


def get_supabase_client() -> Client:
    """Initialize and return Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        st.error("⚠️ Supabase credentials not found. Please check your .env file.")
        st.stop()
    
    return create_client(url, key)


def _get_cookie_manager():
    """Get the cookie manager instance (cached per session)."""
    try:
        from extra_streamlit_components import CookieManager
        return CookieManager(key="saas_cookie_manager")
    except Exception as e:
        print(f"[Session] Cookie manager error: {e}")
        return None


def _save_session_cookie(access_token: str, refresh_token: str) -> bool:
    """Save session tokens to browser cookie.
    
    Args:
        access_token: Supabase access token
        refresh_token: Supabase refresh token
        
    Returns:
        True if save was initiated
    """
    try:
        cookie_mgr = _get_cookie_manager()
        if not cookie_mgr:
            return False
        
        session_data = json.dumps({
            "access_token": access_token,
            "refresh_token": refresh_token
        })
        
        cookie_mgr.set(SESSION_COOKIE_KEY, session_data, max_age=86400)  # 24 hours
        return True
    except Exception as e:
        print(f"[Session] Save cookie error: {e}")
        return False


def _load_session_cookie() -> Optional[dict]:
    """Load session tokens from browser cookie.
    
    Returns:
        Dict with access_token and refresh_token if found,
        None if no cookie found.
    """
    try:
        cookie_mgr = _get_cookie_manager()
        if not cookie_mgr:
            return None
        
        data = cookie_mgr.get(SESSION_COOKIE_KEY)
        
        if data and isinstance(data, str):
            return json.loads(data)
        elif data and isinstance(data, dict):
            return data
        return None
    except Exception as e:
        print(f"[Session] Load cookie error: {e}")
        return None


def _clear_session_cookie() -> bool:
    """Clear session cookie from browser.
    
    Returns:
        True if clear was initiated
    """
    try:
        cookie_mgr = _get_cookie_manager()
        if not cookie_mgr:
            return False
        
        cookie_mgr.delete(SESSION_COOKIE_KEY)
        return True
    except Exception as e:
        print(f"[Session] Clear cookie error: {e}")
        return False


def login(email: str, password: str) -> bool:
    """Login user with email and password.
    
    Args:
        email: User email
        password: User password
        
    Returns:
        True if login successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user and response.session:
            st.session_state.user = response.user
            st.session_state.authenticated = True
            st.session_state.access_token = response.session.access_token
            st.session_state.refresh_token = response.session.refresh_token
            
            # Save to cookie for persistence across page refreshes
            _save_session_cookie(
                response.session.access_token,
                response.session.refresh_token
            )
            
            return True
        return False
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return False


def signup(email: str, password: str) -> bool:
    """Sign up new user.
    
    Args:
        email: User email
        password: User password
        
    Returns:
        True if signup successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            st.success("✅ Account created! Please check your email to verify.")
            
            # If session is available (email confirmation disabled), save it
            if response.session:
                st.session_state.user = response.user
                st.session_state.authenticated = True
                st.session_state.access_token = response.session.access_token
                st.session_state.refresh_token = response.session.refresh_token
                
                _save_session_cookie(
                    response.session.access_token,
                    response.session.refresh_token
                )
            
            return True
        return False
    except Exception as e:
        st.error(f"Signup failed: {str(e)}")
        return False


def logout():
    """Logout current user and clear session cookie.
    
    Clears both Streamlit session state and browser cookie.
    """
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
        
        # Clear Streamlit session state
        st.session_state.authenticated = False
        st.session_state.user = None
        if 'access_token' in st.session_state:
            del st.session_state.access_token
        if 'refresh_token' in st.session_state:
            del st.session_state.refresh_token
        
        # Clear browser cookie
        _clear_session_cookie()
        
    except Exception as e:
        st.error(f"Logout failed: {str(e)}")


def check_stored_session() -> bool:
    """Check for stored session in cookie and restore if valid.
    
    This is called on page load to restore authentication from browser cookie.
    
    Returns:
        True if session was restored, False otherwise
    """
    # Skip if already authenticated
    if st.session_state.get("authenticated"):
        return True
    
    # Skip if we already confirmed no session
    if st.session_state.get("_session_check_done"):
        return False
    
    # Load tokens from cookie
    session_data = _load_session_cookie()
    
    if not session_data or 'access_token' not in session_data:
        st.session_state._session_check_done = True
        return False
    
    # Try to restore the session with stored tokens
    try:
        supabase = get_supabase_client()
        
        response = supabase.auth.set_session(
            session_data['access_token'],
            session_data['refresh_token']
        )
        
        if response.user and response.session:
            # Restore session state
            st.session_state.user = response.user
            st.session_state.authenticated = True
            st.session_state.access_token = response.session.access_token
            st.session_state.refresh_token = response.session.refresh_token
            st.session_state._session_check_done = True
            
            # Update cookie with refreshed tokens if changed
            if response.session.access_token != session_data['access_token']:
                _save_session_cookie(
                    response.session.access_token,
                    response.session.refresh_token
                )
            
            return True
        else:
            _clear_session_cookie()
            st.session_state._session_check_done = True
            return False
            
    except Exception as e:
        print(f"[Session] Restore error: {e}")
        _clear_session_cookie()
        st.session_state._session_check_done = True
        return False


def check_authentication() -> bool:
    """Check if user is authenticated.
    
    Returns:
        True if user is authenticated, False otherwise
    """
    return st.session_state.get("authenticated", False)
