from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام کالا")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت پایه")
    current_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت فعلی")

    class Meta:
        verbose_name = "کالا"
        verbose_name_plural = "کالاها"
        
    def __str__(self):
        return f"{self.name}"
    
    
class TeamItem(models.Model):
    team = models.ForeignKey('accounts.Team', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0, verbose_name="تعداد")

    class Meta:
        unique_together = ('team', 'item')
        verbose_name = "کالای تیم"
        verbose_name_plural = "کالاهای تیم"

    def __str__(self):
        return f"{self.team.name} - {self.item.name} ({self.quantity})"
