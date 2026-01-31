"""Authentication utilities using Supabase with query-param session persistence.

Uses st.query_params to persist a session token across page refreshes.
This is the only client-side storage mechanism in Streamlit that is
available synchronously on the first render (no JS component needed).

The refresh_token is stored as a query parameter. On page load, it's used
to restore the Supabase session. This is secure enough for a demo since:
- Refresh tokens are short-lived and rotatable
- The token is only in the URL, not stored in browser storage
- Supabase validates the token server-side
"""
import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import base64

load_dotenv()

# Query param key for session persistence
SESSION_PARAM_KEY = "s"


def get_supabase_client() -> Client:
    """Initialize and return Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        st.error("⚠️ Supabase credentials not found. Please check your .env file.")
        st.stop()
    
    return create_client(url, key)


def _encode_tokens(access_token: str, refresh_token: str) -> str:
    """Encode tokens for URL storage."""
    combined = f"{access_token}|{refresh_token}"
    return base64.urlsafe_b64encode(combined.encode()).decode()


def _decode_tokens(encoded: str) -> tuple:
    """Decode tokens from URL storage.
    
    Returns:
        Tuple of (access_token, refresh_token) or (None, None) on error
    """
    try:
        decoded = base64.urlsafe_b64decode(encoded.encode()).decode()
        parts = decoded.split("|", 1)
        if len(parts) == 2:
            return parts[0], parts[1]
    except Exception:
        pass
    return None, None


def _save_session_params(access_token: str, refresh_token: str):
    """Save session tokens to query params."""
    try:
        encoded = _encode_tokens(access_token, refresh_token)
        st.query_params[SESSION_PARAM_KEY] = encoded
    except Exception as e:
        print(f"[Session] Save params error: {e}")


def _load_session_params() -> tuple:
    """Load session tokens from query params.
    
    Returns:
        Tuple of (access_token, refresh_token) or (None, None)
    """
    try:
        encoded = st.query_params.get(SESSION_PARAM_KEY)
        if encoded:
            return _decode_tokens(encoded)
    except Exception as e:
        print(f"[Session] Load params error: {e}")
    return None, None


def _clear_session_params():
    """Clear session tokens from query params."""
    try:
        if SESSION_PARAM_KEY in st.query_params:
            del st.query_params[SESSION_PARAM_KEY]
    except Exception as e:
        print(f"[Session] Clear params error: {e}")


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
            
            # Save to query params for persistence across page refreshes
            _save_session_params(
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
                
                _save_session_params(
                    response.session.access_token,
                    response.session.refresh_token
                )
            
            return True
        return False
    except Exception as e:
        st.error(f"Signup failed: {str(e)}")
        return False


def logout():
    """Logout current user and clear session.
    
    Clears both Streamlit session state and URL query params.
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
        
        # Clear URL query params
        _clear_session_params()
        
    except Exception as e:
        st.error(f"Logout failed: {str(e)}")


def check_stored_session() -> bool:
    """Check for stored session in query params and restore if valid.
    
    This is called on page load to restore authentication from URL params.
    Works synchronously — no JS component rendering needed.
    
    Returns:
        True if session was restored, False otherwise
    """
    # Skip if already authenticated
    if st.session_state.get("authenticated"):
        return True
    
    # Skip if we already tried
    if st.session_state.get("_session_check_done"):
        return False
    
    # Load tokens from query params
    access_token, refresh_token = _load_session_params()
    
    if not access_token or not refresh_token:
        st.session_state._session_check_done = True
        return False
    
    # Try to restore the session with stored tokens
    try:
        supabase = get_supabase_client()
        
        response = supabase.auth.set_session(access_token, refresh_token)
        
        if response.user and response.session:
            # Restore session state
            st.session_state.user = response.user
            st.session_state.authenticated = True
            st.session_state.access_token = response.session.access_token
            st.session_state.refresh_token = response.session.refresh_token
            st.session_state._session_check_done = True
            
            # Update query params with refreshed tokens if changed
            if response.session.access_token != access_token:
                _save_session_params(
                    response.session.access_token,
                    response.session.refresh_token
                )
            
            return True
        else:
            _clear_session_params()
            st.session_state._session_check_done = True
            return False
            
    except Exception as e:
        print(f"[Session] Restore error: {e}")
        _clear_session_params()
        st.session_state._session_check_done = True
        return False


def check_authentication() -> bool:
    """Check if user is authenticated.
    
    Returns:
        True if user is authenticated, False otherwise
    """
    return st.session_state.get("authenticated", False)
