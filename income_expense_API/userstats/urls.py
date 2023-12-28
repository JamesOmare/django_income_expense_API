from django.urls import path
from .views import (
    ExpenseSummaryStats
)

urlpatterns  = [
    path('expense_category_data/', ExpenseSummaryStats.as_view(), name = 'expense_category_summary'),
    
]                                