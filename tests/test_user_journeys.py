"""
User Journey Tests for SaaS Analytics Dashboard

Tests cover:
1. Signup flow (with mock Supabase)
2. Login flow
3. Session persistence (token saved/restored from localStorage)
4. Dashboard data loading after auth
5. AI Insights generation (with mock Claude API)
6. Logout and session cleanup
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client with auth and data methods."""
    client = Mock()
    
    # Mock auth responses
    mock_user = Mock()
    mock_user.id = "test-user-123"
    mock_user.email = "test@example.com"
    
    mock_session = Mock()
    mock_session.access_token = "test-access-token-abc123"
    mock_session.refresh_token = "test-refresh-token-xyz789"
    
    # Mock auth methods
    client.auth.sign_up.return_value = Mock(user=mock_user, session=mock_session)
    client.auth.sign_in_with_password.return_value = Mock(user=mock_user, session=mock_session)
    client.auth.set_session.return_value = Mock(user=mock_user, session=mock_session)
    client.auth.sign_out.return_value = None
    
    # Mock data queries
    mock_revenue_data = [
        {
            'month': (datetime.now() - timedelta(days=30*i)).strftime('%Y-%m-01'),
            'mrr': 50000 + (i * 1000),
            'customer_count': 100 + (i * 5),
            'new_customers': 10,
            'churn_count': 2
        }
        for i in range(6)
    ]
    
    mock_plan_data = [
        {'plan_tier': 'Basic', 'revenue': 10000, 'customer_count': 50},
        {'plan_tier': 'Pro', 'revenue': 30000, 'customer_count': 40},
        {'plan_tier': 'Enterprise', 'revenue': 15000, 'customer_count': 10}
    ]
    
    # Mock table queries
    client.table.return_value.select.return_value.execute.return_value.data = mock_revenue_data
    
    return client


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic Claude API client."""
    client = Mock()
    
    # Mock message response
    mock_message = Mock()
    mock_content = Mock()
    mock_content.text = "Your SaaS metrics show healthy growth with MRR increasing 15% month-over-month. Customer acquisition is strong, and churn remains low at 2%. Focus on expanding your Enterprise tier for maximum revenue impact."
    mock_message.content = [mock_content]
    
    client.messages.create.return_value = mock_message
    
    return client


@pytest.fixture
def sample_metrics():
    """Sample SaaS metrics for testing."""
    return {
        'mrr': 55000,
        'mrr_growth': 10.0,
        'customers': 115,
        'customer_growth': 8.5,
        'churn_rate': 2.1,
        'new_customers': 12
    }


@pytest.fixture
def sample_revenue_df():
    """Sample revenue DataFrame for testing."""
    data = {
        'month': pd.date_range(start='2024-01-01', periods=6, freq='MS'),
        'mrr': [45000, 47000, 49000, 51000, 53000, 55000],
        'customer_count': [90, 95, 100, 105, 110, 115],
        'new_customers': [10, 12, 11, 13, 10, 12],
        'churn_count': [2, 3, 1, 2, 2, 3]
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_plan_df():
    """Sample plan DataFrame for testing."""
    data = {
        'month': ['2024-06-01', '2024-06-01', '2024-06-01'],
        'plan_tier': ['Basic', 'Pro', 'Enterprise'],
        'revenue': [12000, 33000, 10000],
        'customer_count': [60, 45, 10]
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_streamlit_session():
    """Mock Streamlit session state."""
    session = {}
    with patch.object(st, 'session_state', session):
        yield session


# ============================================================================
# TEST 1: SIGNUP FLOW
# ============================================================================

@patch('utils.auth.get_supabase_client')
@patch('utils.auth._save_session_to_storage')
def test_signup_flow_success(mock_save_storage, mock_get_client, mock_supabase_client, mock_streamlit_session):
    """Test successful user signup flow."""
    from utils.auth import signup
    
    # Setup
    mock_get_client.return_value = mock_supabase_client
    mock_save_storage.return_value = True
    
    # Execute signup
    result = signup("newuser@example.com", "password123")
    
    # Assertions
    assert result is True
    mock_supabase_client.auth.sign_up.assert_called_once_with({
        "email": "newuser@example.com",
        "password": "password123"
    })
    
    # Check session state was set
    assert mock_streamlit_session.get('authenticated') is True
    assert mock_streamlit_session.get('user') is not None
    assert mock_streamlit_session['user'].email == "test@example.com"
    
    # Check localStorage save was called
    mock_save_storage.assert_called_once()


@patch('utils.auth.get_supabase_client')
def test_signup_flow_failure(mock_get_client, mock_streamlit_session):
    """Test signup flow with invalid credentials."""
    from utils.auth import signup
    
    # Setup - simulate signup failure
    mock_client = Mock()
    mock_client.auth.sign_up.side_effect = Exception("Email already exists")
    mock_get_client.return_value = mock_client
    
    # Execute signup
    result = signup("existing@example.com", "password123")
    
    # Assertions
    assert result is False
    assert mock_streamlit_session.get('authenticated') is not True


# ============================================================================
# TEST 2: LOGIN FLOW
# ============================================================================

@patch('utils.auth.get_supabase_client')
@patch('utils.auth._save_session_to_storage')
def test_login_flow_success(mock_save_storage, mock_get_client, mock_supabase_client, mock_streamlit_session):
    """Test successful user login flow."""
    from utils.auth import login
    
    # Setup
    mock_get_client.return_value = mock_supabase_client
    mock_save_storage.return_value = True
    
    # Execute login
    result = login("test@example.com", "password123")
    
    # Assertions
    assert result is True
    mock_supabase_client.auth.sign_in_with_password.assert_called_once_with({
        "email": "test@example.com",
        "password": "password123"
    })
    
    # Check session state
    assert mock_streamlit_session['authenticated'] is True
    assert mock_streamlit_session['user'].email == "test@example.com"
    assert mock_streamlit_session['access_token'] == "test-access-token-abc123"
    assert mock_streamlit_session['refresh_token'] == "test-refresh-token-xyz789"
    
    # Check localStorage save was called
    mock_save_storage.assert_called_once_with(
        "test-access-token-abc123",
        "test-refresh-token-xyz789"
    )


@patch('utils.auth.get_supabase_client')
def test_login_flow_invalid_credentials(mock_get_client, mock_streamlit_session):
    """Test login flow with invalid credentials."""
    from utils.auth import login
    
    # Setup - simulate login failure
    mock_client = Mock()
    mock_client.auth.sign_in_with_password.side_effect = Exception("Invalid credentials")
    mock_get_client.return_value = mock_client
    
    # Execute login
    result = login("wrong@example.com", "wrongpassword")
    
    # Assertions
    assert result is False
    assert mock_streamlit_session.get('authenticated') is not True


# ============================================================================
# TEST 3: SESSION PERSISTENCE
# ============================================================================

@patch('utils.auth.get_supabase_client')
@patch('utils.auth._load_session_from_storage')
@patch('utils.auth._save_session_to_storage')
def test_session_restore_from_localstorage(
    mock_save_storage,
    mock_load_storage,
    mock_get_client,
    mock_supabase_client,
    mock_streamlit_session
):
    """Test session restoration from localStorage on page load."""
    from utils.auth import check_stored_session
    
    # Setup - simulate existing session in localStorage
    mock_load_storage.return_value = {
        'access_token': 'stored-access-token',
        'refresh_token': 'stored-refresh-token'
    }
    mock_get_client.return_value = mock_supabase_client
    mock_save_storage.return_value = True
    
    # Execute session check
    result = check_stored_session()
    
    # Assertions
    assert result is True
    
    # Check Supabase set_session was called with stored tokens
    mock_supabase_client.auth.set_session.assert_called_once_with(
        'stored-access-token',
        'stored-refresh-token'
    )
    
    # Check session state was restored
    assert mock_streamlit_session['authenticated'] is True
    assert mock_streamlit_session['user'] is not None
    assert mock_streamlit_session['_session_check_done'] is True


@patch('utils.auth._load_session_from_storage')
@patch('utils.auth._clear_session_storage')
def test_session_restore_no_stored_session(
    mock_clear_storage,
    mock_load_storage,
    mock_streamlit_session
):
    """Test session restoration when no session exists in localStorage."""
    from utils.auth import check_stored_session
    
    # Setup - no stored session
    mock_load_storage.return_value = None
    
    # Execute session check
    result = check_stored_session()
    
    # Assertions
    assert result is False
    assert mock_streamlit_session.get('authenticated') is not True


@patch('utils.auth.get_supabase_client')
@patch('utils.auth._load_session_from_storage')
@patch('utils.auth._clear_session_storage')
def test_session_restore_expired_token(
    mock_clear_storage,
    mock_load_storage,
    mock_get_client,
    mock_streamlit_session
):
    """Test session restoration with expired/invalid token."""
    from utils.auth import check_stored_session
    
    # Setup - simulate expired token
    mock_load_storage.return_value = {
        'access_token': 'expired-token',
        'refresh_token': 'expired-refresh'
    }
    
    mock_client = Mock()
    mock_client.auth.set_session.side_effect = Exception("Token expired")
    mock_get_client.return_value = mock_client
    
    # Execute session check
    result = check_stored_session()
    
    # Assertions
    assert result is False
    mock_clear_storage.assert_called_once()
    assert mock_streamlit_session.get('authenticated') is not True


# ============================================================================
# TEST 4: DASHBOARD DATA LOADING
# ============================================================================

@patch('utils.database.get_supabase_client')
def test_dashboard_data_loading(mock_get_client, mock_supabase_client):
    """Test dashboard data loading after authentication."""
    from utils.database import get_monthly_revenue, get_current_metrics
    
    # Setup
    mock_get_client.return_value = mock_supabase_client
    
    # Test monthly revenue loading
    revenue_df = get_monthly_revenue(mock_supabase_client, months=6)
    assert len(revenue_df) > 0
    assert 'mrr' in revenue_df.columns
    assert 'customer_count' in revenue_df.columns
    
    # Test current metrics loading
    metrics = get_current_metrics(mock_supabase_client)
    assert metrics is not None
    assert 'mrr' in metrics


# ============================================================================
# TEST 5: AI INSIGHTS GENERATION
# ============================================================================

@patch('utils.ai_insights.get_claude_client')
def test_ai_insights_generation_success(
    mock_get_claude,
    mock_anthropic_client,
    sample_metrics,
    sample_revenue_df
):
    """Test AI insights generation with valid API key."""
    from utils.ai_insights import generate_executive_summary
    
    # Setup
    mock_get_claude.return_value = mock_anthropic_client
    
    # Execute
    summary = generate_executive_summary(sample_metrics, sample_revenue_df)
    
    # Assertions
    assert summary is not None
    assert len(summary) > 0
    assert "growth" in summary.lower() or "revenue" in summary.lower()
    
    # Check API was called
    mock_anthropic_client.messages.create.assert_called_once()
    call_args = mock_anthropic_client.messages.create.call_args
    assert call_args.kwargs['model'] == "claude-sonnet-4-20250514"


@patch('utils.ai_insights.get_claude_client')
def test_ai_insights_no_api_key(mock_get_claude, sample_metrics, sample_revenue_df):
    """Test AI insights graceful degradation without API key."""
    from utils.ai_insights import generate_executive_summary
    
    # Setup - no API client
    mock_get_claude.return_value = None
    
    # Execute
    summary = generate_executive_summary(sample_metrics, sample_revenue_df)
    
    # Assertions
    assert summary is not None
    assert "Unavailable" in summary or "unavailable" in summary
    assert str(sample_metrics['mrr']) in summary  # Should show basic metrics


@patch('utils.ai_insights.get_claude_client')
def test_ai_question_answering(
    mock_get_claude,
    mock_anthropic_client,
    sample_metrics,
    sample_revenue_df,
    sample_plan_df
):
    """Test AI-powered question answering."""
    from utils.ai_insights import answer_metric_question
    
    # Setup
    mock_get_claude.return_value = mock_anthropic_client
    
    # Execute
    answer = answer_metric_question(
        "What's my biggest growth opportunity?",
        sample_metrics,
        sample_revenue_df,
        sample_plan_df
    )
    
    # Assertions
    assert answer is not None
    assert len(answer) > 0
    
    # Check API was called with question
    mock_anthropic_client.messages.create.assert_called_once()


@patch('utils.ai_insights.get_claude_client')
def test_ai_insights_oauth_token_detection(mock_get_claude):
    """Test that OAuth tokens are properly detected and rejected."""
    from utils.ai_insights import get_claude_client
    
    # Setup - simulate OAuth token in environment
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'sk-ant-oat01-xxxxx'}):
        client = get_claude_client()
        
        # Should return None and show warning
        assert client is None


# ============================================================================
# TEST 6: LOGOUT AND SESSION CLEANUP
# ============================================================================

@patch('utils.auth.get_supabase_client')
@patch('utils.auth._clear_session_storage')
def test_logout_and_cleanup(mock_clear_storage, mock_get_client, mock_supabase_client, mock_streamlit_session):
    """Test logout flow and session cleanup."""
    from utils.auth import logout
    
    # Setup - simulate authenticated session
    mock_streamlit_session['authenticated'] = True
    mock_streamlit_session['user'] = Mock(email="test@example.com")
    mock_streamlit_session['access_token'] = "token123"
    mock_streamlit_session['refresh_token'] = "refresh456"
    
    mock_get_client.return_value = mock_supabase_client
    mock_clear_storage.return_value = True
    
    # Execute logout
    logout()
    
    # Assertions
    assert mock_streamlit_session['authenticated'] is False
    assert mock_streamlit_session['user'] is None
    assert 'access_token' not in mock_streamlit_session
    assert 'refresh_token' not in mock_streamlit_session
    
    # Check Supabase sign_out was called
    mock_supabase_client.auth.sign_out.assert_called_once()
    
    # Check localStorage was cleared
    mock_clear_storage.assert_called_once()


# ============================================================================
# INTEGRATION TEST: FULL USER JOURNEY
# ============================================================================

@patch('utils.auth.get_supabase_client')
@patch('utils.auth._save_session_to_storage')
@patch('utils.auth._load_session_from_storage')
@patch('utils.auth._clear_session_storage')
@patch('utils.ai_insights.get_claude_client')
def test_full_user_journey(
    mock_get_claude,
    mock_clear_storage,
    mock_load_storage,
    mock_save_storage,
    mock_get_client,
    mock_supabase_client,
    mock_anthropic_client,
    mock_streamlit_session,
    sample_metrics,
    sample_revenue_df
):
    """Integration test: Full user journey from signup to logout."""
    from utils.auth import signup, check_stored_session, logout, check_authentication
    from utils.ai_insights import generate_executive_summary
    
    # Setup mocks
    mock_get_client.return_value = mock_supabase_client
    mock_save_storage.return_value = True
    mock_get_claude.return_value = mock_anthropic_client
    
    # Step 1: User signs up
    signup_result = signup("journey@example.com", "password123")
    assert signup_result is True
    assert check_authentication() is True
    
    # Step 2: Session is saved to localStorage
    mock_save_storage.assert_called()
    
    # Step 3: Simulate page refresh - session should restore
    mock_streamlit_session.clear()
    mock_streamlit_session['_session_check_done'] = False
    mock_load_storage.return_value = {
        'access_token': 'test-access-token-abc123',
        'refresh_token': 'test-refresh-token-xyz789'
    }
    
    restored = check_stored_session()
    assert restored is True
    assert check_authentication() is True
    
    # Step 4: User views AI insights
    summary = generate_executive_summary(sample_metrics, sample_revenue_df)
    assert summary is not None
    assert len(summary) > 0
    
    # Step 5: User logs out
    logout()
    assert check_authentication() is False
    mock_clear_storage.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
