# Idea

This document is a rough idea for stakeholders to fill in so that the product manager agent can generate a PRD.

## Goals

1. We want to replace manual leave tracking with a simple web-based system within 2 weeks
2. We want to give employees self-service access to request leaves and check their balance
3. We want to streamline the approval process for managers
4. We want to eliminate confusion about remaining leave balances

## Requirements

1. The product must allow employees to log in and request leave
2. The product must allow managers to approve or reject leave requests
3. The product must track individual leave balances (starting at 21 days/year)
4. The product must work on modern web browsers including mobile phones
5. The product must show request history to employees
6. The product must allow managers to override/adjust employee leave balances
7. The product must automatically deduct approved leaves from balances

## Scope

### In scope

- Basic user authentication (email/password)
- Employee role: Request leave, view balance, view history
- Manager role: Approve/reject requests, adjust employee balances
- Single leave type (annual leave)
- Cloud-hosted solution
- Mobile-responsive web interface
- 20 users (startup size)
- NodeJS-based technology stack

### Out of scope

- Email notifications (Phase 2)
- Multiple leave types (sick, personal, etc.)
- Complex approval workflows
- Integration with other systems
- Leave policies and accrual rules
- Reporting and analytics
- Calendar integration
- Public holidays management
- Half-day leave options
- Leave forwarding to next year

## Notes, considerations and constraints

- Timeline: 2-week MVP development
- Target: 20-person startup
- Industry agnostic solution
- Focus on simplicity and speed to market
- Manual balance adjustments acceptable for MVP
- No regulatory compliance requirements for MVP
- Assume all users are in same timezone/location
