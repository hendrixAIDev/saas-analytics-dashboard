# Tests

Comprehensive user journey tests for the SaaS Analytics Dashboard.

## Running Tests

### Install test dependencies
```bash
pip install -r requirements-dev.txt
```

### Run all tests
```bash
pytest tests/
```

### Run with coverage
```bash
pytest tests/ --cov=utils --cov-report=html
```

### Run specific test
```bash
pytest tests/test_user_journeys.py::test_login_flow_success -v
```

## Test Coverage

The test suite covers:

1. **Signup Flow** - User registration with Supabase auth
2. **Login Flow** - Authentication with email/password
3. **Session Persistence** - localStorage token storage and restoration
4. **Dashboard Data Loading** - Fetching metrics and revenue data
5. **AI Insights Generation** - Claude API integration and fallbacks
6. **Logout & Cleanup** - Session termination and storage cleanup
7. **Full User Journey** - End-to-end integration test

All tests use mocks - no actual API credentials required.

## Test Structure

- `conftest.py` - Shared pytest configuration
- `test_user_journeys.py` - Main test suite with all user journeys
- Fixtures provide mock Supabase client, Anthropic client, and sample data

## Mocking Strategy

Tests mock external dependencies:
- **Supabase**: Auth methods and data queries
- **Anthropic**: Claude API message generation
- **streamlit_js_eval**: localStorage interactions
- **Streamlit session_state**: In-memory session management

This allows tests to run without environment variables or API keys.
