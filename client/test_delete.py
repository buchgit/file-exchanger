#!/usr/bin/env python
"""Test script to verify delete_user works correctly."""

import sys
sys.path.insert(0, '.')

from api import ApiClient, ApiError

# Configure for remote server
BASE_URL = "http://151.236.10.160:8000"

def test_delete():
    api = ApiClient(BASE_URL)
    
    # Login as admin
    print("Logging in as admin...")
    try:
        result = api.login("admin", "1")
        print(f"Login successful. Token: {result.access_token[:20]}...")
    except ApiError as e:
        print(f"Login failed: {e}")
        return
    
    # List users
    print("\nListing users...")
    try:
        users = api.list_users(result.access_token)
        print(f"Found {len(users)} users:")
        for u in users:
            print(f"  - ID {u.id}: {u.username} (admin={u.is_admin})")
    except ApiError as e:
        print(f"List users failed: {e}")
        return
    
    # Find a non-admin user to delete (not admin, not current user)
    admin_user = None
    for u in users:
        if u.username != "admin" and not u.is_admin:
            admin_user = u
            break
    
    if not admin_user:
        print("\nNo suitable user to delete (only admin found).")
        return
    
    print(f"\nAttempting to delete user '{admin_user.username}' (ID {admin_user.id})...")
    try:
        api.delete_user(result.access_token, admin_user.id)
        print("SUCCESS: User deleted!")
    except ApiError as e:
        print(f"Delete failed: Error {e.status_code}: {e.detail}")
        return
    
    # Verify deletion
    print("\nVerifying deletion...")
    try:
        users_after = api.list_users(result.access_token)
        remaining_ids = [u.id for u in users_after]
        if admin_user.id not in remaining_ids:
            print(f"VERIFIED: User ID {admin_user.id} is no longer in the list.")
        else:
            print(f"WARNING: User ID {admin_user.id} still appears in the list!")
    except ApiError as e:
        print(f"Verification failed: {e}")

if __name__ == "__main__":
    test_delete()
