from django.db import models
from market.models import Item

class CompetitionSetting(models.Model):
    duration_hours = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=0)
    bank_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    bank_interest_interval = models.PositiveIntegerField(default=60)
    initial_capital = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    start_time = models.DateTimeField(null=True, blank=True)
    
    total_inflation_rounds = models.PositiveIntegerField(default=0)
    applied_round = models.PositiveIntegerField(default=0)
    


class InflationPrice(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    round_number = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('item', 'round_number')
