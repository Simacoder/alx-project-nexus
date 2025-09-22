# app/management/commands/add_sample_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.models import Category, Product

User = get_user_model()

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Create categories
        electronics, _ = Category.objects.get_or_create(
            name="Electronics", 
            defaults={"description": "Electronic devices"}
        )
        books, _ = Category.objects.get_or_create(
            name="Books", 
            defaults={"description": "Books and education"}
        )
        
        # Make a user a seller
        user = User.objects.first()
        if user:
            user.is_seller = True
            user.save()
            
            # Create sample products
            Product.objects.get_or_create(
                name="iPhone 15",
                defaults={
                    "description": "Latest iPhone",
                    "price": "15999.99",
                    "stock_quantity": 10,
                    "seller": user
                }
            )
            
        self.stdout.write("Sample data created!")