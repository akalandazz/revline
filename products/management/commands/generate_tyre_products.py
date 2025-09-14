import random
from django.core.management.base import BaseCommand
from products.models import Product, Category, Brand

class Command(BaseCommand):
    help = 'Generates 10 tyre products for the database.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating tyre products...')

        # Get or create the category
        category, created = Category.objects.get_or_create(
            name='Wheels & Tires',
            defaults={'slug': 'wheels-tires'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Category "Wheels & Tires" created.'))

        # Get or create a generic brand
        brand, created = Brand.objects.get_or_create(
            name='Chevrolet',
            defaults={'slug': 'chevrolet'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Brand "Chevrolet" created.'))

        # Tyre names and specs
        tyre_names = [
            ("Performance Pro", "225/45R17"),
            ("All-Terrain Grip", "265/70R16"),
            ("Eco Saver", "195/65R15"),
            ("Winter Max", "205/55R16"),
            ("Sport Contact", "245/40R18"),
            ("Highway Cruiser", "215/60R16"),
            ("Off-Road King", "315/75R16"),
            ("City Glide", "185/60R15"),
            ("Track Star", "255/35R19"),
            ("Touring Comfort", "235/50R18"),
        ]

        for name, spec in tyre_names:
            sku = f"TYRE-{spec.replace('/', '')}-{random.randint(1000, 9999)}"
            price = round(random.uniform(80.0, 300.0), 2)
            
            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': f"{name} {spec}",
                    'slug': f"{name.lower().replace(' ', '-')}-{spec.replace('/', '-')}",
                    'description': f"A high-quality {name} tyre with specification {spec}. Provides excellent performance and durability.",
                    'short_description': f"A reliable {name} tyre.",
                    'category': category,
                    'brand': brand,
                    'price': price,
                    'stock_quantity': random.randint(20, 100),
                    'is_active': True,
                    'is_featured': random.choice([True, False]),
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created product: "{product.name}"'))
            else:
                self.stdout.write(self.style.WARNING(f'Product with SKU "{sku}" already exists. Skipping.'))
        
        self.stdout.write(self.style.SUCCESS('Finished generating tyre products.'))
