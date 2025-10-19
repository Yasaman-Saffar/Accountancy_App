from django.db import models

class Question(models.Model):
    LEVEL_CHOICE = [
        ('easy' , 'آسان'),
        ('medium' , 'متوسط'),
        ('hard' , 'سخت')
        ]
    
    level = models.CharField(max_length=10, choices=LEVEL_CHOICE, verbose_name='سطح سوال')
    buy_price = models.DecimalField(max_digits=10,decimal_places=0, verbose_name='قیمت فروش')
    sell_price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='قیمت فروش')
    stock = models.PositiveIntegerField(default=0, verbose_name='تعداد در بانک')
    
    class Meta:
        verbose_name = 'سوال'
        verbose_name_plural = 'سوال‌ها'
        ordering = ['level']
        
    def __str__(self):
        return f"{self.get_level_display()} - خرید: {self.buy_price} / فروش: {self.sell_price} (موجودی: {self.stock})"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            if self.level == 'easy':
                self.stock = 100
                self.buy_price = 100
                self.sell_price = 150
            elif self.level == 'medium':
                self.stock = 60
                self.buy_price = 200
                self.sell_price = 350
            elif self.level == 'hard':
                self.stock = 40
                self.buy_price = 300
                self.sell_price = 600
        super().save(*args, **kwargs)
        