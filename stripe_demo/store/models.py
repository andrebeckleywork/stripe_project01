from django.db import models


class Product(models.Model):
    """A product available for sale in the shop."""
    name        = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price       = models.PositiveIntegerField(
                      help_text="Price in pence (e.g. 1500 = £15.00)")
    emoji       = models.CharField(max_length=10, default="🛍️",
                      help_text="Emoji shown on the storefront")
    available   = models.BooleanField(default=True,
                      help_text="Uncheck to hide from the shop")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (£{self.price / 100:.2f})"

    @property
    def price_display(self):
        """Return a formatted price string e.g. '£15.00'."""
        return f"£{self.price / 100:.2f}"


class Order(models.Model):
    """A record of a completed Stripe payment."""
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('complete',  'Complete'),
        ('cancelled', 'Cancelled'),
    ]

    product           = models.ForeignKey(Product, on_delete=models.PROTECT,
                            related_name='orders')
    stripe_session_id = models.CharField(max_length=200, unique=True)
    customer_email    = models.EmailField()
    amount_paid       = models.PositiveIntegerField(help_text="Amount in pence")
    currency          = models.CharField(max_length=3, default='GBP')
    status            = models.CharField(max_length=10, choices=STATUS_CHOICES,
                            default='pending')
    created_at        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} — {self.product.name} ({self.status})"

    @property
    def amount_display(self):
        return f"£{self.amount_paid / 100:.2f}"