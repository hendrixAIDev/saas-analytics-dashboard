"""Authentication utilities using Supabase."""
import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import Optional
import json

load_dotenv()

# Session storage key for browser localStorage
SESSION_STORAGE_KEY = "saas_dashboard_session"

def get_supabase_client() -> Client:
    """Initialize and return Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        st.error("⚠️ Supabase credentials not found. Please check your .env file.")
        st.stop()
    
    return create_client(url, key)

def _save_session_to_storage(access_token: str, refresh_token: str) -> bool:
    """Save session tokens to browser localStorage.
    
    Args:
        access_token: Supabase access token
        refresh_token: Supabase refresh token
        
    Returns:
        True if save was initiated
    """
    try:
        from streamlit_js_eval import streamlit_js_eval
        
        # Use incrementing counter to force re-render
        if "_session_save_counter" not in st.session_state:
            st.session_state._session_save_counter = 0
        st.session_state._session_save_counter += 1
        
        # Store as JSON with both tokens
        session_data = json.dumps({
            "access_token": access_token,
            "refresh_token": refresh_token
        })
        
        # Escape quotes for JS
        session_data_escaped = session_data.replace("'", "\\'").replace('"', '\\"')
        
        js_code = f"""
        (function() {{
            try {{
                localStorage.setItem('{SESSION_STORAGE_KEY}', '{session_data_escaped}');
                console.log('[SaaS Dashboard] Session saved to localStorage');
                return true;
            }} catch (e) {{
                console.error('[SaaS Dashboard] Session save error:', e);
                return false;
            }}
        }})()
        """
        
        streamlit_js_eval(
            js_expressions=js_code,
            key=f"session_save_{st.session_state._session_save_counter}"
        )
        return True
    except Exception as e:
        print(f"[Session] Save error: {e}")
        return False


def _load_session_from_storage() -> Optional[dict]:
    """Load session tokens from browser localStorage.
    
    Returns:
        Dict with access_token and refresh_token if found,
        empty dict {} if JS executed but no session stored,
        None if JS hasn't executed yet (first render).
    """
    try:
        from streamlit_js_eval import streamlit_js_eval
        
        # Return "__NO_SESSION__" sentinel when no data found,
        # so we can distinguish "JS not run yet (None)" from "no stored session"
        js_code = f"""
        (function() {{
            try {{
                const data = localStorage.getItem('{SESSION_STORAGE_KEY}');
                console.log('[SaaS Dashboard] Loading session:', data ? 'found' : 'not found');
                return data || '__NO_SESSION__';
            }} catch (e) {{
                console.error('[SaaS Dashboard] Session load error:', e);
                return '__NO_SESSION__';
            }}
        }})()
        """
        
        result = streamlit_js_eval(js_expressions=js_code, key="session_loader")
        
        if result is None:
            # JS component hasn't rendered yet - first render cycle
            return None
        
        if result == '__NO_SESSION__':
            # JS executed but no stored session found
            return {}
        
        return json.loads(result)
    except Exception as e:
        print(f"[Session] Load error: {e}")
        return {}


def _clear_session_storage() -> bool:
    """Clear session tokens from browser localStorage.
    
    Returns:
        True if clear was initiated
    """
    try:
        from streamlit_js_eval import streamlit_js_eval
        
        if "_session_clear_counter" not in st.session_state:
            st.session_state._session_clear_counter = 0
        st.session_state._session_clear_counter += 1
        
        js_code = f"""
        (function() {{
            try {{
                localStorage.removeItem('{SESSION_STORAGE_KEY}');
                console.log('[SaaS Dashboard] Session cleared from localStorage');
                return true;
            }} catch (e) {{
                console.error('[SaaS Dashboard] Session clear error:', e);
                return false;
            }}
        }})()
        """
        
        streamlit_js_eval(
            js_expressions=js_code,
            key=f"session_clear_{st.session_state._session_clear_counter}"
        )
        return True
    except Exception as e:
        print(f"[Session] Clear error: {e}")
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
            
            # Save to localStorage for persistence
            _save_session_to_storage(
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
                
                _save_session_to_storage(
                    response.session.access_token,
                    response.session.refresh_token
                )
            
            return True
        return False
    except Exception as e:
        st.error(f"Signup failed: {str(e)}")
        return False

def logout():
    """Logout current user and clear session storage.
    
    Clears both Streamlit session state and browser localStorage.
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
        
        # Clear browser localStorage
        _clear_session_storage()
        
    except Exception as e:
        st.error(f"Logout failed: {str(e)}")

def check_stored_session() -> bool:
    """Check for stored session in localStorage and restore if valid.
    
    This is called on page load to restore authentication from browser storage.
    Uses a two-phase approach:
    - Phase 1 (first render): streamlit_js_eval renders but returns None. 
      We return "pending" status so the caller can show a loading state.
    - Phase 2 (second render): JS has executed and returns actual data.
    
    Returns:
        True if session was restored, False otherwise.
        When _load returns None (JS pending), sets _session_pending flag.
    """
    # Skip if already authenticated
    if st.session_state.get("authenticated"):
        return True
    
    # Check if we've already confirmed no session exists
    if st.session_state.get("_session_check_done"):
        return False
    
    # Load tokens from localStorage
    session_data = _load_session_from_storage()
    
    # None = JS component hasn't rendered yet (first render cycle)
    # We need a rerun for the JS to execute and return a value
    if session_data is None:
        st.session_state._session_pending = True
        return False
    
    # Empty dict = JS executed but no stored session
    if not session_data or 'access_token' not in session_data:
        st.session_state._session_check_done = True
        st.session_state._session_pending = False
        return False
    
    # We have stored tokens — try to restore the session
    st.session_state._session_pending = False
    
    try:
        supabase = get_supabase_client()
        
        # Set the session with stored tokens
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
            
            # Update localStorage with refreshed tokens (if changed)
            if response.session.access_token != session_data['access_token']:
                _save_session_to_storage(
                    response.session.access_token,
                    response.session.refresh_token
                )
            
            return True
        else:
            # Invalid/expired session - clear it
            _clear_session_storage()
            st.session_state._session_check_done = True
            return False
            
    except Exception as e:
        print(f"[Session] Restore error: {e}")
        _clear_session_storage()
        st.session_state._session_check_done = True
        return False


def check_authentication() -> bool:
    """Check if user is authenticated.
    
    Returns:
        True if user is authenticated, False otherwise
    """
    return st.session_state.get("authenticated", False)
