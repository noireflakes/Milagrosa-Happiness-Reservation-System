from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cloudinary_storage.storage import MediaCloudinaryStorage

# Create your models here.

class Book(models.Model):

    user=models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    book_type = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    payment_method = models.CharField(max_length=20)
    payment_type = models.CharField(max_length=20)

    REFUNDCHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("declined", "Declined"),
        ("not requested", "Not Requested"),
        ("complete", "Complete")
    ]
    amount=models.IntegerField(blank=True, null=True)


    refund_status=models.CharField(max_length=20, choices=REFUNDCHOICES, default="not requested")
  
    def save(self, *args, **kwargs):
        if not self.amount:
            prices = {
            'Day Tour': 7500,
            'Night Tour': 8500,
            '22 Hours': 15000
            }
            down_payment_amount = 1000
            base_price = prices.get(self.book_type)
            if base_price:
                self.amount = down_payment_amount if self.payment_type == 'Down payment' else base_price

        super().save(*args, **kwargs)
    

    @property
    def event_status(self):
        today=timezone.now().date()
        if today>self.start_date:
            return "Not Started"
        elif today<=self.start_date and today>=self.end_date:
            return "Ongoing"
        elif today>self.end_date:
            return "Completed"

    
    def __str__(self):
        return f"{self.book_type} from {self.start_date} to {self.end_date}"
    

class Proof(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("declined", "Declined"),
    ]
    book=models.ForeignKey(Book, on_delete=models.CASCADE, default=1)
    img = models.ImageField(storage=MediaCloudinaryStorage(),upload_to='proof/payment_proof')
    payment_status = models.CharField(choices=STATUS_CHOICES, max_length=20, default="pending")
  
    def __str__(self):
        return f"{self.payment_status}"

