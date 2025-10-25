from django.db import models

class Team(models.Model):
    # Basic information
    group_name = models.CharField(max_length=100, verbose_name='نام گروه')
    members = models.TextField(verbose_name='اعضای گروه')
    team_number = models.PositiveIntegerField(unique=True, verbose_name='شماره گروه')
    
    # Financial information
    cash = models.DecimalField(max_digits=12, decimal_places=0, default=700, verbose_name='پول نقد')
    bank_balance = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="موجودی حساب بانکی")
    
    # Items
    items = models.ManyToManyField('market.Item', through='market.TeamItem', related_name='teams', verbose_name="کالاهای خریداری‌شده")
    
    # Questions
    unsolved_questions = models.PositiveIntegerField(default=0, verbose_name="تعداد سوال‌های حل‌نشده")
    solved_questions = models.PositiveIntegerField(default=0, verbose_name="تعداد سوال‌های حل‌شده")
    
    # Assets and rank calaulations
    total_assets = models.DecimalField(max_digits=14, decimal_places=2, default=700, verbose_name="کل دارایی")
    rank = models.PositiveIntegerField(default=1, verbose_name="رتبه دارایی")
    
    class Meta:
        verbose_name = "گروه"
        verbose_name_plural = "گروه‌ها"
        ordering = ['team_number']

    def __str__(self):
        return f"{self.team_number} - {self.group_name}"
    
    def total_money(self):
        return self.cash + self.bank_balance

    def calculate_total_assets(self):
        items_value = sum([
            team_item.item.current_price * team_item.quantity
            for team_item in self.teamitem_set.all()
        ])
        self.total_assets = self.cash + self.bank_balance + items_value
        self.save()
        return self.total_assets

