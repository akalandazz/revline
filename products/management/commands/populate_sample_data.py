import random
import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.files import File
from products.models import Product, Category, Brand, ProductImage


class Command(BaseCommand):
    help = 'Populates the database with 5 brands, 10 categories, and 50 products with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))
        
        # Clear existing data first
        if self.confirm_action('Do you want to clear existing products, brands, and categories? (y/N): '):
            Product.objects.all().delete()
            Brand.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING('Existing data cleared.'))
        
        # Create brands
        brands = self.create_brands()
        self.stdout.write(self.style.SUCCESS(f'Created {len(brands)} brands'))
        
        # Create categories
        categories = self.create_categories()
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))
        
        # Create products
        products_created = self.create_products(brands, categories)
        self.stdout.write(self.style.SUCCESS(f'Created {products_created} products'))
        
        self.stdout.write(self.style.SUCCESS('Data population completed successfully!'))

    def confirm_action(self, message):
        """Ask for user confirmation"""
        try:
            response = input(message)
            return response.lower() == 'y'
        except KeyboardInterrupt:
            return False

    def create_brands(self):
        """Create 5 automotive brands"""
        brand_data = [
            {
                'name': 'BMW',
                'description': 'Premium German automotive manufacturer known for luxury vehicles and innovative technology.',
                'website': 'https://www.bmw.com',
                'logo': None  # No BMW logo available
            },
            {
                'name': 'Mercedes-Benz',
                'description': 'German luxury automotive brand renowned for engineering excellence and premium vehicles.',
                'website': 'https://www.mercedes-benz.com',
                'logo': None  # No Mercedes logo available
            },
            {
                'name': 'Audi',
                'description': 'German automotive manufacturer known for quattro all-wheel drive and advanced technology.',
                'website': 'https://www.audi.com',
                'logo': None  # No Audi logo available
            },
            {
                'name': 'Toyota',
                'description': 'Japanese automotive manufacturer famous for reliability, quality, and hybrid technology.',
                'website': 'https://www.toyota.com',
                'logo': 'brands/toyota.png'
            },
            {
                'name': 'Ford',
                'description': 'American automotive company known for trucks, performance vehicles, and innovation.',
                'website': 'https://www.ford.com',
                'logo': 'brands/ford-logo.png'
            }
        ]
        
        brands = []
        for brand_info in brand_data:
            defaults = {
                'description': brand_info['description'],
                'website': brand_info['website'],
                'is_active': True
            }
            
            # Add logo if available
            if brand_info['logo'] and os.path.exists(f"media/{brand_info['logo']}"):
                defaults['logo'] = brand_info['logo']
            
            brand, created = Brand.objects.get_or_create(
                name=brand_info['name'],
                defaults=defaults
            )
            brands.append(brand)
            if created:
                self.stdout.write(f'  Created brand: {brand.name}')
            else:
                self.stdout.write(f'  Brand already exists: {brand.name}')
        
        return brands

    def create_categories(self):
        """Create 10 automotive categories"""
        category_data = [
            {
                'name': 'Engine Parts',
                'description': 'Essential engine components including filters, belts, and performance parts.',
                'image': None
            },
            {
                'name': 'Brake Systems',
                'description': 'Complete brake components for safety and performance including pads, rotors, and calipers.',
                'image': None
            },
            {
                'name': 'Suspension & Steering',
                'description': 'Suspension components and steering parts for optimal handling and comfort.',
                'image': None
            },
            {
                'name': 'Wheels & Tires',
                'description': 'Wheels, tires, and related accessories for all vehicle types.',
                'image': 'categories/category_wheels.png'
            },
            {
                'name': 'Lighting & Electrical',
                'description': 'Automotive lighting systems, electrical components, and accessories.',
                'image': None
            },
            {
                'name': 'Interior Accessories',
                'description': 'Interior upgrades, seat covers, floor mats, and comfort accessories.',
                'image': None
            },
            {
                'name': 'Exterior Accessories',
                'description': 'Body parts, exterior styling, and protection accessories.',
                'image': None
            },
            {
                'name': 'Fluids & Chemicals',
                'description': 'Motor oils, coolants, brake fluids, and automotive chemicals.',
                'image': None
            },
            {
                'name': 'Tools & Equipment',
                'description': 'Automotive tools, diagnostic equipment, and maintenance accessories.',
                'image': None
            },
            {
                'name': 'Performance Parts',
                'description': 'High-performance upgrades, exhaust systems, and tuning components.',
                'image': None
            }
        ]
        
        categories = []
        for cat_info in category_data:
            defaults = {
                'description': cat_info['description'],
                'is_active': True
            }
            
            # Add image if available
            if cat_info['image'] and os.path.exists(f"media/{cat_info['image']}"):
                defaults['image'] = cat_info['image']
            
            category, created = Category.objects.get_or_create(
                name=cat_info['name'],
                defaults=defaults
            )
            categories.append(category)
            if created:
                self.stdout.write(f'  Created category: {category.name}')
            else:
                self.stdout.write(f'  Category already exists: {category.name}')
        
        return categories

    def create_products(self, brands, categories):
        """Create 50 diverse automotive products"""
        products_data = [
            # Engine Parts
            ('Premium Air Filter', 'Engine Parts', ['BMW', 'Mercedes-Benz', 'Audi'], 45.99, 'High-flow air filter for enhanced engine performance'),
            ('Oil Filter Kit', 'Engine Parts', ['Toyota', 'Ford'], 24.99, 'Complete oil filter kit with gaskets'),
            ('Timing Belt', 'Engine Parts', ['BMW', 'Audi'], 89.99, 'Precision timing belt for optimal engine timing'),
            ('Spark Plug Set', 'Engine Parts', ['Toyota', 'Ford'], 39.99, 'High-performance spark plugs - set of 4'),
            ('Fuel Pump Assembly', 'Engine Parts', ['Mercedes-Benz', 'BMW'], 299.99, 'Electric fuel pump assembly with pressure regulator'),
            
            # Brake Systems
            ('Ceramic Brake Pads', 'Brake Systems', ['BMW', 'Mercedes-Benz'], 129.99, 'Low-dust ceramic brake pads for premium vehicles'),
            ('Brake Rotor Set', 'Brake Systems', ['Audi', 'BMW'], 199.99, 'Ventilated brake rotors - front pair'),
            ('Brake Caliper', 'Brake Systems', ['Mercedes-Benz', 'Audi'], 249.99, 'Remanufactured brake caliper assembly'),
            ('Brake Fluid DOT 4', 'Brake Systems', ['Toyota', 'Ford'], 19.99, 'High-performance brake fluid - 1L bottle'),
            ('Emergency Brake Cable', 'Brake Systems', ['Ford', 'Toyota'], 45.99, 'Parking brake cable assembly'),
            
            # Suspension & Steering
            ('Shock Absorber', 'Suspension & Steering', ['BMW', 'Mercedes-Benz'], 159.99, 'Gas-filled shock absorber for smooth ride'),
            ('Strut Assembly', 'Suspension & Steering', ['Toyota', 'Ford'], 199.99, 'Complete strut assembly with spring'),
            ('Tie Rod End', 'Suspension & Steering', ['Audi', 'BMW'], 35.99, 'Inner tie rod end for precise steering'),
            ('Sway Bar Link', 'Suspension & Steering', ['Ford', 'Toyota'], 29.99, 'Stabilizer bar link with bushings'),
            ('Control Arm', 'Suspension & Steering', ['Mercedes-Benz', 'Audi'], 119.99, 'Lower control arm with ball joint'),
            
            # Wheels & Tires
            ('Alloy Wheel 18"', 'Wheels & Tires', ['BMW', 'Mercedes-Benz'], 399.99, 'Lightweight alloy wheel - 18 inch diameter'),
            ('Performance Tire 225/45R18', 'Wheels & Tires', ['Audi', 'BMW'], 179.99, 'High-performance summer tire'),
            ('All-Season Tire 215/60R16', 'Wheels & Tires', ['Toyota', 'Ford'], 129.99, 'Reliable all-season tire for daily driving'),
            ('Wheel Hub Assembly', 'Wheels & Tires', ['Ford', 'Toyota'], 89.99, 'Complete wheel hub with bearings'),
            ('Tire Pressure Sensor', 'Wheels & Tires', ['BMW', 'Mercedes-Benz'], 75.99, 'TPMS sensor for wheel monitoring'),
            
            # Lighting & Electrical
            ('LED Headlight Bulb', 'Lighting & Electrical', ['BMW', 'Audi'], 89.99, 'Bright LED headlight bulb - H7 type'),
            ('Alternator', 'Lighting & Electrical', ['Toyota', 'Ford'], 199.99, 'Remanufactured alternator - 120A output'),
            ('Car Battery', 'Lighting & Electrical', ['Mercedes-Benz', 'BMW'], 149.99, 'AGM battery - 70Ah capacity'),
            ('Fog Light Assembly', 'Lighting & Electrical', ['Audi', 'Mercedes-Benz'], 79.99, 'Complete fog light with housing'),
            ('Ignition Coil', 'Lighting & Electrical', ['Toyota', 'Ford'], 45.99, 'High-performance ignition coil'),
            
            # Interior Accessories
            ('Leather Seat Cover', 'Interior Accessories', ['BMW', 'Mercedes-Benz'], 199.99, 'Premium leather seat cover set'),
            ('Floor Mat Set', 'Interior Accessories', ['Toyota', 'Ford'], 79.99, 'All-weather floor mat set - 4 pieces'),
            ('Dashboard Camera', 'Interior Accessories', ['Audi', 'BMW'], 129.99, 'HD dashboard camera with night vision'),
            ('Phone Mount', 'Interior Accessories', ['Mercedes-Benz', 'Audi'], 24.99, 'Magnetic phone mount for dashboard'),
            ('Steering Wheel Cover', 'Interior Accessories', ['Ford', 'Toyota'], 19.99, 'Leather-wrapped steering wheel cover'),
            
            # Exterior Accessories
            ('Side Mirror', 'Exterior Accessories', ['BMW', 'Mercedes-Benz'], 149.99, 'Power-folding side mirror with signal'),
            ('Front Grille', 'Exterior Accessories', ['Audi', 'BMW'], 299.99, 'Sport-style front grille assembly'),
            ('Mud Flaps', 'Exterior Accessories', ['Toyota', 'Ford'], 49.99, 'Heavy-duty mud flaps - set of 4'),
            ('Window Deflector', 'Exterior Accessories', ['Mercedes-Benz', 'Audi'], 89.99, 'In-channel window deflectors'),
            ('Roof Rack', 'Exterior Accessories', ['Ford', 'Toyota'], 199.99, 'Crossbar roof rack system'),
            
            # Fluids & Chemicals
            ('Synthetic Motor Oil 5W-30', 'Fluids & Chemicals', ['BMW', 'Mercedes-Benz'], 49.99, 'Full synthetic motor oil - 5L container'),
            ('Engine Coolant', 'Fluids & Chemicals', ['Toyota', 'Ford'], 19.99, 'Long-life engine coolant - 4L bottle'),
            ('Power Steering Fluid', 'Fluids & Chemicals', ['Audi', 'BMW'], 15.99, 'ATF power steering fluid - 1L bottle'),
            ('Glass Cleaner', 'Fluids & Chemicals', ['Mercedes-Benz', 'Audi'], 9.99, 'Streak-free glass cleaner spray'),
            ('Engine Degreaser', 'Fluids & Chemicals', ['Ford', 'Toyota'], 12.99, 'Heavy-duty engine degreaser spray'),
            
            # Tools & Equipment
            ('OBD2 Scanner', 'Tools & Equipment', ['BMW', 'Mercedes-Benz'], 79.99, 'Professional OBD2 diagnostic scanner'),
            ('Socket Set', 'Tools & Equipment', ['Toyota', 'Ford'], 59.99, 'Complete socket set with ratchet'),
            ('Jack Stand Set', 'Tools & Equipment', ['Audi', 'BMW'], 89.99, 'Heavy-duty jack stands - pair'),
            ('Torque Wrench', 'Tools & Equipment', ['Mercedes-Benz', 'Audi'], 119.99, 'Digital torque wrench - 1/2" drive'),
            ('Multimeter', 'Tools & Equipment', ['Ford', 'Toyota'], 45.99, 'Digital automotive multimeter'),
            
            # Performance Parts
            ('Cold Air Intake', 'Performance Parts', ['BMW', 'Audi'], 299.99, 'High-flow cold air intake system'),
            ('Exhaust System', 'Performance Parts', ['Mercedes-Benz', 'BMW'], 799.99, 'Cat-back exhaust system with muffler'),
            ('Performance Chip', 'Performance Parts', ['Audi', 'Mercedes-Benz'], 399.99, 'ECU performance tuning chip'),
            ('Turbo Upgrade Kit', 'Performance Parts', ['BMW', 'Audi'], 1299.99, 'Turbocharger upgrade kit'),
            ('Sport Springs', 'Performance Parts', ['Toyota', 'Ford'], 249.99, 'Lowering springs for improved handling'),
        ]
        
        products_created = 0
        
        for product_name, category_name, compatible_brands, price, description in products_data:
            # Get category
            category = next((cat for cat in categories if cat.name == category_name), None)
            if not category:
                continue
            
            # Get random brand from compatible brands
            compatible_brand_objects = [brand for brand in brands if brand.name in compatible_brands]
            if not compatible_brand_objects:
                continue
            
            brand = random.choice(compatible_brand_objects)
            
            # Generate SKU
            sku = f"{category.name.replace(' ', '').replace('&', '').upper()[:4]}-{brand.name.upper()[:3]}-{random.randint(1000, 9999)}"
            
            # Create product
            try:
                product, created = Product.objects.get_or_create(
                    sku=sku,
                    defaults={
                        'name': product_name,
                        'description': f"{description}. Compatible with {', '.join(compatible_brands)}. High-quality replacement part guaranteed to meet or exceed OEM specifications.",
                        'short_description': description,
                        'category': category,
                        'brand': brand,
                        'price': Decimal(str(price)),
                        'sale_price': Decimal(str(round(price * 0.85, 2))) if random.choice([True, False, False]) else None,  # 33% chance of sale
                        'stock_quantity': random.randint(10, 100),
                        'weight': round(random.uniform(0.5, 50.0), 2),
                        'compatible_makes': ', '.join(compatible_brands),
                        'year_from': random.randint(2010, 2018),
                        'year_to': random.randint(2019, 2024),
                        'condition': random.choice(['new', 'new', 'new', 'refurbished']),  # Mostly new
                        'is_active': True,
                        'is_featured': random.choice([True, False, False, False]),  # 25% chance of featured
                        'meta_title': f"{product_name} - {brand.name} | Auto Parts Store",
                        'meta_description': f"Buy {product_name} for {brand.name}. {description[:150]}..."
                    }
                )
                
                if created:
                    # Add product images if available
                    self.add_product_images(product)
                    products_created += 1
                    self.stdout.write(f'  Created product: {product.name} (SKU: {product.sku})')
                else:
                    self.stdout.write(f'  Product already exists: {sku}')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating product {product_name}: {str(e)}'))
        
        return products_created

    def add_product_images(self, product):
        """Add default product images"""
        # Available product images
        available_images = [
            "products/cold_air_intake.png",
            "products/exhaust_system.png",
            "products/jack_stand_set.png",
            "products/michelin.png",
            "products/multimeter.png",
            "products/obd2_scanner.png",
            "products/performance_chip.png",
            "products/socket_set.png",
            "products/sport_springs.png",
            "products/torque_wrench.png",
            "products/turbo_upgrade_kit.png",
        ]
        
        # Random chance to add 1-2 images
        num_images = random.choice([1, 1, 1, 2])  # 75% chance 1 image, 25% chance 2 images
        
        if num_images > 0:
            selected_images = random.sample(available_images, min(num_images, len(available_images)))
            
            for i, image_path in enumerate(selected_images):
                if os.path.exists(f"media/{image_path}"):
                    try:
                        ProductImage.objects.create(
                            product=product,
                            image=image_path,
                            alt_text=f"{product.name} - Image {i+1}",
                            is_primary=(i == 0),  # First image is primary
                            order=i
                        )
                    except Exception as e:
                        self.stdout.write(f'    Warning: Could not add image {image_path}: {str(e)}')