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
            'redirect_url': reverse('bank_home')
        })
    return render(request, 'bank/buying_questions.html', {
        'teams': teams,
        'questions': questions,
    })