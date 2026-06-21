# Boarding House App — System Workflow Design

**Date:** 2026-06-21
**Status:** Draft
**Author:** System Design

## Overview

The Boarding House App connects **Students** looking for rooms with **Owners** offering boarding houses, moderated by **Admins**. The system has a Python FastAPI backend with a CustomTkinter desktop GUI frontend.

---

## 1. Roles

| Role | Description |
|------|-------------|
| **Student** | Tenant looking for a place to stay. Can browse, favorite, view, book, pay, review, and request maintenance. |
| **Owner** | Property manager who creates listings, manages rooms, handles bookings/viewings/maintenance requests. |
| **Admin** | System moderator who verifies users & listings, handles reports, monitors all activity via audit logs. |

---

## 2. Student Workflow

The student journey has 7 stages:

### 2.1 Register & Verify
- Sign up with email + password **OR** Google OAuth
- Verify email via 6-digit code sent through Brevo API or SMTP
- Complete account setup (name, phone, date of birth, street address)
- Upload valid ID document (optional until needed for verification by admin)

### 2.2 Discover Listings
- Browse / search listings with filters: location (province/city/barangay), price range (min/max), amenities, minimum stay
- View full listing details: photos, available rooms, amenities, property rules, owner info, location on map
- Save listings to Favorites/Wishlist for later

### 2.3 Schedule Viewing (Optional)
- Pick a date and time to visit the property in person
- Owner receives notification and can confirm or reschedule
- Viewing status lifecycle: `pending → confirmed → completed | cancelled`

### 2.4 Book a Room
- Select a specific room, choose check-in and check-out dates
- System calculates total price based on room's monthly rate
- Submit booking request → status becomes `pending`
- Owner reviews and either approves (`active`) or declines (`cancelled`)
- Student can cancel only while status is `pending`

### 2.5 Pay
- Make payment via GCash, bank transfer, cash, or card
- Payment status lifecycle: `pending → completed | failed | refunded`
- Reference number tracked for verification

### 2.6 During Stay
- Submit maintenance requests (title + description)
- Request status lifecycle: `pending → in_progress → completed`
- Owner resolves the issue and marks it done

### 2.7 After Stay
- Leave a rating (1-5) and comment/review for the listing
- Reviews linked to booking for "verified stay" badge
- Can optionally report issues with the listing (triggers admin moderation)

---

## 3. Owner Workflow

The owner journey has 5 stages:

### 3.1 Register & Verify
- Sign up with role = "owner"
- Verify email
- Complete account setup
- Upload valid ID document for identity verification by admin
- (Registration same process as student but role differs)

### 3.2 Create Listing
- Add property details: name, property type (Boarding House / Dormitory / Apartment), description, rules, minimum stay months
- Set location (province, city, barangay, street) — linked to global Location table
- Upload business permit (required for admin verification)
- Upload listing photos (one cover photo + gallery)
- Link amenities from global list (WiFi, Aircon, Kitchen, Security, etc.)
- Initial status: `pending` — admin reviews the permit
- Admin approves → status becomes `active`, `is_verified = true`
- Admin rejects → status can be set to `banned`

### 3.3 Add Rooms
- For each room: type (Single/Double/Studio), capacity, price per month, floor level
- Upload room-specific photos
- Room marked `available = true` by default
- Can update room details or mark unavailable later

### 3.4 Manage Requests
- **Booking requests:** View incoming → Approve (student can pay) or Decline
- **Viewing requests:** View calendar of requests → Confirm or Reschedule
- **Maintenance reports:** View from tenants → Mark `in_progress` while working → `completed` when done

### 3.5 Track & Monitor
- View enriched booking list with tenant name, email, phone, payment status
- View booking stats: total, pending, active, cancelled counts + total revenue
- View payment history from tenants

---

## 4. Admin Workflow

Admins are pre-created accounts (not self-registerable). Their workflow has 5 areas:

### 4.1 Monitor Listings
- View all listings, filter by verification status
- Review uploaded business permits
- Approve listing → `is_verified = true`, status = `active`
- Ban listing if rules violated → status = `banned`

### 4.2 Manage Users
- View all users (students and owners)
- Verify user identity documents
- Change user status: `active`, `banned`, or `suspended`

### 4.3 Moderate Reports
- View all incoming reports (targeting listings, users, reviews, or bookings)
- Review the report details and reason
- Resolve or Dismiss the report
- Take action on the reported entity as needed (ban listing, suspend user, etc.)
- Report lifecycle: `pending → reviewed → resolved | dismissed`

### 4.4 View System Data
- All bookings across all properties with enriched data
- Booking stats: counts by status + total revenue
- All payments
- Full booking detail view including payment history and status change history

### 4.5 Audit Trail
- Every admin action is logged in the `AdminLogs` table
- Logged fields: admin_id, action, target_type, target_id, description, ip_address, timestamp
- Immutable audit trail for accountability

---

## 5. Cross-Cutting Flows

### 5.1 Authentication
- Login via email/password returns JWT token (30 min expiry, HS256)
- Login via Google OAuth with state parameter (5 min TTL)
- Token sent on every API request via `Authorization: Bearer <token>` header
- Rate limited: 10 login attempts/minute, 5 booking creates/minute
- Token blacklist for logout

### 5.2 Email Notifications
- Brevo API (primary) or SMTP fallback (Mailtrap for dev)
- Emails sent for: email verification, password reset code, (future: booking confirmations, maintenance updates)

### 5.3 Password Management
- Forgot password: enter email → receive 6-digit code → verify code → set new password
- Change password (while logged in): enter old password → set new password

### 5.4 Google OAuth
- Sign up or log in with Google
- Profile auto-filled from Google account
- `auth_provider` set to "google" or "both" if email+password also linked

### 5.5 File Storage
- Photos and documents stored on Cloudflare R2 (S3-compatible)
- Entity types: listing photos, room photos, profile photos, ID documents, business permits

---

## 6. Data Relationships (Summary)

```
Users (Student/Owner/Admin)
  ├── Location (address)
  ├── BoardingHouse (owned by Owner)
  │     ├── Location (property address)
  │     ├── Rooms
  │     │     ├── Photos (room)
  │     │     └── Bookings
  │     │           ├── Payments
  │     │           ├── BookingHistory
  │     │           └── Reviews
  │     ├── ListingAmenities → Amenities (global list)
  │     ├── Photos (listing)
  │     ├── Viewings
  │     ├── MaintenanceRequests
  │     └── Favorites (by Students)
  ├── Reports (filed or assigned)
  ├── Notifications
  └── AdminLogs (admin actions only)

Other:
  TokenBlacklist, BookingHistory
```

---

## 7. State Machines

### Booking Status
```
pending ──(owner approves)──> active
pending ──(owner declines)──> cancelled
pending ──(student cancels)──> cancelled
```

### Payment Status
```
pending ──> completed
pending ──> failed
completed ──> refunded
```

### Viewing Status
```
pending ──(owner confirms)──> confirmed ──(visit done)──> completed
pending ──> cancelled
```

### Maintenance Status
```
pending ──(owner starts)──> in_progress ──(owner finishes)──> completed
```

### Report Status
```
pending ──(admin reviews)──> reviewed ──> resolved | dismissed
```

### Listing Status
```
pending ──(admin approves)──> active
active ──(admin bans)──> banned
```

---

## 8. Key Business Rules

- Only verified owners can create listings (admin checks permit)
- Student can only cancel their own booking while status is `pending`
- Only owner or admin can approve/decline a booking
- All admin actions are logged immutably
- Payments are linked to a booking, which is linked to a room
- Reviews can be marked "verified" if linked to a completed booking
- Each booking status change is recorded in BookingHistory for dispute resolution
- Rate limits apply to sensitive endpoints (login, booking, payment creation)
