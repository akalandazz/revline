from django.core.management.base import BaseCommand
from django.utils.text import slugify
from vehicles.models import Make, VehicleModel, Engine, Vehicle
from products.models import Category, Brand, Product
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Import sample data for development'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create vehicle makes
        makes_data = [
            'Toyota', 'Honda', 'Ford', 'Chevrolet', 'Nissan', 
            'BMW', 'Mercedes-Benz', 'Audi', 'Volkswagen', 'Hyundai'
        ]
        makes = []
        for make_name in makes_data:
            make, created = Make.objects.get_or_create(
                name=make_name,
                defaults={'slug': slugify(make_name)}
            )
            makes.append(make)
            if created:
                self.stdout.write(f'Created make: {make_name}')

        # Create vehicle models
        models_data = {
            'Toyota': ['Camry', 'Corolla', 'Prius', 'RAV4', 'Highlander'],
            'Honda': ['Civic', 'Accord', 'CR-V', 'Pilot', 'Fit'],
            'Ford': ['F-150', 'Mustang', 'Focus', 'Explorer', 'Escape'],
            'Chevrolet': ['Silverado', 'Cruze', 'Equinox', 'Tahoe', 'Malibu'],
            'Nissan': ['Altima', 'Sentra', 'Rogue', 'Pathfinder', 'Maxima'],
        }
        
        vehicle_models = []
        for make in makes:
            if make.name in models_data:
                for model_name in models_data[make.name]:
                    model, created = VehicleModel.objects.get_or_create(
                        make=make,
                        name=model_name,
                        defaults={'slug': slugify(model_name)}
                    )
                    vehicle_models.append(model)
                    if created:
                        self.stdout.write(f'Created model: {make.name} {model_name}')

        # Create engines
        engines_data = [
            {'name': '2.0L I4 Gasoline', 'displacement': 2.0, 'fuel_type': 'gasoline'},
            {'name': '2.5L I4 Gasoline', 'displacement': 2.5, 'fuel_type': 'gasoline'},
            {'name': '3.5L V6 Gasoline', 'displacement': 3.5, 'fuel_type': 'gasoline'},
            {'name': '2.0L I4 Turbo', 'displacement': 2.0, 'fuel_type': 'gasoline'},
            {'name': '1.8L I4 Hybrid', 'displacement': 1.8, 'fuel_type': 'hybrid'},
        ]
        
        engines = []
        for engine_data in engines_data:
            engine, created = Engine.objects.get_or_create(**engine_data)
            engines.append(engine)
            if created:
                self.stdout.write(f'Created engine: {engine.name}')

        # Create vehicles
        for model in vehicle_models[:10]:  # Limit for demo
            for year in range(2018, 2025):
                engine = random.choice(engines)
                vehicle, created = Vehicle.objects.get_or_create(
                    make=model.make,
                    model=model,
                    year=year,
                    engine=engine
                )
                if created:
                    self.stdout.write(f'Created vehicle: {vehicle}')

        # Create categories
        categories_data = [
            'Engine Parts', 'Brake System', 'Suspension', 'Electrical',
            'Filters', 'Belts & Hoses', 'Cooling System', 'Exhaust',
            'Transmission', 'Body Parts'
        ]
        
        categories = []
        for cat_name in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_name,
                defaults={'slug': slugify(cat_name)}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {cat_name}')

        # Create brands
        brands_data = [
            'OEM', 'Bosch', 'ACDelco', 'Motorcraft', 'Beck Arnley',
            'Genuine Parts', 'Febi', 'Mann Filter', 'NGK', 'Denso'
        ]
        
        brands = []
        for brand_name in brands_data:
            brand, created = Brand.objects.get_or_create(
                name=brand_name,
                defaults={'slug': slugify(brand_name)}
            )
            brands.append(brand)
            if created:
                self.stdout.write(f'Created brand: {brand_name}')

        # Create sample products
        product_templates = [
            {'name': 'Oil Filter', 'base_price': 12.99, 'weight': 0.5},
            {'name': 'Air Filter', 'base_price': 18.50, 'weight': 0.3},
            {'name': 'Brake Pads Set', 'base_price': 89.99, 'weight': 2.5},
            {'name': 'Spark Plugs Set', 'base_price': 45.99, 'weight': 0.8},
            {'name': 'Cabin Filter', 'base_price': 24.99, 'weight': 0.4},
            {'name': 'Fuel Filter', 'base_price': 35.99, 'weight': 1.2},
            {'name': 'Serpentine Belt', 'base_price': 42.50, 'weight': 1.0},
            {'name': 'Radiator', 'base_price': 185.99, 'weight': 8.5},
        ]

        for i, template in enumerate(product_templates):
            for brand in brands[:5]:  # Create variants for different brands
                part_number = f"P{1000 + i}{brand.id:02d}"
                
                product, created = Product.objects.get_or_create(
                    part_number=part_number,
                    defaults={
                        'name': f"{brand.name} {template['name']}",
                        'category': random.choice(categories),
                        'brand': brand,
                        'description': f"High-quality {template['name'].lower()} from {brand.name}. "
                                     f"Direct replacement for OEM part. Fits multiple vehicle applications.",
                        'short_description': f"Premium {template['name'].lower()} for reliable performance.",
                        'price': Decimal(str(template['base_price'])),
                        'stock_quantity': random.randint(5, 50),
                        'weight': Decimal(str(template['weight'])),
                        'is_active': True,
                    }
                )
                
                if created:
                    # Add compatibility with random vehicles
                    compatible_vehicles = random.sample(
                        list(Vehicle.objects.all()[:20]), 
                        k=random.randint(3, 8)
                    )
                    product.compatible_vehicles.set(compatible_vehicles)
                    
                    self.stdout.write(f'Created product: {product.name}')

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))# Vehicle compatibility API views
