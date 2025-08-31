from django.db import models
from django.urls import reverse


class Make(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class VehicleModel(models.Model):
    make = models.ForeignKey(Make, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=50)
    slug = models.SlugField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['make', 'name']
        ordering = ['name']

    def __str__(self):
        return f"{self.make.name} {self.name}"


class Engine(models.Model):
    name = models.CharField(max_length=100)
    displacement = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    fuel_type = models.CharField(max_length=20, choices=[
        ('gasoline', 'Gasoline'),
        ('diesel', 'Diesel'),
        ('hybrid', 'Hybrid'),
        ('electric', 'Electric'),
    ])
    
    def __str__(self):
        return self.name


class Vehicle(models.Model):
    make = models.ForeignKey(Make, on_delete=models.CASCADE)
    model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    engine = models.ForeignKey(Engine, on_delete=models.CASCADE, null=True, blank=True)
    trim = models.CharField(max_length=50, blank=True)
    
    class Meta:
        unique_together = ['make', 'model', 'year', 'engine', 'trim']
        ordering = ['-year', 'make__name', 'model__name']
    
    def __str__(self):
        return f"{self.year} {self.make.name} {self.model.name}"