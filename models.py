from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Property(models.Model):

    PROPERTY_TYPES = [
        ('Apartment', 'Apartment'),
        ('Villa', 'Villa'),
        ('Office', 'Office'),
    ]

    LISTING_TYPES = [
        ('For Sale', 'For Sale'),
        ('Monthly Rent', 'Monthly Rent'),
        ('Daily Rent', 'Daily Rent'),
    ]

    PROPERTY_STATUS = [
        ('Available', 'Available'),
        ('Rented', 'Rented'),
        ('Sold', 'Sold'),
        ('Pending', 'Pending'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    favorites = models.ManyToManyField(
    User,
    related_name='favorite_properties',
    blank=True
    )  

    title = models.CharField(max_length=200)
    description = models.TextField()
    city = models.CharField(max_length=100)

    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    listing_type = models.CharField(max_length=50, choices=LISTING_TYPES)
    status = models.CharField(max_length=50,choices=PROPERTY_STATUS,default='Available')

    price = models.DecimalField(max_digits=12, decimal_places=2)
    size = models.IntegerField()
    year_built = models.IntegerField()

    elevator = models.BooleanField(default=False)
    parking = models.BooleanField(default=False)

    floor = models.IntegerField(null=True, blank=True)
    floors = models.IntegerField(null=True, blank=True)
    rooms = models.CharField(max_length=50, blank=True)

    image = models.ImageField(upload_to='properties/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(
       default=0
    )
    featured = models.BooleanField(
    default=False
    )

    @property
    def average_rating(self):
        reviews = self.reviews.all()

        if reviews.exists():
            total = 0

            for review in reviews:
                total += review.rating

            return round(total / reviews.count(), 1)

        return 0

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Properties"
        ordering = ['-created_at']


class Review(models.Model):

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    rating = models.IntegerField(
    choices=[
        (5, '5 - Excellent'),
        (4, '4 - Good'),
        (3, '3 - Average'),
        (2, '2 - Poor'),
        (1, '1 - Very Poor'),
    ],

    validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
    ]
)

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.property.title}"

    class Meta:
        ordering = ['-created_at']


class ContactMessage(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)

    email = models.EmailField()

    subject = models.CharField(max_length=200)

    message = models.TextField()

    admin_reply = models.TextField(
        blank=True
    )

    is_answered = models.BooleanField(
        default=False
    )

    replied_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        if self.admin_reply:

            self.is_answered = True

            if not self.replied_at:
                self.replied_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):

        return self.name

    class Meta:

        ordering = ['-created_at']

class PropertyInquiry(models.Model):

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='inquiries'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)

    email = models.EmailField()

    message = models.TextField()

    admin_reply = models.TextField(
        blank=True
    )

    is_answered = models.BooleanField(
        default=False
    )

    replied_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        if self.admin_reply:

            self.is_answered = True

            if not self.replied_at:
                self.replied_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Inquiry for {self.property.title}"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Property Inquiries"


class ChatMessage(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    question = models.TextField()

    answer = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.question[:50]

    class Meta:
        ordering = ['-created_at']

class PropertyView(models.Model):

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='property_views'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    viewed_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        if self.user:
            return f"{self.user.username} viewed {self.property.title}"

        return f"Anonymous viewed {self.property.title}"

    class Meta:
        ordering = ['-viewed_at']