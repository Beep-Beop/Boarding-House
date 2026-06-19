# Account Settings Accordion Redesign v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite `gui/screens/account_settings.py` from scratch with a fundamentally different architecture — extract accordion UI into a reusable widget, leaving the mixin thin.

**Architecture:** Two-layer: (1) `gui/widgets/settings_accordion.py` with `SettingsAccordion` + `SettingsSection` classes managing all accordion UI and animation, (2) `AccountSettingsMixin` that only orchestrates sections and handles API calls.

**Tech Stack:** customtkinter, threading, PIL, tkinter.filedialog, datetime, re

## Global Constraints

- Must NOT reuse any old code patterns, widget-creation style, or structural approach from previous versions
- Mixin must be thin — no accordion state management, no animation logic, no accordion frame creation
- Accordion widget must own all expand/collapse/animation state internally
- Section builder methods receive a plain `CTkFrame` to populate — no knowledge of accordion internals
- Use `self.*` from parent `BoardingHouseApp` for theme colors, fonts, `current_user`, `api`, `show_toast`, `pfp_placeholder_lg`
- Single progress bar per settings view

---

### Task 1: Create the Accordion Widget

**Files:**
- Create: `gui/widgets/__init__.py` — empty init
- Create: `gui/widgets/settings_accordion.py` — `SettingsAccordion` + `SettingsSection` classes

**Description:**

Build a standalone accordion widget system. Two classes:

**`SettingsSection`** — a single collapsible card:
- Constructor takes `(parent, title_text)`, creates outer `CTkFrame` (rounded corners, border), header row with title label + arrow label, wrapper frame for height animation, content frame inside wrapper, and a hidden progress bar
- Header is clickable (cursor="hand2") — binds work for all children too
- `expand()`: measures content natural height via `update_idletasks()`, sets wrapper to 0, animates to target height in 10 steps × 15ms via `after()`, flips arrow to ▼
- `collapse()`: gets current wrapper height, animates to 0, hides content on completion, flips arrow to ▶
- `toggle()`: delegates to expand or collapse based on `is_expanded` flag, with `_animating` lock to prevent double-trigger
- Exposes `.content_frame` (the inner frame where builders place widgets)
- Exposes `.show_progress()` / `.hide_progress()` for the built-in progress bar

**`SettingsAccordion`** — container extending `CTkScrollableFrame`:
- Holds a list of `SettingsSection` instances
- `add_section(title: str) -> CTkFrame`: creates a new `SettingsSection`, packs it, returns its `.content_frame`
- `show_progress()` / `hide_progress()`: top-level progress bar (used for API calls)
- `expand_first()`: expands the first section (called after all sections added)

**Animation details:**
- 10 steps, 15ms interval (150ms total per toggle)
- Uses `linear` interpolation between start and end heights
- Wrapper frame has `pack_propagate(False)` so height is controllable
- No `tkinter` geometry hacks — pure height attribute changes

- [ ] Create `gui/widgets/__init__.py` (empty file)
- [ ] Create `gui/widgets/settings_accordion.py` with `SettingsSection` class (header, wrapper, content_frame, progress bar, expand/collapse/toggle with animation)
- [ ] Add `SettingsAccordion` class extending `CTkScrollableFrame` with `add_section()`, `show_progress()`, `hide_progress()`, `expand_first()`

---

### Task 2: Rewrite the Mixin — Accordion Surface + Profile Section

**Files:**
- Rewrite: `gui/screens/account_settings.py` — thin mixin

**`show_account_settings()`**:
1. Find content wrapper (`_admin_content_wrapper` or `content_wrapper`)
2. Destroy existing children
3. Create a container frame inside the content wrapper
4. Add header row with back button (same bk_btn_icon pattern) + "ACCOUNT SETTINGS" title
5. Create `SettingsAccordium` instance
6. Determine role from `self.current_user`
7. Add sections: "Profile" then "Security" for all roles, plus "Verification" for tenants, "Documents" for owners
8. Build content into each section's `.content_frame` via `_build_*_content(frame)` methods
9. Call `accordion.expand_first()`

**`_build_profile_content(frame)`**:
- Avatar row (left: 100x100 circular avatar label + "Edit Photo" button, right: name, email, role badge, email verified badge, auth provider badge)
- Personal Information card: Full Name entry, Phone entry, Street entry, Date of Birth (3 dropdowns: month/day/year with "/" separators), error label, SAVE CHANGES button
- Account Info card: read-only rows with alternating background colors showing Role, Member Since, Auth Provider, Account Status

**`_save_profile()`**:
- Collect values from entries and DOB dropdowns
- Validate date of birth
- Build payload dict with only changed fields
- Call `accordion.show_progress()`, thread PATCH `/users/{user_id}`, on success update `self.current_user` and show toast, on failure show inline error, always call `accordion.hide_progress()`

**`_pick_profile_photo()`**:
- `filedialog.askopenfilename` for .png/.jpg/.jpeg
- Validate max 2MB
- Open with PIL, thumbnail to 100x100, set as CTkImage on avatar label

**`_format_date(date_str)`**:
- Parse "YYYY-MM-DD" to "Month Day, Year" format
- Return em-dash if empty or invalid

- [ ] Write `show_account_settings()` entry point with content wrapper detection, header, accordion creation, and role-based section selection
- [ ] Implement `_build_profile_content(frame)` with avatar row, personal information card (entries + DOB), account info card
- [ ] Implement `_save_profile()` with validation, threaded API call, success/error handling
- [ ] Implement `_pick_profile_photo()` and `_format_date()` helpers

---

### Task 3: Security Section + Verification Section + Documents Section

**`_build_security_content(frame)`**:
- Change Password card: Current Password entry (with eye toggle icon and binding to `_toggle_pw_visibility`), New Password entry (with eye toggle, strength checklist grid updated on KeyRelease via `_validate_sec_strength`), Confirm Password entry (with eye toggle, match validation on KeyRelease via `_validate_sec_match`), error labels, UPDATE PASSWORD button
- Danger Zone: thin separator, "Danger Zone" red label, red-bordered card with warning text and "Delete Account" button bound to `_confirm_delete_account`

**Password helpers** (reuse from old code but rewrite cleanly):
- `_toggle_pw_visibility(field)`: toggles show/• on the entry, animates eye icon using `self._eye_frames_open/closed` from parent
- `_validate_sec_strength(event)`: checks 8+ chars, uppercase, number, special char; updates labels with ✓/✗ and green/red colors
- `_validate_sec_match(event)`: compares new and confirm, shows/hides match error

**`_update_password()`**:
- Validate all fields filled, passwords match, minimum 8 chars
- Thread POST `/auth/change-password`, on success show toast + clear fields, on failure show error

**`_confirm_delete_account()`**:
- CTkInputDialog with "Type DELETE" prompt
- If confirmed, thread DELETE `/users/{user_id}`, on success toast + logout, on failure toast error

**`_build_verification_content(frame)`**:
- Status card (three states: verified/green, pending review/amber, not verified/gray with appropriate messages)
- Valid ID Document card: Upload button, accepted formats note (JPG, PNG, PDF max 5MB), current file label, error label
- Linked Accounts card (delegates to `_build_linked_accounts`)

**`_pick_id_document()`**:
- filedialog, validate 5MB max
- Thread POST `/users/{user_id}/upload-id` with multipart file
- On success update `self.current_user`, show file label, toast

**`_build_documents_content(frame)`**:
- Same pattern as verification but for business permits (10MB limit, different endpoint `/upload-permit`, "Business Permit" heading)

**`_pick_permit()`**:
- Same pattern as ID upload but different endpoint and 10MB limit

**`_build_linked_accounts(frame, auth_provider)`**:
- Row with "Google" label, Connected/Not linked badge, Unlink button (or disabled Link button), email display

**`_unlink_google()`**:
- CTkInputDialog for confirmation
- Thread PATCH `/users/{user_id}` setting auth_provider to "email"
- On success update `self.current_user`, reload account settings

**`_go_back_from_settings()`**:
- Check role, call appropriate `show_*_dashboard()` method

- [ ] Implement `_build_security_content(frame)` with password change card and danger zone
- [ ] Implement password helpers: `_toggle_pw_visibility()`, `_validate_sec_strength()`, `_validate_sec_match()`
- [ ] Implement `_update_password()` and `_confirm_delete_account()` with threaded API calls
- [ ] Implement `_build_verification_content(frame)` with status card, ID upload card, linked accounts
- [ ] Implement `_pick_id_document()` with file validation and threaded upload
- [ ] Implement `_build_documents_content(frame)` with status card, permit upload card, linked accounts
- [ ] Implement `_pick_permit()` with file validation and threaded upload
- [ ] Implement `_build_linked_accounts(frame, auth_provider)` and `_unlink_google()`
- [ ] Implement `_go_back_from_settings()` for role-based navigation
