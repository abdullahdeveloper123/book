from django.db import models

class Book(models.Model):
    name = models.TextField()
    quotes = models.TextField()
    genre = models.TextField()
    year = models.IntegerField()
    pages = models.IntegerField()
    desc = models.TextField()
    price = models.IntegerField()
    author = models.CharField(max_length=100)
    views=models.IntegerField(default=0, null=True)

    def __str__(self):
        return f"{self.name}-{self.desc}-{self.price} - {self.author}"
    

class Wishlist(models.Model):
    product_id = models.IntegerField()
    name = models.TextField()
    quotes = models.TextField()
    desc = models.TextField()
    price = models.IntegerField()
    author = models.CharField(max_length=100)
    user_id = models.IntegerField()
    genre = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} for User {self.user_id}"
    

class Order(models.Model):
    product_id = models.IntegerField()
    quantity = models.IntegerField()
    user_id = models.IntegerField(null=True)
    date = models.DateField(auto_now_add=True)
    name = models.TextField()
    quotes = models.TextField()
    genre = models.TextField()
    year = models.IntegerField()
    pages = models.IntegerField()
    desc = models.TextField()
    price = models.IntegerField()
    author = models.CharField(max_length=100)
    

    def __str__(self):
        return f"{self.name}-{self.desc}-{self.price} - {self.author}"

    def __str__(self):
        return f"{self.product_id}-{self.quantity}-{self.date}"
    



