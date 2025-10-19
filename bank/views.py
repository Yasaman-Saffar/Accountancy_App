from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from .models import Question
from accounts.models import Team
from decimal import Decimal


def bank_home(request):
    return render(request, 'bank/bank_home.html')

def get_team_info(request):
    team_id = request.GET.get('team_id')
    try:
        team = Team.objects.get(id=team_id)
        data = {
            'name': team.group_name,
            'unsolved': team.unsolved_questions,
            'solved': team.solved_questions,
        }
        return JsonResponse(data)
    except Team.DoesNotExist:
        return JsonResponse({'error': 'تیمی با این شناسه وجود ندارد'})

def buying_questions(request):
    teams = Team.objects.all()
    questions = Question.objects.all()
    
    if request.method == 'POST':
        team_id = request.POST.get('team')
        level = request.POST.get('level')
        pay_method = request.POST.get('pay_method')
        cash_part = Decimal(request.POST.get('cash_part') or 0)
        bank_part = Decimal(request.POST.get('bank_part') or 0)
        
        team = Team.objects.get(id=team_id)
        question = Question.objects.get(level=level)
        price = question.buy_price
        
        if pay_method == 'cash':
            cash_part = price
            bank_part = 0
        elif pay_method == 'bank':
            bank_part = price
            cash_part = 0
            
        total_payment = cash_part + bank_part
        if total_payment != price:
            return JsonResponse({'error': f"مبلغ پرداختی ({total_payment}) باید دقیقاً برابر با قیمت سؤال ({price}) باشد."})
        
        if question.stock <= 0:
            return JsonResponse({'error': 'سؤال در بانک موجود نیست.'})
        
        if team.cash < cash_part:
            return JsonResponse({'error': f"موجودی نقدی گروه {team.team_number} کافی نیست."})

        if team.bank_balance < bank_part:
            return JsonResponse({'error': f"موجودی بانکی گروه {team.team_number} کافی نیست."})
        

        # Apply changes

        team.cash -= cash_part
        team.bank_balance -= bank_part
        team.unsolved_questions += 1
        team.save()

        question.stock -= 1
        question.save()
        
        team.calculate_total_assets()

        return JsonResponse({
            'success': f" گروه {team.team_number} یک سؤال {question.get_level_display()} خرید.",
        })
    return render(request, 'bank/buying_questions.html', {
        'teams': teams,
        'questions': questions,
    })
    
    
def trading_questions(request):
    teams = Team.objects.all()
    questions = Question.objects.all()
    
    if request.method == 'POST':
        seller_team_id = request.POST.get('seller_team')
        recipient_team_id = request.POST.get('recipient_team')
        consensual_price = Decimal(request.POST.get('consensual_price') or 0)
        pay_mathod = request.POST.get('pay_method')
        cash_part = Decimal(request.POST.get('cash_part') or 0)
        bank_part = Decimal(request.POST.get('bank_part') or 0)
        
        seller_team = Team.objects.get(id=seller_team_id)
        recipient_team = Team.objects.get(id=recipient_team_id)
        
        
        if pay_mathod == 'cash':
            cash_part = consensual_price
            bank_part = 0
        elif pay_mathod == 'bank':
            cash_part = 0
            bank_part = consensual_price
            
        total_payment = cash_part + bank_part
        if total_payment != consensual_price:
            return JsonResponse({'error': f"مبلغ پرداختی ({total_payment}) باید دقیقاً برابر با قیمت سؤال ({consensual_price}) باشد."})
        
        if seller_team.unsolved_questions <= 0:
            return JsonResponse({'error': f"سؤال حل نشده‌ای در بانک گروه {recipient_team.team_number} موجود نیست."})
        
        if recipient_team.cash < cash_part:
            return JsonResponse({'error': f"موجودی نقدی گروه {recipient_team.team_number} کافی نیست."})

        if recipient_team.bank_balance < bank_part:
            return JsonResponse({'error': f"موجودی بانکی گروه {recipient_team.team_number} کافی نیست."})
        
        recipient_team.cash -= cash_part
        recipient_team.bank_balance -= bank_part
        recipient_team.unsolved_questions += 1
        
        seller_team.cash += cash_part
        seller_team.bank_balance += bank_part
        seller_team.unsolved_questions -= 1
        
        recipient_team.save()
        recipient_team.calculate_total_assets()
        
        seller_team.save()
        seller_team.calculate_total_assets()
        
        return JsonResponse({
            'success': f" گروه {seller_team.team_number} یک سؤال با قیمت {consensual_price} به گروه {recipient_team.team_number} فروخت.",
        })
    return render(request, 'bank/trading_questions.html', {
        'teams': teams,
        'questions': questions,
    })
    
    
def receive_award(request):
    teams = Team.objects.all()
    questions = Question.objects.all()
    
    if request.method == 'POST':
        team_id = request.POST.get('team')
        level = request.POST.get('level')
        receive_method = request.POST.get('receive_method')
        cash_part = Decimal(request.POST.get('cash_part') or 0)
        bank_part = Decimal(request.POST.get('bank_part') or 0)
        
        team = Team.objects.get(id=team_id)
        question = Question.objects.get(level=level)
        price = question.sell_price
        
        if receive_method == 'cash':
            cash_part = price
            bank_part = 0
        elif receive_method == 'bank':
            cash_part = 0
            bank_part = price
            
        total_receiving = cash_part + bank_part
        if total_receiving != price:
            return JsonResponse({'error': f"مبلغ دریافتی ({total_receiving}) باید دقیقاً برابر با جایزه سؤال ({price}) باشد."})
        
        team.cash += cash_part
        team.bank_balance += bank_part
        team.save()
        team.calculate_total_assets()
        
        return JsonResponse({
            'success': f" گروه {team.team_number} جایزه یک سؤال {question.get_level_display()} را دریافت کرد.",
        })
    return render(request, 'bank/receive_award.html', {
        'teams': teams,
        'questions': questions,
    })
    
    
def withdrawal_and_deposit(request):
    teams = Team.objects.all()
    
    if request.method == 'POST':
        team_id = request.POST.get('team')
        money_value = Decimal(request.POST.get('money_value') or 0)
        operation = request.POST.get('operation')
        
        team = Team.objects.get(id=team_id)

    
        if operation == 'withdrawal' and team.bank_balance < money_value:
            return JsonResponse({'error': f' موجودی حساب گروه {team.team_number} برای برداشت کافی نیست'})

        if operation == 'withdrawal':
            team.cash += money_value
            team.bank_balance -= money_value
            message = f'گروه {team.team_number}، {money_value} از حسابش برداشت کرد.'
        elif operation == 'deposit':
            team.cash -= money_value
            team.bank_balance += money_value
            message = f'گروه {team.team_number}، {money_value} به حسابش وارد کرد.'
        else:
            return JsonResponse({'error': 'نوع عملیات نامعتبر است.'})
            
            
        team.save()
        team.calculate_total_assets()
        
        return JsonResponse({'success': message})

    return render(request, 'bank/withdrawal_and_deposit.html', {
        'teams': teams,
    })