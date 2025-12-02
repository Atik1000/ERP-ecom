## SmartERP – Phase-wise Implementation Plan

SmartERP is a role-based ERP system built with **Django 5+, Django Template Engine, HTML, CSS, Tailwind/Bootstrap, and vanilla JavaScript**. The system is designed without DRF/REST APIs, focusing on server-rendered templates + progressive enhancement via AJAX/Fetch.

### Tech Stack
- **Backend**: Django 5+, PostgreSQL
- **Frontend**: Django Templates, Tailwind/Bootstrap, vanilla JS, Select2 for search dropdowns
- **Auth/RBAC**: Django auth with custom `User` model and role field
- **Static/Media**: Django static files system, `static/` and `media/` roots

### Core Roles
- **Admin**
- **Warehouse Manager**
- **Branch Manager**
- **Cashier**
- **Customer**

These roles drive both:
- **Permissions** (what actions are allowed)
- **Sidebar (left menu) visibility** (which modules are visible)

### Sidebar / Left Menu Visibility Rules (Initial Design)
The admin panel layout will use a shared sidebar template (`templates/partials/sidebar.html`) that checks `request.user.role` and/or Django permissions to show/hide menu sections.

Planned visibility (can be refined later):
- **Admin**
  - Full access: Inventory, Purchase, POS, E‑Commerce, Sales, Finance, Accounts, CRM, Reports, Settings, User & Branch management.
- **Warehouse Manager**
  - Inventory Management
  - Stock Movements & Transfers
  - Purchase receiving (limited)
  - Relevant reports (inventory/stock)
- **Branch Manager**
  - POS & Sales overview (for their branch)
  - Inventory (branch stock)
  - Transfers (from warehouse → branch)
  - Cash register & daily cash report (their branch)
- **Cashier**
  - POS screen
  - Basic sales history for their own sales
  - Cash register (open/close) where applicable
- **Customer**
  - E‑commerce frontend (no access to back-office sidebar)

Implementation details:
- `accounts.User.role` (TextChoices) is the primary role flag.
- Template logic in `sidebar.html` will conditionally render each section.
- Later we can refine to use **Django permissions + groups** for more granular control, but role-based visibility is the first step.

### High-level Folder Structure
- `core/` – Django project settings, URLs, WSGI/ASGI
- `accounts/` – Users, roles, branch assignments
- `inventory/` – Products, categories, brands, units, stock, stock movements
- `purchase/` – Suppliers, purchase orders, GRNs, invoices
- `pos/` – POS UI, cart, receipts, offline queue
- `ecommerce/` – Storefront, product listing, cart, checkout
- `sales/` – Sales records, returns
- `finance/` – Cash registers, daily cash report
- `accounts/` – (This repo uses `accounts/` for auth; accounting-specific logic will go into `finance/` and/or a future `ledger/` app.)
- `crm/` – Customer groups, loyalty, coupons, feedback
- `reports/` – Dashboards & analytics
- `templates/` – Shared templates (base, dashboard, partials, etc.)
- `static/` – CSS, JS, images
- `media/` – Uploads

### Stock Management Design (Central Service)
All stock changes **must** flow through a single service function, never by directly modifying stock quantity fields from views or signals.

- `inventory.models.StockMovement` records every stock mutation (IN/OUT).
- `inventory.services.stock.apply_stock_movement(...)`:
  - Creates a `StockMovement` record
  - Updates warehouse/branch stock models
  - Enforces movement types:
    - PURCHASE → IN  
    - POS SALE → OUT  
    - ONLINE ORDER → OUT  
    - TRANSFER IN/OUT → IN/OUT  
    - RETURN → IN  
    - DAMAGE → OUT

Views in **Purchase**, **POS**, **E‑Commerce**, **Transfers** will call this service instead of touching stock directly.

### Phase 1 – Scaffold (this commit)
- Django project `core` created with PostgreSQL-ready settings.
- `accounts` app with:
  - Custom `User` model + role choices and branch reference
  - `Branch` model
  - Admin registration
- `inventory` app with:
  - `Category`, `Brand`, `Unit`, `Product`, `ProductVariant`
  - `WarehouseStock`, `BranchStock`
  - `StockMovement` model
  - Skeleton `inventory.services.stock.apply_stock_movement`
- Global URLs, base dashboard, placeholder templates.

### Next Phases
1. **Auth & RBAC**
   - Login, logout, password change
   - Branch selector for staff
   - Role-based sidebar + per-view permissions
2. **Inventory Operations**
   - Implement stock movement flows via service
   - Low stock & expiry alerts
   - Barcode/QR integration
3. **Purchase, POS, E‑Commerce, Transfers, Sales, Finance, CRM, Reports**
   - Implement each module using the stock service
   - Add AJAX-based UIs and print styles
4. **Testing & Hardening**
   - Unit tests for stock service, permissions, and critical flows
   - Performance optimizations and UI polish

You can now run migrations and start the server after installing dependencies:

```bash
cd ERP-ecomerse
python -m venv venv
source venv/bin/activate
pip install 'Django>=5,<6' psycopg2-binary
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```


