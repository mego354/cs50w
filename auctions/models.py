from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F
from django.forms import ValidationError

class User(AbstractUser):
    pass




class Category(models.Model):
    name = models.CharField(max_length=30)
    count = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        listings_count = Listing.objects.filter(category=self).count()
        self.count = listings_count
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="listings")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="listings")
    title = models.CharField(max_length=200)
    description = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    price = models.FloatField(validators=[MinValueValidator(0.0)])
    current_price = models.FloatField(blank=True, null=True)
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="won")

    def save(self, *args, **kwargs):
        largest_bid = None
        try:
            largest_bid = Bid.objects.filter(listing=self).order_by('-money').first()
        except ValueError:
            pass
        if not largest_bid:
            self.current_price = self.price
        else:
            self.current_price = largest_bid.money

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}: {self.title} for {self.current_price}"


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids") 
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids") 
    money = models.FloatField()

    def save(self, *args, **kwargs):
        # Ensure that the bid money is at least the minimum of the listing price
        if self.money <= self.listing.price:
            raise ValidationError("Bid amount cannot be less than or equal the listing price.")
        super().save(*args, **kwargs)
        self.listing.save()

    def __str__(self):
        return f"{self.id}: {self.money} for {self.listing.title}"
    
class Comment(models.Model):
    text = models.TextField( blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments") 
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments") 


class Watchlist_Item(models.Model):
    listing = models.ManyToManyField(Listing) 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watch_items")

