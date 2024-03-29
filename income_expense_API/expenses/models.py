from django.db import models

# Create your models here.
class Expense(models.Model):
    CATEGORY_OPTIONS = [
        ('ONLINE_SERVICES', 'ONLINE_SERVICES'),
        ('TRAVEL', 'TRAVEL'),
        ('FOOD', 'FOOD'),
        ('RENT', 'RENT'),
        ('OTHERS', 'OTHERS'),
    ]
    
    category = models.CharField(choices = CATEGORY_OPTIONS, max_length = 255)
    amount = models.DecimalField(max_digits = 10, decimal_places = 2)
    description = models.TextField()
    owner = models.ForeignKey(to = 'authentication.User', on_delete = models.CASCADE)
    created_at = models.DateTimeField(null = False, blank = False, auto_now_add = True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return str(self.owner) + 's expense'