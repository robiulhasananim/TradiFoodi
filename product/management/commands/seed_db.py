import random
import uuid
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from product.models import Category, Product, Review
from order.models import Order, OrderItem
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with a high volume of dummy data'

    def handle(self, *args, **options):
        self.stdout.write('Starting high-volume database seeding...')

        with transaction.atomic():
            # 1. Create Users
            self.stdout.write('Creating users...')
            
            # Admins
            admin_user, _ = User.objects.get_or_create(
                email='admin@tradifoodi.com',
                defaults={'first_name': 'Admin', 'last_name': 'User', 'role': 'admin', 'is_superuser': True}
            )
            admin_user.set_password('admin123')
            admin_user.save()

            # Sellers
            sellers = []
            for i in range(1, 6):
                seller, _ = User.objects.get_or_create(
                    email=f'seller{i}@tradifoodi.com',
                    defaults={
                        'first_name': f'Seller',
                        'last_name': f'Number {i}',
                        'role': 'seller',
                        'phone': f'01711111{i:03d}',
                        'city': random.choice(['Dhaka', 'Chittagong', 'Sylhet', 'Rajshahi', 'Khulna']),
                        'address': f'Industrial Road {i}',
                    }
                )
                seller.set_password('seller123')
                seller.save()
                sellers.append(seller)

            # Customers
            customers = []
            for i in range(1, 51):
                customer, _ = User.objects.get_or_create(
                    email=f'customer{i}@tradifoodi.com',
                    defaults={
                        'first_name': f'Customer',
                        'last_name': f'User {i}',
                        'role': 'customer',
                        'phone': f'01811111{i:03d}',
                        'city': random.choice(['Dhaka', 'Chittagong', 'Khulna', 'Barisal', 'Comilla', 'Sylhet', 'Noakhali']),
                        'address': f'House {i}, Road {random.randint(1,50)}, Sector {random.randint(1,15)}',
                        'postal_code': f'{1000 + i}'
                    }
                )
                customer.set_password('customer123')
                customer.save()
                customers.append(customer)

            self.stdout.write(self.style.SUCCESS(f'Created {len(sellers)} sellers and {len(customers)} customers.'))

            # 2. Create Categories
            self.stdout.write('Creating categories...')
            categories_data = [
                ('Organic Honey', 'pure-honey'),
                ('Traditional Ghee', 'pure-ghee'),
                ('Pure Spices', 'spices'),
                ('Homemade Pickles', 'pickles'),
                ('Nuts & Seeds', 'nuts-seeds'),
                ('Organic Rice', 'organic-rice'),
                ('Handmade Snacks', 'snacks'),
                ('Herbal Tea', 'herbal-tea'),
                ('Traditional Sweets', 'sweets'),
                ('Cold Pressed Oil', 'organic-oil')
            ]

            categories = []
            for name, slug_base in categories_data:
                cat, created = Category.objects.get_or_create(
                    slug=slug_base,
                    defaults={
                        'name': name,
                        'description': f'Premium quality {name.lower()} sourced directly from rural artisans.',
                        'image': f'https://picsum.photos/seed/{slug_base}/400/400'
                    }
                )
                categories.append(cat)
            
            self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories.'))

            # 3. Create Products (10 per category)
            self.stdout.write('Creating products...')
            products = []
            for cat in categories:
                for i in range(1, 11):
                    price = Decimal(random.randint(150, 2500))
                    original_price = price + Decimal(random.randint(50, 400))
                    
                    prod = Product.objects.create(
                        name=f'{cat.name} Premium Pack - {i}',
                        description=f'Experience the authentic taste of {cat.name} with this carefully curated premium selection. Harvested with care and packed for purity.',
                        price=price,
                        originalPrice=original_price,
                        stock=random.randint(20, 1000),
                        category=cat,
                        seller=random.choice(sellers),
                        thumbnail=f'https://picsum.photos/seed/{uuid.uuid4().hex}/400/400',
                        images=[f'https://picsum.photos/seed/{uuid.uuid4().hex}/800/800'],
                        ingredients=['Organic Raw Material', 'Natural Preservatives', 'Love'],
                        preparationTime=f'{random.randint(1, 15)} days',
                        servingSize=random.choice(['250g', '500g', '1kg', '2kg', '1L', '5L']),
                        isAvailable=True,
                        sizes=['Standard', 'Family Pack', 'Trial Size'] if cat.name != 'Organic Honey' else ['500ml', '1L'],
                        color=['Natural', 'Golden', 'Brown']
                    )
                    products.append(prod)

            self.stdout.write(self.style.SUCCESS(f'Created {len(products)} products (10 per category).'))

            # 4. Create Reviews
            self.stdout.write('Creating random reviews...')
            for prod in products:
                num_reviews = random.randint(2, 10) # At least 2 per product
                reviewers = random.sample(customers, num_reviews)
                for user in reviewers:
                    Review.objects.create(
                        product=prod,
                        user=user,
                        rating=random.randint(3, 5),
                        comment=random.choice([
                            'Absolutely wonderful!', 'Very authentic and pure.', 'The packaging was excellent.',
                            'I have been looking for this for a long time.', 'Will definitely order again!',
                            'Great value for money.', 'Perfect taste!', '100% genuine products.'
                        ])
                    )

            self.stdout.write(self.style.SUCCESS('Created exhaustive reviews for all products.'))

            # 5. Create Orders (100 sample orders)
            self.stdout.write('Creating sample orders...')
            order_statuses = ['pending', 'confirmed', 'preparing', 'delivered', 'cancelled']
            payment_statuses = ['pending', 'paid', 'failed']
            
            for i in range(100):
                customer = random.choice(customers)
                order = Order.objects.create(
                    user=customer,
                    payment_method='cod',
                    status=random.choice(order_statuses),
                    payment_status=random.choice(payment_statuses),
                    delivery_note=f'Handle with care. Order {i+1}'
                )

                # Add random 1-5 items
                num_items = random.randint(1, 5)
                order_products = random.sample(products, num_items)
                total = Decimal('0.00')
                
                for prod in order_products:
                    qty = random.randint(1, 4)
                    item = OrderItem.objects.create(
                        order=order,
                        product=prod,
                        quantity=qty,
                        price=prod.price,
                        size=random.choice(['Standard', 'Family Pack']) if prod.sizes else 'Standard',
                        color=random.choice(prod.color) if prod.color else 'Natural'
                    )
                    total += item.subtotal()
                
                order.total_amount = total
                order.save()

            self.stdout.write(self.style.SUCCESS(f'Created 100 sample orders with diverse items and statuses.'))
            self.stdout.write(self.style.SUCCESS('Database flushing and re-seeding completed with high volume!'))
