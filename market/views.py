from django.shortcuts import render
from accounts.models import Team
from django.http import JsonResponse
from .models import Item, TeamItem
from decimal import Decimal
from django.db import transaction

def get_team_item_info(request):
    team_id = request.GET.get('team_id')
    try:
        team = Team.objects.get(id=team_id)
        team_item = TeamItem.objects.filter(team=team)
        
        data = []
        for t_item in team_item:
            if t_item.quantity != 0:
                data.append({
                    'item': t_item.item.name,
                    'quantity': t_item.quantity,
                })
                
        return JsonResponse({'items': data})
    except Team.DoesNotExist:
        return JsonResponse({'error': 'تیمی با این شناسه وجود ندارد'})

@transaction.atomic
def dealing_items(request):
    teams = Team.objects.all()
    items = Item.objects.all()
    
    if request.method == 'POST':
        team_id = request.POST.get('team')
        operation = request.POST.get('operation')
        pay_method = request.POST.get('pay_method')
        cash_part = Decimal(request.POST.get('cash_part') or 0)
        bank_part = Decimal(request.POST.get('bank_part') or 0)

        team = Team.objects.get(id=team_id)
        
        team_items = []
        results = []
        cart = []
        buyOrSell = []
        items_price = Decimal(0)
        
        # Calculating the money that must be paid
        for item in items:
            qty_str = request.POST.get(f'item_{item.id}')
            if not qty_str or int(qty_str) == 0:
                continue
            quantity = int(qty_str)
            subtotal = item.current_price * quantity
            cart.append((item, quantity, subtotal))
            
        items_price = sum(subtotal for _, _, subtotal in cart)
        
        if pay_method == 'cash':
            cash_part = items_price
            bank_part = 0
        elif pay_method == 'bank':
            bank_part = items_price
            cash_part = 0
            
        total_payment = cash_part + bank_part
        if total_payment != items_price:
            return JsonResponse({'error': f"مبلغ پرداختی ({total_payment}) (ها)باید دقیقاً برابر با قیمت کالا ({items_price}) باشد"})
        
            
        if operation == 'buying':
            if team.cash < cash_part:
                return JsonResponse({'error': f"موجودی نقدی گروه {team.team_number} برای خرید کالا کافی نیست."})
            elif team.bank_balance < bank_part:
                return JsonResponse({'error': f"موجودی بانکی گروه {team.team_number} برای خرید کالا کافی نیست."})
            
            for item, quantity, subtotal in cart:
                team_item, _ = TeamItem.objects.get_or_create(team=team, item=item)
                
                team_item.quantity += quantity
                team_items.append(team_item)
                buyOrSell.append(f'{quantity} عدد {item.name}')
                
            team.cash -= cash_part
            team.bank_balance -= bank_part
            items_str = '\n'.join(buyOrSell)
            results.append(f'گروه {team.group_name}، \n {items_str} خریداری کرد')

        
        elif operation == 'selling':
            for item, quantity, subtotal in cart:
                team_item = TeamItem.objects.get(team=team, item=item)
                if team_item.quantity < quantity:
                    return JsonResponse({'error' : f"تیم موجودی کافی از {item.name} ندارد"})
                
                team_item.quantity -= quantity
                team_items.append(team_item)
                buyOrSell.append(f'{quantity} عدد {item.name}')
                
            team.cash += cash_part
            team.bank_balance += bank_part
            items_str = '\n'.join(buyOrSell)
            results.append(f"فروش {items_str} \n توسط تیم {team.group_name} انجام شد")
            
            
        TeamItem.objects.bulk_update(team_items, ['quantity'])
        team.save()
        team.calculate_total_assets()

        if not results:
            return JsonResponse({'error': "هیچ کالایی برای معامله انتخاب نشده است"})

        return JsonResponse({'success': results})

    return render(request, 'market/dealing_items.html', {
        'teams': teams,
        'items': items,
    })

        
    
            