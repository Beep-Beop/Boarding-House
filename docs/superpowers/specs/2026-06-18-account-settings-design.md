# Account Settings — Design Spec

**Date:** 2026-06-18
**Project:** Boarding House Finder
**Status:** Approved

---

## 1. Motivation & Goals

Currently the user's account management is split across two separate overlay dialogs:
- `ProfileMixin.show_profile()` — edits name, phone, street, DOB
- `ChangePasswordMixin.show_change_password()` — changes password

Both are triggered from separate menu items in every dashboard's user dropdown. The UX is disjointed: a user must close one overlay to open the other, losing context. Modern web applications (GitHub, Google, Airbnb) consolidate all account management into a single page with tabbed or sectioned layout.

**Goals:**
1. Merge profile editing and password changing into a single unified "Account Settings" overlay
2. Add missing account-state information (email, role, member date, verification status, auth provider)
3. Add ID document upload for tenants and business permit upload for owners
4. Add linked Google account display
5. Add client-side password strength checklist (reusing pattern from register page)
6. Add account deletion (Danger Zone)
7. Keep per-role customizations: 3 tabs for Tenant, 3 tabs for Owner, 2 tabs for Admin
8. Preserve all existing theme tokens (colors, fonts, corner radii)

---

## 2. Menu & Navigation Changes

**Files affected:** `gui/screens/dashboard.py`, `gui/screens/owner_dashboard.py`, `gui/screens/admin_dashboard.py`

All three dashboards currently have two separate menu items:
```python
("My Profile",       self.menu_profile_icon,  self.show_profile)
("Account Security",  self.menu_lock_icon,    self.show_change_password)
```

Replace with a single entry:
```python
("Account Settings", self.menu_profile_icon, self.show_account_settings)
```

The two old methods (`show_profile`, `show_change_password`) and their helpers (`_save_profile`, `_change_password`, `_close_profile_overlay`, `_close_pw_overlay`) are deleted. They are replaced by `show_account_settings` plus role-specific `_build_*_tab` methods in the new `AccountSettingsMixin`.

**New menu items per dashboard:**

| Dashboard | Menu items |
|-----------|------------|
| Tenant | Account Settings, —, My Bookings, Notifications, —, Logout |
| Owner | Account Settings, —, My Bookings, Notifications, —, Logout |
| Admin | Account Settings, —, Notifications, —, Logout |

---

## 3. Overlay Shell

**File:** `gui/screens/account_settings.py` (new file — single `AccountSettingsMixin` class)

### 3.1 Entry Point

```python
class AccountSettingsMixin:
    def show_account_settings(self):
        """Build the unified overlay with CTkTabview."""
```

**Container resolution** (same pattern as existing overlays):
```python
container = getattr(self, 'form_container', None) or \
            getattr(self, '_admin_form_container', None) or \
            self.container
```

### 3.2 Overlay Structure

- **Outer overlay:** `CTkFrame` with `fg_color=self.fg_color`, fills container via `place(x=0, y=0, relwidth=1, relheight=1)`, lifted.
- **Card:** `CTkFrame` with:
  - `fg_color=self.secondary_color`
  - `corner_radius=12`
  - `border_width=1`, `border_color=self.entry_border`
  - `width=580`
  - Centered: `place(relx=0.5, rely=0.5, anchor="center")`
- **Close button:** `CTkButton` top-left (x=12, y=12), text="✕", 32×32px, transparent bg, `command=self._close_account_overlay`
- **Title:** `CTkLabel` centered: `text="ACCOUNT SETTINGS"`, `font=self.alt_title_font`

### 3.3 Tabview

```python
tabview = ctk.CTkTabview(
    card, width=540, height=460,
    fg_color="transparent",
    segmented_button_fg_color=self.fg_color,
    segmented_button_selected_color=self.primary_color,
    segmented_button_unselected_color=self.hover_color_text,
    text_color=self.text_color,
)
tabview.pack(padx=20, pady=(0, 20))
```

Each tab contains a `CTkScrollableFrame` internally for overflow.

### 3.4 Per-Role Tab Configuration

| Role | Tab 1 | Tab 2 | Tab 3 |
|------|-------|-------|-------|
| Tenant | Profile | Security | Verification |
| Owner | Profile | Security | Documents |
| Admin | Profile | Security | *(none)* |

```python
if role == "admin":
    tabs = ["Profile", "Security"]
elif role == "student":
    tabs = ["Profile", "Security", "Verification"]
else:  # owner
    tabs = ["Profile", "Security", "Documents"]
```

---

## 4. Profile Tab (All Roles)

### 4.1 Avatar Section

- **Left side:** `CTkFrame(fg_color="transparent")` with fixed width=120
  - `CTkLabel` for photo: 80×80px, `corner_radius=40`, `image=self.pfp_placeholder` initially
  - "Edit" `CTkButton` below: `fg_color="transparent"`, `text_color=self.primary_color`, `command=self._pick_profile_photo`
    - Opens `filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])`
    - Validates max 2MB client-side
    - Shows `CTkImage` preview with `CTkImage(pil_img, size=(80, 80))`
    - Does NOT upload yet — waits for "Save Changes" button
- **Right side:** `CTkFrame(fg_color="transparent")`
  - Name in `body_bold_paragraph_font`
  - Email in `body_light_font`

### 4.2 Badges Row

Horizontal row below the name/email, using existing `CTkLabel` styling:

| Badge | Condition | Style |
|-------|-----------|-------|
| `role.capitalize()` (e.g., "Tenant") | Always | `fg_color=self.primary_color`, white text, `corner_radius=4` |
| "✓ Verified" / "○ Pending" / "○ Not Verified" | Tenant only, based on `is_verified` | Green / Orange / Gray |
| "✓ Email Verified" / "○ Unverified" | Based on `email_verified` | Green / Orange |
| "Google" / "Email" / "Email + Google" | Based on `auth_provider` | `fg_color=self.hover_color`, white text |

### 4.3 Form Fields

Two sections separated by a thin `CTkFrame(height=1, fg_color=self.entry_border)`:

**Personal Information:**

| Field | Widget | Width | Placeholder |
|-------|--------|-------|-------------|
| Full Name | `CTkEntry` | 380 | "John Doe" |
| Phone Number | `CTkEntry` | 380 | "+63 912 345 6789" |
| Street Address | `CTkEntry` | 380 | "123 Mabini St, Barangay ..." |
| Date of Birth | 3× `CTkOptionMenu` | 120 each | Month, Day, Year |

**Date of Birth picker:**
- Month: `["Jan", "Feb", ... "Dec"]`
- Day: `["1", "2", ... "31"]`
- Year: `["1950", "1951", ... "2010"]`
- Arranged horizontally in a `CTkFrame`
- Pre-populated from `date_of_birth` value, or set to placeholder if empty

**Account Info (read-only):**

| Label | Value Source |
|-------|-------------|
| Role | `user['role'].capitalize()` |
| Member Since | `user['created_at']` formatted as "January 15, 2025" |
| Auth Provider | `user['auth_provider'].replace('_', ' ').title()` |
| Account Status | `user['status'].capitalize()` |

### 4.4 Data Loading & Save

- **Loading:** On tab creation, if user data not already available, fetch from `GET /users/{user_id}` in a thread, post result via `self.after(0, ...)`
- **Dirty tracking:** Each `CTkEntry` gets a `StringVar` with `.trace_add("write", callback)`. Save button disabled until any field changes. Trace also clears the error label.
- **Save (`_save_profile_tab`):**
  1. Validate all fields client-side
  2. Build payload dict (only changed fields)
  3. Button → disabled, text="SAVING..."
  4. `PATCH /users/{user_id}` in a thread
  5. Success → toast "Profile updated", keep overlay open
  6. Error → inline error, re-enable button

---

## 5. Security Tab (All Roles)

### 5.1 Change Password Section

**Heading:** "Change Password" in `body_bold_paragraph_font`

Three password fields — each in its own row with a 👁 toggle:

```
Current Password  [••••••••••••]  👁
New Password      [••••••••••••]  👁
Confirm New       [••••••••••••]  👁

Password Requirements:
✓  8+ characters    ✓  Uppercase letter
✓  Number           ✗  Special character

     [ UPDATE PASSWORD ]
```

**Password visibility toggle:**
- Reuses `closed_eye_icon` / `open_eye_icon` + `_animate_eye()` from `app.py`
- Each field has a `CTkLabel(image=self.closed_eye_icon, cursor="hand2")` to its right
- On click: toggle `show=""` / `show="•"`, swap icon, animate

**Real-time validation (reusing logic from `register_validation.py`):**
- **`validate_password_strength_realtime`**: Updates 4 labels (✓/✗) on every `<KeyRelease>` of "New Password". Same criteria:
  - Length ≥ 8
  - Has uppercase letter
  - Has number
  - Has special character
- **`validate_password_match_realtime`**: Compares "New Password" + "Confirm New" on `<KeyRelease>`, shows "Passwords do not match"
- Both update `text_color=green` / `text_color=self.error_red`
- **All error labels** pre-created with empty text and toggled — never dynamically created/destroyed

**Update flow:**
1. All three fields non-empty, new passwords match, all 4 criteria met → enable button
2. Click → disabled, text="UPDATING..."
3. `POST /auth/change-password` in a thread
4. Success → toast "Password changed!", clear all fields
5. Error → inline error, re-enable button

### 5.2 Danger Zone Section

**Separator:** thin line + "Danger Zone" heading in `self.error_red`

**Red-bordered card:**
```python
ctk.CTkFrame(card, fg_color=self.secondary_color,
             border_width=1, border_color=self.error_red,
             corner_radius=6)
```

- Warning text: "Delete your account and all associated data. This action CANNOT be undone."
- **Delete button:** `fg_color=self.error_red`, `command=self._confirm_delete_account`

**Delete flow:**
1. Click → `CTkInputDialog` with:
   - Title: "Delete Account"
   - Text: "Type DELETE to permanently delete your account:"
2. If input == "DELETE":
   - `DELETE /users/{user_id}` in thread
   - Success → toast + `_handle_logout()`
   - Error → toast with error

---

## 6. Tenant — Verification Tab

### 6.1 Status Card

Colored card at top showing verification state:

| State | Visual |
|-------|--------|
| No ID uploaded | Orange: "You haven't uploaded a valid ID yet." |
| Pending review | Yellow: "Your ID is under review (1-2 business days)" |
| Verified | Green: "You're verified! ✓" |
| Rejected | Red: "Your ID was rejected. Please upload a new one." |

### 6.2 Upload Section

- **Upload button:** `CTkButton(text="📤 Upload Valid ID", ...)`
  - Opens `filedialog.askopenfilename(filetypes=[("Images/PDF", "*.jpg *.jpeg *.png *.pdf")], max_size=5MB)`
- **Preview:** Shows filename + small image thumbnail
- **Upload progress:** Indeterminate `CTkProgressBar` during upload
- **Existing file:** If `id_document_url` is set, show filename + "Replace" + "Remove" buttons

### 6.3 Linked Accounts

**Google section (only if `auth_provider` contains 'google'):**

```
┌────────────────────────────────────────────┐
│  Google                         ● Connected │
│  user@gmail.com                           │
│                                   [Unlink] │
└────────────────────────────────────────────┘
```

- "Unlink" shows confirmation dialog
- On confirm: `PATCH /users/{user_id}` setting `auth_provider`
- If `auth_provider` is 'email' only: gray "○ Not linked" with disabled "Link" button (future feature)

---

## 7. Owner — Documents Tab

### 7.1 Status Card

Same layout as Tenant Verification, but for business permit:

| State | Visual |
|-------|--------|
| No permit | Orange: "Upload your business permit to get your listings verified." |
| Pending | Yellow: "Your permit is being reviewed." |
| Verified | Green: "Your permit is verified. Listings show the Verified badge." |
| Rejected | Red: "Your permit was rejected. Please upload a compliant permit." |

### 7.2 Upload Section

- Same pattern as Tenant, but max 10MB instead of 5MB
- Uploads to `permit_url` field (not `id_document_url`)

### 7.3 Linked Accounts

Identical to Tenant section — Google connect/unlink.

---

## 8. Admin — No Third Tab

Admin gets exactly 2 tabs: Profile + Security. No third tab. All admin-specific functions are in the admin dashboard sidebar.

---

## 9. Theme & Visual Consistency

All new widgets reuse existing theme properties from `app.py`:
- `self.primary_color`, `self.secondary_color`, `self.fg_color`
- `self.text_color`, `self.entry_border`
- `self.hover_color`, `self.error_red`
- `self.alt_title_font`, `self.body_bold_paragraph_font`, `self.body_light_font`
- `self.body_paragraph_font`, `self.body_description_font`, `self.body_bold_font`
- `self.inline_error_font`

All colors as `(light, dark)` tuples — no hardcoded hex strings except white text on colored badges.

---

## 10. Error Handling

- **Network errors:** Caught in thread, posted via `self.after(0, ...)` to label
- **Validation errors:** Inline next to the relevant field
- **Token expiry (401):** Toast "Session expired" and redirect to login
- **Server validation (422):** Parse `resp.json()["detail"]` and show inline
- **File upload:** Size validated client-side before upload; server error shown inline
- **All error labels** pre-created with empty text and toggled — never dynamically created/destroyed

---

## 11. Files Changed

| File | Action |
|------|--------|
| `gui/screens/account_settings.py` | CREATE — new `AccountSettingsMixin` |
| `gui/screens/profile.py` | DELETE — replaced |
| `gui/screens/change_password.py` | DELETE — replaced |
| `gui/app.py` | EDIT — swap imports, remove old mixins, add AccountSettingsMixin |
| `gui/screens/dashboard.py` | EDIT — `_toggle_user_menu()`: single "Account Settings" entry |
| `gui/screens/owner_dashboard.py` | EDIT — same menu change |
| `gui/screens/admin_dashboard.py` | EDIT — same menu change |
