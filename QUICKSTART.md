# SmartERP - Quick Start Guide

## ✅ Setup Complete!

Your SmartERP system is now running with SQLite database.

## 🚀 Access Your System

- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Login Credentials**: 
  - Username: `admin`
  - Password: (the one you just created)

## 📊 What's Working

✅ **Database**: SQLite (automatically switches to PostgreSQL in production)
✅ **All Models Created**: 50+ models across 9 modules
✅ **Migrations Applied**: All database tables created
✅ **Admin Panel**: Ready to use
✅ **Stock Management Service**: Centralized stock operations

## 🎯 Next Steps

### 1. Explore Admin Panel
- Go to http://127.0.0.1:8000/admin/
- Login with your credentials
- You can now manage:
  - Branches & Users (Accounts)
  - Products, Categories, Brands (Inventory)
  - Stock Movements & Alerts
  - Stock Transfers

### 2. Create Sample Data
Create some initial data through admin:
1. **Branch**: Create a warehouse and a branch
2. **Users**: Create users with different roles
3. **Categories & Brands**: For organizing products
4. **Products**: Add some test products

### 3. Switch to PostgreSQL (For Production)

When deploying to production:

```bash
# 1. Create .env file
cp .env.example .env

# 2. Edit .env and set:
USE_POSTGRES=1
DB_NAME=smarterp
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
DB_HOST=your_postgres_host
DB_PORT=5432

# 3. Run migrations
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser
```

## 📁 Project Structure

```
ERP-ecomerse/
├── accounts/           # Users, Branches, Activity Logs
├── inventory/          # Products, Stock, Movements, Transfers
├── purchase/           # Suppliers, Purchase Orders
├── pos/                # POS Sales, Cash Registers
├── ecommerce/          # Online Orders, Cart, Wishlist
├── sales/              # Returns, Targets
├── finance/            # Expenses, Transactions, Reports
├── crm/                # Customers, Loyalty, Coupons
├── reports/            # (To be implemented)
├── core/               # Project settings
├── templates/          # (To be created)
├── static/             # CSS, JS, Images
└── media/              # Uploaded files
```

## 🔧 Development Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Run development server
python manage.py runserver

# Create migrations (after model changes)
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run Python shell
python manage.py shell

# Collect static files (for production)
python manage.py collectstatic
```

## 📚 Available Modules

### ✅ Fully Implemented (Models & Admin)
1. **Accounts** - User management with roles
2. **Inventory** - Complete stock management
3. **Purchase** - Supplier and purchase orders
4. **POS** - Point of sale system
5. **E-commerce** - Online ordering
6. **Sales** - Returns and targets
7. **Finance** - Expense tracking
8. **CRM** - Customer relationship management

### 🚧 Pending Implementation
- URL routing for each module
- Views and forms
- Templates and UI
- Reports and dashboard
- Frontend JavaScript features

## 🎨 Admin Panel Features

Currently available in admin:

### Accounts
- Branch/Warehouse management
- User management with roles
- Branch assignments
- Activity logs (audit trail)

### Inventory
- Products with variants
- Categories and brands
- Warehouse stock
- Branch stock
- Stock movements (read-only)
- Stock alerts
- Stock transfers with approval

## 💡 Tips

1. **Stock Management**: Always use the Stock Service for stock changes
   ```python
   from inventory.services.stock import StockService
   StockService.apply_stock_movement(...)
   ```

2. **User Roles**: Assign proper roles to users:
   - Admin: Full access
   - Warehouse Manager: Warehouse operations
   - Branch Manager: Branch operations
   - Cashier: POS operations
   - Customer: E-commerce access

3. **Stock Transfers**: Create transfers through admin for moving stock between branches

## 🐛 Troubleshooting

### Database Issues
If you encounter database errors:
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Migration Conflicts
```bash
# Delete migration files (keep __init__.py)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recreate migrations
python manage.py makemigrations
python manage.py migrate
```

## 📞 Support

For issues or questions:
1. Check IMPLEMENTATION_STATUS.md for current progress
2. Review model definitions in each app's models.py
3. Check the centralized stock service in inventory/services/stock.py

---

**Status**: Development Ready ✅
**Database**: SQLite (switches to PostgreSQL with USE_POSTGRES=1)
**Server**: http://127.0.0.1:8000/
**Admin**: http://127.0.0.1:8000/admin/
