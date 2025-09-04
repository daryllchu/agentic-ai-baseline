# Software Design Document (SDD)
## Leave Management System MVP

**Version:** 1.0  
**Date:** January 2025  
**Status:** Final  
**Development Timeline:** 2 weeks  

---

## 1. Executive Summary

This Software Design Document outlines the technical implementation of the Leave Management System MVP for a 20-person startup. The design prioritizes simplicity, rapid deployment, and core functionality over comprehensive features, ensuring delivery within the 2-week timeline.

**Key Design Principles:**
- Minimal viable architecture with room for growth
- Mobile-first responsive design
- Simple role-based access (Employee, Manager, HR)
- Stateless REST API with JWT authentication
- PostgreSQL for reliable data persistence

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   React SPA with Material-UI (Mobile Responsive)      │  │
│  └────────────────────┬─────────────────────────────────┘  │
└──────────────────────┼─────────────────────────────────────┘
                       │ HTTPS
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Express.js REST API (Node.js)                 │  │
│  │    ┌─────────────┐  ┌──────────┐  ┌──────────┐      │  │
│  │    │Auth Handler │  │   CORS   │  │  Router  │      │  │
│  │    └─────────────┘  └──────────┘  └──────────┘      │  │
│  └────────────────────┬─────────────────────────────────┘  │
└──────────────────────┼─────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Business Logic Layer                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────────────┐    │  │
│  │  │   User   │  │  Leave   │  │    Balance      │    │  │
│  │  │  Service │  │  Service │  │   Calculator    │    │  │
│  │  └──────────┘  └──────────┘  └─────────────────┘    │  │
│  └────────────────────┬─────────────────────────────────┘  │
└──────────────────────┼─────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Access Layer                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              PostgreSQL Database                      │  │
│  │         (Users, Leaves, LeaveRequests)               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

| Layer | Technology | Justification |
|-------|------------|---------------|
| Frontend | React 18 + Material-UI 5 | Fast development with pre-built components |
| API | Node.js 18 + Express.js 4 | Simple, well-documented, quick to implement |
| Database | PostgreSQL 14 | Robust, ACID compliant, good for relational data |
| Authentication | JWT (jsonwebtoken) | Stateless, simple to implement |
| ORM | Knex.js | Lightweight, flexible, good migration support |
| Hosting | Heroku/Railway | One-click deployment, free tier available |
| Password Hashing | bcrypt | Industry standard, secure |
| Date Handling | date-fns | Lightweight, timezone friendly |
| Validation | Joi | Schema validation for API inputs |
| Environment | dotenv | Environment variable management |

### 2.3 Deployment Architecture

```
Production Environment:
├── Web Server (Heroku/Railway)
│   ├── Node.js Application
│   └── Static React Build
└── Database Server
    └── PostgreSQL (Heroku Postgres/Railway)
```

---

## 3. Database Design

### 3.1 Entity Relationship Diagram

```
┌─────────────────┐
│     Users       │
├─────────────────┤
│ id (PK)         │
│ email (unique)  │
│ password_hash   │
│ first_name      │
│ last_name       │
│ role            │──────┐
│ manager_id (FK) │      │
│ leave_balance   │      │ (Employee, Manager, HR)
│ created_at      │      │
│ updated_at      │      │
│ is_active       │      │
└───────┬─────────┘      │
        │                │
        │ 1:N            │
        ▼                │
┌─────────────────┐      │
│  LeaveRequests  │      │
├─────────────────┤      │
│ id (PK)         │      │
│ employee_id (FK)│◄─────┘
│ start_date      │
│ end_date        │
│ days_requested  │
│ reason          │
│ status          │────────── (pending, approved, rejected, cancelled)
│ approver_id (FK)│
│ approver_comment│
│ created_at      │
│ updated_at      │
└─────────────────┘
```

### 3.2 Database Schema

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('employee', 'manager', 'hr')),
    manager_id INTEGER REFERENCES users(id),
    leave_balance DECIMAL(4,1) DEFAULT 21.0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Leave Requests table
CREATE TABLE leave_requests (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES users(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days_requested DECIMAL(4,1) NOT NULL,
    reason TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' 
        CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled')),
    approver_id INTEGER REFERENCES users(id),
    approver_comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_leave_requests_employee ON leave_requests(employee_id);
CREATE INDEX idx_leave_requests_status ON leave_requests(status);
CREATE INDEX idx_users_manager ON users(manager_id);
CREATE INDEX idx_users_email ON users(email);
```

### 3.3 Initial Data Seed

```sql
-- Create first HR user (hardcoded)
INSERT INTO users (email, password_hash, first_name, last_name, role) 
VALUES ('hr@company.com', '$2b$10$...', 'HR', 'Admin', 'hr');

-- Seed script will handle:
-- 1. Creating remaining users based on HR input
-- 2. Setting up manager relationships
-- 3. Initializing leave balances to 21 days
```

---

## 4. API Design

### 4.1 RESTful Endpoints

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| **Authentication** |
| POST | /api/auth/login | User login | No | All |
| POST | /api/auth/logout | User logout | Yes | All |
| GET | /api/auth/profile | Get current user | Yes | All |
| **User Management (HR Only)** |
| POST | /api/users | Create new user | Yes | HR |
| GET | /api/users | List all users | Yes | HR |
| PUT | /api/users/:id | Update user | Yes | HR |
| **Leave Requests** |
| POST | /api/leaves | Create leave request | Yes | Employee/Manager |
| GET | /api/leaves | Get user's requests | Yes | All |
| GET | /api/leaves/:id | Get specific request | Yes | All |
| PUT | /api/leaves/:id/cancel | Cancel request | Yes | Employee |
| **Manager Functions** |
| GET | /api/leaves/pending | Get pending team requests | Yes | Manager |
| PUT | /api/leaves/:id/approve | Approve request | Yes | Manager |
| PUT | /api/leaves/:id/reject | Reject request | Yes | Manager |
| GET | /api/leaves/team | Get team leave history | Yes | Manager |
| **Dashboard** |
| GET | /api/dashboard | Get dashboard data | Yes | All |

### 4.2 Request/Response Formats

#### Authentication Request
```json
POST /api/auth/login
{
    "email": "john.doe@company.com",
    "password": "password123"
}

Response:
{
    "success": true,
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "id": 1,
        "email": "john.doe@company.com",
        "firstName": "John",
        "lastName": "Doe",
        "role": "employee",
        "leaveBalance": 21
    }
}
```

#### Create Leave Request
```json
POST /api/leaves
{
    "startDate": "2025-02-01",
    "endDate": "2025-02-05",
    "reason": "Family vacation"
}

Response:
{
    "success": true,
    "request": {
        "id": 123,
        "startDate": "2025-02-01",
        "endDate": "2025-02-05",
        "daysRequested": 3,
        "status": "pending",
        "reason": "Family vacation"
    }
}
```

#### Approve/Reject Request
```json
PUT /api/leaves/123/approve
{
    "comment": "Approved. Have a great vacation!"
}

PUT /api/leaves/123/reject
{
    "comment": "Project deadline conflicts. Please reschedule."
}
```

### 4.3 Error Responses

```json
{
    "success": false,
    "error": {
        "code": "INSUFFICIENT_BALANCE",
        "message": "Insufficient leave balance. Available: 5 days, Requested: 10 days"
    }
}
```

Error Codes:
- `AUTH_REQUIRED` - Authentication required
- `UNAUTHORIZED` - Insufficient permissions
- `VALIDATION_ERROR` - Input validation failed
- `INSUFFICIENT_BALANCE` - Not enough leave days
- `OVERLAP_DETECTED` - Overlapping leave request exists
- `NOT_FOUND` - Resource not found
- `SERVER_ERROR` - Internal server error

---

## 5. Frontend Design

### 5.1 Component Architecture

```
src/
├── components/
│   ├── common/
│   │   ├── Layout.jsx
│   │   ├── Navigation.jsx
│   │   ├── LoadingSpinner.jsx
│   │   └── ErrorMessage.jsx
│   ├── auth/
│   │   └── LoginForm.jsx
│   ├── employee/
│   │   ├── Dashboard.jsx
│   │   ├── LeaveRequestForm.jsx
│   │   ├── LeaveHistory.jsx
│   │   └── BalanceCard.jsx
│   ├── manager/
│   │   ├── ApprovalQueue.jsx
│   │   ├── TeamCalendar.jsx
│   │   └── ApprovalDialog.jsx
│   └── hr/
│       ├── UserCreateForm.jsx
│       └── UserList.jsx
├── services/
│   ├── api.js
│   ├── auth.js
│   └── leaves.js
├── utils/
│   ├── dateHelpers.js
│   └── validators.js
├── contexts/
│   └── AuthContext.jsx
└── App.jsx
```

### 5.2 Page Layouts

#### Employee Dashboard
```
┌─────────────────────────────────────────┐
│            Navigation Bar                │
├─────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ │
│ │     Leave Balance Card              │ │
│ │     Available: 18 days              │ │
│ │     Used: 3 | Pending: 2            │ │
│ └─────────────────────────────────────┘ │
│                                          │
│ ┌─────────────────────────────────────┐ │
│ │     Quick Actions                    │ │
│ │  [Request Leave] [View History]     │ │
│ └─────────────────────────────────────┘ │
│                                          │
│ ┌─────────────────────────────────────┐ │
│ │     Recent Requests                  │ │
│ │  • Feb 1-5: Pending                 │ │
│ │  • Jan 15: Approved                 │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

#### Manager Approval Queue
```
┌─────────────────────────────────────────┐
│            Navigation Bar                │
├─────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ │
│ │   Pending Approvals (3)             │ │
│ ├─────────────────────────────────────┤ │
│ │ John Doe - Feb 1-5 (3 days)        │ │
│ │ Reason: Family vacation             │ │
│ │ [Approve] [Reject] [View Details]   │ │
│ ├─────────────────────────────────────┤ │
│ │ Jane Smith - Feb 10-11 (2 days)    │ │
│ │ Reason: Personal                    │ │
│ │ [Approve] [Reject] [View Details]   │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### 5.3 Responsive Breakpoints

```css
/* Mobile First Approach */
/* Base: 320px - 767px */
.container {
    padding: 16px;
    max-width: 100%;
}

/* Tablet: 768px - 1023px */
@media (min-width: 768px) {
    .container {
        padding: 24px;
        max-width: 768px;
    }
}

/* Desktop: 1024px+ */
@media (min-width: 1024px) {
    .container {
        padding: 32px;
        max-width: 1200px;
    }
}
```

---

## 6. Security Design

### 6.1 Authentication Flow

```
1. User Login
   ├── Email/Password → API
   ├── Validate credentials
   ├── Generate JWT (8-hour expiry)
   └── Return token + user data

2. Authenticated Request
   ├── Client sends JWT in Authorization header
   ├── Server validates JWT
   ├── Extract user context
   └── Process request with role validation

3. Token Expiry
   ├── Client detects 401 response
   └── Redirect to login
```

### 6.2 Security Measures

| Threat | Mitigation |
|--------|------------|
| SQL Injection | Parameterized queries with Knex.js |
| XSS | React's built-in escaping + Content Security Policy |
| CSRF | SameSite cookies + CORS configuration |
| Password Storage | bcrypt with salt rounds = 10 |
| Brute Force | Rate limiting: 5 login attempts per minute |
| Sensitive Data | HTTPS only, no sensitive data in logs |
| JWT Security | Short expiry (8 hours), HTTP-only cookies |

### 6.3 Role-Based Access Control

```javascript
// Middleware example
const authorize = (roles) => {
    return (req, res, next) => {
        if (!roles.includes(req.user.role)) {
            return res.status(403).json({ 
                error: 'Insufficient permissions' 
            });
        }
        next();
    };
};

// Usage
router.post('/api/users', authorize(['hr']), createUser);
router.get('/api/leaves/pending', authorize(['manager']), getPendingRequests);
```

---

## 7. Business Logic Implementation

### 7.1 Leave Calculation Algorithm

```javascript
function calculateLeaveDays(startDate, endDate) {
    let days = 0;
    let current = new Date(startDate);
    const end = new Date(endDate);
    
    while (current <= end) {
        const dayOfWeek = current.getDay();
        // Exclude weekends (0 = Sunday, 6 = Saturday)
        if (dayOfWeek !== 0 && dayOfWeek !== 6) {
            days++;
        }
        current.setDate(current.getDate() + 1);
    }
    
    return days;
}
```

### 7.2 Leave Request Validation

```javascript
async function validateLeaveRequest(userId, startDate, endDate) {
    const errors = [];
    
    // Check date validity
    if (new Date(startDate) < new Date()) {
        errors.push('Start date cannot be in the past');
    }
    
    if (new Date(endDate) < new Date(startDate)) {
        errors.push('End date must be after start date');
    }
    
    // Check balance
    const daysRequested = calculateLeaveDays(startDate, endDate);
    const user = await getUserById(userId);
    
    if (daysRequested > user.leave_balance) {
        errors.push(`Insufficient balance. Available: ${user.leave_balance}`);
    }
    
    // Check overlaps
    const overlaps = await checkOverlappingRequests(userId, startDate, endDate);
    if (overlaps.length > 0) {
        errors.push('Overlapping leave request exists');
    }
    
    return {
        isValid: errors.length === 0,
        errors,
        daysRequested
    };
}
```

### 7.3 Approval Workflow

```javascript
async function approveLeaveRequest(requestId, approverId, comment) {
    const request = await getRequestById(requestId);
    
    // Validate approver is the employee's manager
    const employee = await getUserById(request.employee_id);
    if (employee.manager_id !== approverId) {
        throw new Error('Only direct manager can approve');
    }
    
    // Start transaction
    await db.transaction(async (trx) => {
        // Update request status
        await trx('leave_requests')
            .where('id', requestId)
            .update({
                status: 'approved',
                approver_id: approverId,
                approver_comment: comment,
                updated_at: new Date()
            });
        
        // Deduct from balance
        await trx('users')
            .where('id', request.employee_id)
            .decrement('leave_balance', request.days_requested);
    });
    
    return { success: true };
}
```

---

## 8. Development Plan

### 8.1 Sprint Breakdown (14 Days)

#### Days 1-3: Backend Foundation
- [ ] Project setup and dependencies
- [ ] Database schema and migrations
- [ ] User authentication (login/logout)
- [ ] JWT middleware
- [ ] Basic error handling

#### Days 4-6: Core API Development
- [ ] User management endpoints (HR)
- [ ] Leave request CRUD operations
- [ ] Manager approval endpoints
- [ ] Leave calculation logic
- [ ] Balance management

#### Days 7-9: Frontend Foundation
- [ ] React project setup with Material-UI
- [ ] Authentication context and routing
- [ ] Login page
- [ ] Navigation and layout components
- [ ] API service layer

#### Days 10-12: Frontend Features
- [ ] Employee dashboard
- [ ] Leave request form
- [ ] Leave history view
- [ ] Manager approval queue
- [ ] HR user management

#### Days 13-14: Integration & Testing
- [ ] End-to-end testing of workflows
- [ ] Bug fixes and polish
- [ ] Deployment setup
- [ ] Production deployment
- [ ] User data seed and onboarding

### 8.2 File Structure

```
leave-management-system/
├── backend/
│   ├── src/
│   │   ├── config/
│   │   │   └── database.js
│   │   ├── controllers/
│   │   │   ├── authController.js
│   │   │   ├── userController.js
│   │   │   └── leaveController.js
│   │   ├── middleware/
│   │   │   ├── auth.js
│   │   │   └── errorHandler.js
│   │   ├── models/
│   │   │   ├── User.js
│   │   │   └── LeaveRequest.js
│   │   ├── routes/
│   │   │   ├── auth.js
│   │   │   ├── users.js
│   │   │   └── leaves.js
│   │   ├── services/
│   │   │   ├── leaveCalculator.js
│   │   │   └── validator.js
│   │   ├── utils/
│   │   │   └── jwt.js
│   │   └── app.js
│   ├── migrations/
│   ├── seeds/
│   ├── .env.example
│   ├── knexfile.js
│   └── server.js
├── frontend/
│   ├── public/
│   ├── src/
│   │   └── [React components as outlined above]
│   └── package.json
├── .gitignore
├── README.md
└── package.json
```

---

## 9. Testing Strategy

### 9.1 Critical Test Cases

#### Unit Tests (Backend)
```javascript
// Leave calculation tests
describe('Leave Calculator', () => {
    test('excludes weekends from calculation', () => {
        // Friday to Monday = 2 days
        expect(calculateDays('2025-01-31', '2025-02-03')).toBe(2);
    });
    
    test('single day leave', () => {
        expect(calculateDays('2025-02-03', '2025-02-03')).toBe(1);
    });
});

// Balance validation tests
describe('Balance Validation', () => {
    test('prevents negative balance', async () => {
        const user = { leave_balance: 5 };
        const result = await validateRequest(user, 10);
        expect(result.isValid).toBe(false);
    });
});
```

#### Integration Tests
- Login flow with valid/invalid credentials
- Leave request submission and approval cycle
- Manager can only approve team members
- HR can create users

### 9.2 Manual Test Checklist

- [ ] User login on mobile and desktop
- [ ] Submit leave request with various date ranges
- [ ] Cancel pending request
- [ ] Manager approve/reject with comments
- [ ] Balance updates correctly after approval
- [ ] HR creates new user successfully
- [ ] Logout works properly
- [ ] Error messages display correctly
- [ ] Responsive design on iPhone/Android

---

## 10. Deployment Guide

### 10.1 Environment Variables

```env
# .env.example
NODE_ENV=production
PORT=3000
DATABASE_URL=postgresql://user:password@host:5432/leavedb
JWT_SECRET=your-secret-key-here
CORS_ORIGIN=https://yourdomain.com
```

### 10.2 Deployment Steps

```bash
# 1. Clone repository
git clone <repository-url>

# 2. Install dependencies
cd backend && npm install
cd ../frontend && npm install

# 3. Setup database
createdb leavedb
cd backend
npx knex migrate:latest
npx knex seed:run

# 4. Build frontend
cd ../frontend
npm run build

# 5. Start application
cd ../backend
npm start

# For Heroku deployment
heroku create leave-management-mvp
heroku addons:create heroku-postgresql:mini
git push heroku main
heroku run knex migrate:latest
heroku run knex seed:run
```

### 10.3 Initial Setup Checklist

- [ ] Deploy to production environment
- [ ] Run database migrations
- [ ] Create HR admin user (seed script)
- [ ] Test HR login
- [ ] Create 19 employee/manager users via HR interface
- [ ] Set up manager relationships
- [ ] Verify all users can login
- [ ] Test complete workflow (request → approve → balance update)
- [ ] Share credentials with users

---

## 11. Performance Considerations

### 11.1 Optimization Strategies

| Area | Strategy | Implementation |
|------|----------|----------------|
| Database | Indexing | Indexes on foreign keys and frequently queried columns |
| API | Pagination | Limit results to 50 per page |
| Frontend | Lazy Loading | Code splitting for routes |
| Caching | Browser Cache | Cache static assets for 7 days |
| Images | Compression | Use WebP format, lazy load images |

### 11.2 Expected Performance

- **API Response Time:** < 200ms for most endpoints
- **Page Load:** < 2 seconds on 4G connection
- **Database Queries:** < 50ms with proper indexing
- **Concurrent Users:** 20 users without degradation

---

## 12. Error Handling & Logging

### 12.1 Error Handling Strategy

```javascript
// Global error handler
app.use((err, req, res, next) => {
    console.error(err.stack);
    
    // Known errors
    if (err.name === 'ValidationError') {
        return res.status(400).json({
            success: false,
            error: {
                code: 'VALIDATION_ERROR',
                message: err.message
            }
        });
    }
    
    // Default error
    res.status(500).json({
        success: false,
        error: {
            code: 'SERVER_ERROR',
            message: 'An error occurred. Please try again.'
        }
    });
});
```

### 12.2 Logging (Console Only for MVP)

```javascript
// Simple logging for MVP
const log = {
    info: (msg, data) => console.log(`[INFO] ${msg}`, data || ''),
    error: (msg, err) => console.error(`[ERROR] ${msg}`, err || ''),
    warn: (msg, data) => console.warn(`[WARN] ${msg}`, data || '')
};

// Usage
log.info('User logged in', { userId: user.id });
log.error('Database connection failed', err);
```

---

## 13. Known Limitations & Future Enhancements

### 13.1 MVP Limitations

1. **No password reset** - Admin must reset manually
2. **No email notifications** - Users must check app
3. **No public holidays** - Users exclude manually  
4. **Single leave type** - No sick/personal categorization
5. **No half-days** - Full days only
6. **No carry forward** - Balance resets January 1st
7. **No audit trail** - Basic logging only
8. **No reports** - Manual database queries if needed

### 13.2 Post-MVP Enhancements

**Week 3-4:**
- Email notifications for requests/approvals
- Password reset functionality
- Public holiday configuration
- Audit trail for all actions

**Month 2:**
- Half-day leave support
- Multiple leave types
- Calendar view for team leave
- Excel export for HR

**Month 3:**
- Mobile app
- Advanced approval workflows
- Leave policy engine
- Integration with HR systems

---

## 14. Acceptance Criteria

### 14.1 Technical Acceptance

- [ ] All endpoints return expected responses
- [ ] Authentication works with 8-hour token expiry
- [ ] Leave calculation excludes weekends correctly
- [ ] Balance updates immediately after approval
- [ ] No critical bugs in production
- [ ] Mobile responsive on all target devices

### 14.2 Functional Acceptance

- [ ] HR can create all 20 users
- [ ] Employees can request leave
- [ ] Managers can approve/reject requests
- [ ] Balances reflect approved leave
- [ ] Users can view their request history
- [ ] System prevents negative balances
- [ ] Overlapping requests are blocked

### 14.3 Deployment Acceptance

- [ ] Application deployed to production
- [ ] Database populated with users
- [ ] All users can login successfully
- [ ] Complete workflow tested end-to-end
- [ ] Basic documentation provided

---

## Appendix A: API Error Codes

| Code | Description | HTTP Status |
|------|-------------|------------|
| AUTH_REQUIRED | No valid token provided | 401 |
| TOKEN_EXPIRED | JWT token has expired | 401 |
| UNAUTHORIZED | User lacks required role | 403 |
| USER_NOT_FOUND | User ID doesn't exist | 404 |
| REQUEST_NOT_FOUND | Leave request doesn't exist | 404 |
| VALIDATION_ERROR | Input validation failed | 400 |
| DUPLICATE_EMAIL | Email already registered | 409 |
| INSUFFICIENT_BALANCE | Not enough leave days | 400 |
| OVERLAP_DETECTED | Dates overlap existing request | 409 |
| INVALID_DATE_RANGE | End date before start date | 400 |
| PAST_DATE | Start date in the past | 400 |
| SERVER_ERROR | Unexpected server error | 500 |

---

## Appendix B: Database Seed Data

```javascript
// Initial HR user
const hrUser = {
    email: 'hr@company.com',
    password: 'ChangeMeNow123!',
    first_name: 'HR',
    last_name: 'Admin',
    role: 'hr',
    leave_balance: 21
};

// Sample manager (created by HR)
const manager = {
    email: 'manager@company.com',
    password: 'TempPass123!',
    first_name: 'John',
    last_name: 'Manager',
    role: 'manager',
    manager_id: null, // Reports to CEO/HR
    leave_balance: 21
};

// Sample employee (created by HR)
const employee = {
    email: 'employee@company.com',
    password: 'TempPass123!',
    first_name: 'Jane',
    last_name: 'Employee',
    role: 'employee',
    manager_id: 2, // John Manager's ID
    leave_balance: 21
};
```

---

**Document Version Control:**
- v1.0 - Initial SDD based on simplified PRD requirements
- Focus: MVP delivery within 2-week timeline
- Scope: Core leave management functionality only

---

*This SDD provides the complete technical blueprint for implementing the Leave Management System MVP. Any deviations from this design should be documented and may impact the 2-week timeline.*