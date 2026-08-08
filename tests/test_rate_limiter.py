
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.rate_limiter import check_rate_limit, ROLE_LIMITS

def test_allows_within_limit():
    result = check_rate_limit("test_user_1", "user")
    assert result["allowed"] is True

def test_role_limits_correct():
    assert ROLE_LIMITS["user"]    < ROLE_LIMITS["premium"]
    assert ROLE_LIMITS["premium"] < ROLE_LIMITS["admin"]

def test_remaining_decreases():
    r1 = check_rate_limit("test_user_2", "user")
    r2 = check_rate_limit("test_user_2", "user")
    assert r2["remaining"] <= r1["remaining"]

def test_limit_reflects_role():
    r_user  = check_rate_limit("test_user_3", "user")
    r_admin = check_rate_limit("test_user_4", "admin")
    assert r_admin["limit"] > r_user["limit"]
