"""
Management command to create sample data for testing SmartERP
Usage: python manage.py create_sample_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from accounts.models import Branch, User
from inventory.models import Category, Brand, Unit, Product
from inventory.services.stock import StockService, StockMovement


class Command(BaseCommand):
    help = 'Creates sample data for testing SmartERP'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))

        # Create Branches
        warehouse, _ = Branch.objects.get_or_create(
            code='WH-001',
            defaults={
                'name': 'Main Warehouse',
                'is_warehouse': True,
                'address': '123 Warehouse Street',
                'phone': '+8801711111111',
                'email': 'warehouse@smarterp.com'
            }
        )
        self.stdout.write(f'✓ Created warehouse: {warehouse.name}')

        branch1, _ = Branch.objects.get_or_create(
            code='BR-001',
            defaults={
                'name': 'Downtown Branch',
                'is_warehouse': False,
                'address': '456 Main Street',
                'phone': '+8801722222222',
                'email': 'downtown@smarterp.com',
                'parent_branch': warehouse
            }
        )
        self.stdout.write(f'✓ Created branch: {branch1.name}')

        # Create Users
        admin_user = User.objects.filter(username='admin').first()
        if not admin_user:
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@smarterp.com',
                password='admin123',
                role=User.Role.ADMIN
            )
        self.stdout.write(f'✓ Admin user ready: {admin_user.username}')

        warehouse_manager, _ = User.objects.get_or_create(
            username='wh_manager',
            defaults={
                'email': 'wh_manager@smarterp.com',
                'role': User.Role.WAREHOUSE_MANAGER,
                'default_branch': warehouse,
                'first_name': 'John',
                'last_name': 'Warehouse'
            }
        )
        if not warehouse_manager.has_usable_password():
            warehouse_manager.set_password('manager123')
            warehouse_manager.save()
        self.stdout.write(f'✓ Created warehouse manager: {warehouse_manager.username}')

        branch_manager, _ = User.objects.get_or_create(
            username='br_manager',
            defaults={
                'email': 'br_manager@smarterp.com',
                'role': User.Role.BRANCH_MANAGER,
                'default_branch': branch1,
                'first_name': 'Jane',
                'last_name': 'Branch'
            }
        )
        if not branch_manager.has_usable_password():
            branch_manager.set_password('manager123')
            branch_manager.save()
        self.stdout.write(f'✓ Created branch manager: {branch_manager.username}')

        cashier, _ = User.objects.get_or_create(
            username='cashier1',
            defaults={
                'email': 'cashier1@smarterp.com',
                'role': User.Role.CASHIER,
                'default_branch': branch1,
                'first_name': 'Bob',
                'last_name': 'Cashier'
            }
        )
        if not cashier.has_usable_password():
            cashier.set_password('cashier123')
            cashier.save()
        self.stdout.write(f'✓ Created cashier: {cashier.username}')

        # Create Categories
        electronics, _ = Category.objects.get_or_create(name='Electronics')
        clothing, _ = Category.objects.get_or_create(name='Clothing')
        food, _ = Category.objects.get_or_create(name='Food & Beverages')
        self.stdout.write('✓ Created categories')

        # Create Brands
        samsung, _ = Brand.objects.get_or_create(name='Samsung')
        apple, _ = Brand.objects.get_or_create(name='Apple')
        nike, _ = Brand.objects.get_or_create(name='Nike')
        self.stdout.write('✓ Created brands')

        # Create Units
        pcs, _ = Unit.objects.get_or_create(name='Pieces', short_name='pcs')
        kg, _ = Unit.objects.get_or_create(name='Kilogram', short_name='kg')
        ltr, _ = Unit.objects.get_or_create(name='Liter', short_name='ltr')
        self.stdout.write('✓ Created units')

        # Create Products
        products_data = [
            {
                'name': 'Samsung Galaxy S23',
                'sku': 'ELEC-SAM-001',
                'category': electronics,
                'brand': samsung,
                'unit': pcs,
                'cost_price': Decimal('45000.00'),
                'selling_price': Decimal('55000.00'),
                'reorder_level': Decimal('5'),
                'barcode': '1234567890123'
            },
            {
                'name': 'Apple iPhone 14',
                'sku': 'ELEC-APP-001',
                'category': electronics,
                'brand': apple,
                'unit': pcs,
                'cost_price': Decimal('80000.00'),
                'selling_price': Decimal('95000.00'),
                'reorder_level': Decimal('3'),
                'barcode': '1234567890124'
            },
            {
                'name': 'Nike Air Max',
                'sku': 'CLO-NIK-001',
                'category': clothing,
                'brand': nike,
                'unit': pcs,
                'cost_price': Decimal('3500.00'),
                'selling_price': Decimal('5500.00'),
                'reorder_level': Decimal('10'),
                'barcode': '1234567890125'
            }
        ]

        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                sku=prod_data['sku'],
                defaults=prod_data
            )
            if created:
                self.stdout.write(f'✓ Created product: {product.name}')
                
                # Add initial stock to warehouse
                try:
                    StockService.apply_stock_movement(
                        product=product,
                        quantity=Decimal('50'),
                        movement_type=StockMovement.MovementType.ADJUSTMENT_IN,
                        dest_branch=warehouse,
                        reference='INITIAL-STOCK',
                        notes='Initial stock for testing',
                        created_by=admin_user
                    )
                    self.stdout.write(f'  → Added 50 units to warehouse')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  → Could not add stock: {e}'))
            else:
                self.stdout.write(f'  Product already exists: {product.name}')

        self.stdout.write(self.style.SUCCESS('\n✅ Sample data created successfully!'))
        self.stdout.write(self.style.SUCCESS('\nLogin credentials:'))
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Warehouse Manager: wh_manager / manager123')
        self.stdout.write('  Branch Manager: br_manager / manager123')
        self.stdout.write('  Cashier: cashier1 / cashier123')
