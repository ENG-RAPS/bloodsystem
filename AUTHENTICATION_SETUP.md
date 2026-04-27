# Blood Bank System - Authentication & Authorization Setup

## ✅ What Has Been Implemented

### 1. **Backend Authentication System**

#### New API Endpoints Created:
- `POST /api/auth/login/` - Login with username/password → Returns token
- `POST /api/auth/logout/` - Logout and invalidate token
- `POST /api/auth/register/` - Register new user
- `GET /api/auth/user/` - Get current authenticated user info

#### Authentication Method:
- **Token Authentication** (Django REST Framework)
- Tokens stored in database and localStorage on client side
- Session authentication also supported

### 2. **Frontend Pages Created**

#### `login.html`
- Professional login form with email/username and password
- Error handling with visual feedback
- "Forgot Password" link (ready for implementation)
- "Create Account" link to registration
- Stores authentication token on successful login
- Redirects to dashboard

#### `register.html`
- Complete registration form with fields:
  - First Name, Last Name
  - Username, Email
  - Password confirmation validation
  - Phone number
  - Blood type selector (8 types: O+, O-, A+, A-, B+, B-, AB+, AB-)
  - Role selection: Donor, Recipient, or Both
- Input validation on client and server
- Password strength validation (minimum 6 chars)
- Phone format validation
- Automatic login after registration

#### `dashboard.html` (Updated)
- **Role-Based Interface System**:
  - **Donor Interface**: Donation history, donation statistics
  - **Recipient Interface**: Blood requests list, new request form
  - **Admin Interface**: Manage users, manage inventory, pending requests
  - **Super Admin Interface**: Reports, settings (in addition to admin features)

### 3. **Backend Updated**

#### `views.py` - New Functions:
```python
- home()              # Landing page
- login_page()        # Login template view
- register_page()     # Registration template view
- dashboard()         # Dashboard template view
- login_api()         # Login API endpoint
- logout_api()        # Logout API endpoint
- register_api()      # Register API endpoint
- current_user()      # Get current user info
```

#### `urls.py` - New Routes:
```
/login/                    # Login page
/register/                 # Registration page
/dashboard/                # Dashboard page
/api/auth/login/          # Login API
/api/auth/logout/         # Logout API
/api/auth/register/       # Register API
/api/auth/user/           # Current user API
/api/users/               # User ViewSet (CRUD)
/api/locations/           # Location ViewSet
/api/inventory/           # Blood inventory management
/api/requests/            # Blood requests
/api/donations/           # Donations
/api/notifications/       # Notifications
```

#### `settings.py` - Updates:
- Added `rest_framework.authtoken` app
- Changed authentication to Token-based
- CORS configuration enabled

### 4. **Database Schema**

#### Extended User Model Fields:
```python
- blood_type       # 8 blood types
- role             # donor, recipient, both, admin, super_admin
- phone            # Phone number
- location         # Link to Location
- is_active_donor  # Boolean flag
- last_donation_date  # DateTime
```

#### Permission System (permissions.py):
- `IsSuperAdmin` - Only super admins
- `IsAdmin` - Only admins
- `IsAdminOrSuperAdmin` - Both admin roles
- `IsRequestOwner` - Request creator only

### 5. **Authentication Flow**

#### Login Flow:
```
1. User enters username/password on /login/
2. Frontend sends POST to /api/auth/login/
3. Backend authenticates against User model
4. Returns: token + user data (role, blood_type, name, etc.)
5. Frontend stores token in localStorage
6. Frontend redirects to /dashboard/
7. Dashboard loads user info from localStorage
8. UI shows role-specific features based on user.role
```

#### Registration Flow:
```
1. User fills registration form on /register/
2. Form validates all fields client-side
3. Frontend sends POST to /api/auth/register/
4. Backend creates new User with role
5. Token auto-generated and returned
6. Frontend stores token & redirects to dashboard
```

## 🔐 Security Features

✅ Password hashing (Django default)  
✅ CSRF protection  
✅ Token-based authentication  
✅ Role-based access control  
✅ Input validation (client & server)  
✅ Email/Username uniqueness checks  
✅ Phone format validation  

## 📱 User Roles & Permissions

### Donor Role Features:
- View donation history
- See donation statistics
- Find nearby recipients
- Manage donor profile

### Recipient Role Features:
- Submit blood requests
- View request status
- Track available blood units
- Manage recipient profile

### Admin Role Features:
- Manage all users (view, edit, delete)
- Manage blood inventory
- Review pending blood requests
- Approve/reject requests
- View system logs

### Super Admin Role Features:
- All admin features +
- Generate reports
- System settings
- User role management
- Full system control

## 🧪 Testing Instructions

### 1. **Test Registration**
```
URL: http://127.0.0.1:8000/register/
Steps:
1. Fill all fields
2. Select blood type
3. Choose role (Donor/Recipient/Both)
4. Submit form
5. Should auto-login and redirect to dashboard
```

### 2. **Test Login**
```
URL: http://127.0.0.1:8000/login/
Steps:
1. Enter username/password
2. Click Login
3. Should redirect to dashboard with role-based UI
```

### 3. **Test API Endpoints (cURL examples)**

#### Login API:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

Response:
```json
{
  "success": true,
  "token": "abc123xyz...",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "donor",
    "blood_type": "O+"
  }
}
```

#### Current User API:
```bash
curl -X GET http://127.0.0.1:8000/api/auth/user/ \
  -H "Authorization: Token abc123xyz..."
```

#### Register API:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "new@example.com",
    "password": "pass123456",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "blood_type": "AB+",
    "role": "recipient"
  }'
```

## 📂 File Structure

```
accounts/
├── templates/
│   └── accounts/
│       ├── home.html              # Landing page
│       ├── login.html             # Login page ✨ NEW
│       ├── register.html          # Registration page ✨ NEW
│       └── dashboard.html         # Role-based dashboard (UPDATED)
├── views.py                       # Backend APIs (UPDATED)
├── urls.py                        # URL routing (UPDATED)
├── models.py                      # User model (unchanged)
├── serializers.py                 # Serializers (unchanged)
├── permissions.py                 # Permissions (unchanged)
└── static/
    ├── css/
    └── js/

core/
├── settings.py                    # Django settings (UPDATED)
├── urls.py                        # Project URLs (UPDATED)
└── wsgi.py
```

## 🔄 Role-Based Dashboard Load Flow

```
User Visits /dashboard/
    ↓
Check localStorage for token
    ↓
If no token → Redirect to /login/
    ↓
If token exists → Load user data from localStorage
    ↓
Fetch user role (donor/recipient/admin/super_admin)
    ↓
Show role-specific sidebar items:
├── All: Profile link, Logout
├── Donor: Donation history
├── Recipient: Blood requests
├── Admin: Users, Inventory, Pending Requests
└── Super Admin: Reports, Settings
    ↓
Load role-specific statistics cards
    ↓
Display role-specific content sections
```

## 🎨 UI Color Scheme

- **Primary**: Blue #2563eb (Professional, accessible)
- **Secondary**: #1d4ed8 (Darker blue)
- **Success**: Green (Blood available)
- **Warning**: Yellow/Orange (Emergency requests)
- **Danger**: Red (Critical alerts)

## ⚙️ Next Steps (Optional Enhancements)

1. **Email Verification**
   - Send confirmation email on registration
   - Resend verification email link

2. **Forgot Password**
   - Password reset token
   - Email-based password recovery

3. **User Profile Edit**
   - Update personal information
   - Change blood type
   - Update location

4. **Notifications**
   - Real-time notification system
   - Email notifications
   - Push notifications

5. **Advanced Admin Features**
   - User activity logs
   - Blood inventory analytics
   - Request fulfillment statistics
   - Export reports to PDF/Excel

6. **Mobile App**
   - React Native/Flutter app
   - Use same API endpoints
   - Offline capability

## 📋 API Response Formats

### Success (200/201):
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Error (400/401/403):
```json
{
  "success": false,
  "error": "Error message",
  "details": { ... }
}
```

## 🚀 Deployment Considerations

- Use environment variables for SECRET_KEY
- Set DEBUG=False in production
- Use HTTPS only
- Configure ALLOWED_HOSTS
- Set secure cookies (SECURE_COOKIE, HTTPONLY)
- Use production database (PostgreSQL)
- Set up proper logging

---

**Created**: April 26, 2026  
**System**: Blood Bank Management System v1.0  
**Status**: ✅ Authentication System Ready for Testing
