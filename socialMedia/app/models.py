from django.db import models

class Book(models.Model):
    name = models.TextField()
    quotes = models.TextField()
    desc = models.TextField()
    price = models.IntegerField()
    author = models.CharField(max_length=100)
    views=models.IntegerField(default=0, null=True)

    def __str__(self):
        return f"{self.name}-{self.desc}-{self.price} - {self.author}"
    

class Wishlist(models.Model):
    product_id = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_id}"
    

class Order(models.Model):
    product_id = models.IntegerField()
    quantity = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_id}-{self.quantity}-{self.date}"
    



