from django.db import models

# Create your models here.
class Income(models.Model):
    SOURCE_OPTIONS = [
        ('SALARY', 'SALARY'),
        ('BUSINESS', 'BUSINESS'),
        ('INVESTMENT', 'INVESTMENT'),
        ('OTHERS', 'OTHERS'),
    ]
    
    category = models.CharField(choices = SOURCE_OPTIONS, max_length = 255)
    amount = models.DecimalField(max_digits = 10, decimal_places = 2)
    description = models.TextField()
    owner = models.ForeignKey(to = 'authentication.User', on_delete = models.CASCADE)
    created_at = models.DateTimeField(null = False, blank = False, auto_now_add = True)
    
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return str(self.owner) + 's income'