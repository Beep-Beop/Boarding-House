# Owner Dashboard Bookings Feature — Build Plan

> **Last updated:** 2026-06-17
> Implements a full booking management view in the owner dashboard.

---

## Files to Change

| # | File | Change |
|---|------|--------|
| 1 | `src/crud.py` | Add 3 new CRUD methods to `BookingsCRUD` |
| 2 | `src/routers/bookings.py` | Add 3 new endpoints |
| 3 | `gui/screens/owner_dashboard.py` | Rewrite bookings view + add detail view + fix progress bar |

---

## Phase 1 — Backend (CRUD + Routes)

### 1.1 CRUD — `BookingsCRUD.get_owner_bookings_enriched(owner_id, status=None)`
- Join: Bookings → Rooms → BoardingHouse → Users (tenant) → Payments
- Filter by `BoardingHouse.owner_id == owner_id`
- Optional status filter
- Returns list of tuples: (booking, room, listing, tenant, [payments])

### 1.2 CRUD — `BookingsCRUD.get_owner_booking_stats(owner_id)`
- Count bookings across owner's properties grouped by status
- Sum total_price for revenue
- Returns dict: `{total_bookings, pending_count, active_count, cancelled_count, total_revenue}`

### 1.3 CRUD — Reuse existing `get_booking_detail(booking_id)`
- Already created for admin, works for owner too

### 1.4 Router — `GET /bookings/owner/{owner_id}/enriched`
- Admin or owner only
- Returns `List[BookingAdminResponse]` with enriched data
- Supports `?status=` filter

### 1.5 Router — `GET /bookings/owner/{owner_id}/stats`
- Admin or owner only
- Returns `BookingStats`

### 1.6 Router — `GET /bookings/{booking_id}/owner-detail`
- Admin or owner of the property only
- Returns `BookingDetailResponse`

---

## Phase 2 — GUI (Owner Dashboard)

### 2.1 Fix `_show_loading` CTkProgressBar bug
- Replace `CTkProgressBar` + `bar.start()` with a simple `CTkLabel(text="Loading...")` spinner text
- This eliminates the `_variable` AttributeError on view switch

### 2.2 Rewrite `build_bookings_content()` → Full list view
- Stats bar: 4 `CTkFrame` cards (Total, Pending, Active, Cancelled) with accent colors
- Filter bar: `CTkComboBox` (All/Pending/Active/Cancelled) + search `CTkEntry` + Search button
- Table: ID, Tenant, Property→Room, Check-in, Check-out, Status badge, Total, Payment, Actions
- Actions: View button, Approve (pending), Cancel (pending)
- Background thread fetches `/bookings/owner/{id}/stats` + `/bookings/owner/{id}/enriched`
- Follows same table pattern as existing Tenants tab

### 2.3 Add `_owner_show_booking_detail(booking_id)` → Detail view
- Back button (reuse `bk_btn_icon`/`bk_btn_hvr_icon`)
- Header card: Booking # + Status badge + Dates
- Two-column: Tenant info (name, email, phone) | Property/Room info (name, type, room #)
- Booking details: Check-in/out, total price, notes
- Payment: Method, status, amount, ref
- Status history timeline
- Action buttons: Approve / Cancel based on status

### 2.4 Add `_owner_booking_action(booking_id, new_status)`
- `PATCH /bookings/{booking_id}/status`
- Toast feedback
- Refresh current view

---

## Phase 3 — Verify

- Restart uvicorn
- Login as owner
- Click Bookings in sidebar
- Verify stats load, table populates, filter/search works
- Click View → detail view shows all sections
- Approve/Cancel → status updates, toast shows
- Verify owner cannot see other owners' bookings
- Fix progress bar `_variable` error eliminated
