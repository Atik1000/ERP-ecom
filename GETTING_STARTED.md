# SmartERP - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Server is Already Running!
Your development server is running at:
- **E-commerce Store**: http://127.0.0.1:8000/
- **Admin Dashboard**: http://127.0.0.1:8000/dashboard
- **Django Admin**: http://127.0.0.1:8000/admin

### 2. Test Login Credentials

#### Staff Users (Access Dashboard)
| Role | Username | Password | Access |
|------|----------|----------|--------|
| Admin | `admin` | `admin123` | Full system access |
| Warehouse Manager | `wh_manager` | `manager123` | Inventory & Purchase |
| Branch Manager | `br_manager` | `manager123` | Branch operations |
| Cashier | `cashier1` | `cashier123` | POS transactions |

#### Customer User (Access E-commerce)
| Role | Username | Password | Access |
|------|----------|----------|--------|
| Customer | `customer1` | `customer123` | Online shopping |

### 3. What You Can Do Now

#### As a Customer (http://127.0.0.1:8000/)
1. ✅ Browse products on homepage
2. ✅ View product details with descriptions
3. ✅ Add products to cart
4. ✅ Proceed to checkout
5. ✅ Place orders (COD, bKash, Card)
6. ✅ Add products to wishlist
7. ✅ Write product reviews
8. ✅ Manage shipping addresses

#### As Staff (http://127.0.0.1:8000/dashboard)
1. ✅ View role-based dashboard with KPIs
2. ✅ Access role-specific menu items
3. ✅ View sales charts and analytics
4. ✅ Check pending tasks and alerts
5. ✅ Quick access to common actions
6. ✅ Manage inventory (Admin/Warehouse)
7. ✅ View reports

### 4. Testing the Application

#### Test E-commerce Flow:
```
1. Visit http://127.0.0.1:8000/
2. Click on "Products" in navbar
3. Click on any product
4. Click "Add to Cart"
5. Click cart icon (top right)
6. Click "Proceed to Checkout"
7. Login as customer1/customer123
8. Fill shipping address
9. Select payment method
10. Place order ✅
```

#### Test Dashboard Access:
```
1. Visit http://127.0.0.1:8000/login
2. Login as admin/admin123
3. You'll be redirected to /dashboard
4. See KPI cards (products, orders, sales, alerts)
5. Try quick action buttons
6. Check sidebar menu (role-based)
7. Click "Products" to manage inventory
8. Click "Suppliers" to manage purchases
```

#### Test Role-Based Access:
```
1. Login as cashier1/cashier123
2. Notice: Only POS, Sales, Reports menus visible
3. Logout and login as admin/admin123
4. Notice: All menus are visible
5. This is role-based access control! ✅
```

### 5. Project Structure Overview

```
📁 Your Project
├── 🏠 E-commerce UI (/)
│   ├── Homepage with featured products
│   ├── Product listing with filters
│   ├── Product detail with reviews
│   ├── Shopping cart
│   └── Checkout
│
├── 📊 Dashboard (/dashboard)
│   ├── Admin Dashboard (all modules)
│   ├── Warehouse Dashboard (inventory focus)
│   ├── Branch Dashboard (sales focus)
│   └── Cashier Dashboard (POS focus)
│
└── ⚙️ Django Admin (/admin)
    └── Full CRUD for all models
```

### 6. Key URLs to Try

#### E-commerce (Customer)
- Homepage: http://127.0.0.1:8000/
- Products: http://127.0.0.1:8000/products/
- Cart: http://127.0.0.1:8000/cart/
- Checkout: http://127.0.0.1:8000/checkout/

#### Dashboard (Staff)
- Main Dashboard: http://127.0.0.1:8000/dashboard/
- Products: http://127.0.0.1:8000/dashboard/inventory/
- Suppliers: http://127.0.0.1:8000/dashboard/purchase/

#### Admin Panel
- Django Admin: http://127.0.0.1:8000/admin/

### 7. Templates Created

✅ **8 Templates Ready:**
1. `base_ecommerce.html` - E-commerce base template
2. `base_dashboard.html` - Dashboard base with role-based sidebar
3. `home.html` - E-commerce homepage
4. `product_list.html` - Product listing with filters
5. `product_detail.html` - Product details with reviews
6. `cart.html` - Shopping cart
7. `checkout.html` - Checkout page
8. `admin_dashboard.html` - Dashboard with KPIs & charts
9. `login.html` - Professional login page

### 8. Sample Data Available

The database is populated with:
- ✅ 8 Sample Products (various categories)
- ✅ 3 Categories (Electronics, Fashion, Home)
- ✅ 2 Brands (TechBrand, FashionHub)
- ✅ 5 Users (all roles)
- ✅ 2 Branches (Main Branch, Downtown Branch)
- ✅ 1 Warehouse
- ✅ 3 Suppliers

### 9. What's Next?

You can now:
1. **Test existing features** using the credentials above
2. **Customize templates** in the `templates/` folder
3. **Add more products** via Django admin
4. **Create module-specific pages** (POS, Sales, Finance, CRM)
5. **Add JavaScript interactivity** to forms
6. **Style components** with Bootstrap/CSS

### 10. Common Tasks

#### Stop the Server
Press `CTRL+C` in the terminal

#### Restart the Server
```bash
cd /Users/epert/Desktop/ERP-ecomerse
/Users/epert/Desktop/ERP-ecomerse/venv/bin/python manage.py runserver
```

#### Access Database Shell
```bash
python manage.py shell
```

#### Create New Admin User
```bash
python manage.py createsuperuser
```

#### View All URLs
```bash
python manage.py show_urls  # If django-extensions installed
```

---

## 🎉 You're All Set!

Your SmartERP system is fully functional with:
- ✅ Complete backend (50+ models)
- ✅ Role-based authentication
- ✅ E-commerce frontend
- ✅ Admin dashboard
- ✅ Sample data

**Start testing now at: http://127.0.0.1:8000/**

Need help? Check the main README.md for detailed documentation.
