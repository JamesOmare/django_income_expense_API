from django.shortcuts import render
from rest_framework.views import APIView
from datetime import date, timedelta
from expenses.models import Expense
from rest_framework import status
from rest_framework.response import Response


# Create your views here.
class ExpenseSummaryStats(APIView):
    
    def get_amount_for_category(self, expense_queryset, category):
        expenses = expense_queryset.filter(category = category)
        amount = 0
        
        for expense in expenses:
            amount += expense.amount
            
        return {'amount': str(amount)}
        
    def get_category(self, expense):
        return expense.category
        
    def get(self, request):
        todays_date = date.today()
        Ayearago = todays_date - timedelta(days=30 * 12)
        expenses = Expense.objects.filter(owner = request.user, created_at__gte = Ayearago, created_at__lte = todays_date)
        
        
        final = {}

        # we add set to remove duplicates
        categories = list(set(map(self.get_category, expenses)))
        
        for expense in expenses:
            for category in categories:
                final[category] = self.get_amount_for_category(expenses, category)
                

        return Response({
            'category_data': final
        }, status = status.HTTP_200_OK)
                
        