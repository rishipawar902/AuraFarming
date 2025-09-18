# Registration Debugging Guide

## ✅ Fixed Issues:
1. **Password hashing**: Updated to use bcrypt directly instead of passlib
2. **Language field**: Changed from enum to string with validation
3. **Frontend data format**: Fixed to send `phone` instead of `phone_number`

## 🔧 Current Registration Flow:

### Backend expects (POST /api/v1/auth/register):
```json
{
  "name": "Farmer Name",
  "phone": "9876543210", 
  "password": "password123",
  "language": "en"
}
```

### Response format:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer", 
  "expires_in": 86400
}
```

## 🐛 If registration still fails, check:

### 1. **Phone number validation**:
   - Must start with 6, 7, 8, or 9
   - Must be exactly 10 digits
   - Examples: ✅ "9876543210" ❌ "1234567890"

### 2. **Password validation**:
   - Must be at least 6 characters
   - Examples: ✅ "password123" ❌ "12345"

### 3. **Name validation**:
   - Must be 2-100 characters
   - Examples: ✅ "John Doe" ❌ "A"

### 4. **Language validation**:
   - Must be "en" or "hi"
   - Examples: ✅ "en" ❌ "english"

## 🧪 Test Users Available:
After running add_test_data.sql, you can login with:
- Phone: `9876543210`, Password: `password123` (Ravi Kumar - Dhanbad)
- Phone: `9876543211`, Password: `password123` (Priya Singh - Bokaro) 
- Phone: `9876543212`, Password: `password123` (Suresh Mahto - Ranchi)

## 🔍 Debug Steps:
1. Open browser developer tools (F12)
2. Go to Network tab
3. Try registration
4. Check the request being sent to `/api/v1/auth/register`
5. Verify the request body matches the expected format above

## 🚀 Test Registration:
Try registering with a new phone number (not one of the test users):
- Name: "New Farmer"
- Phone: "9876543213" 
- Password: "newpass123"
- Language: "en" (automatically set)

If you still get 422 errors, the request body format might not match what's expected.