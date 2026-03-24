from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.contrib.auth.models import User
from decimal import Decimal
from budgets.models import BudgetGoal
from transactions.models import Transaction


class Command(BaseCommand):
    help = 'Generuj raport budżetu dla użytkownika'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username użytkownika',
            default='test123',
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['text', 'csv'],
            default='text',
            help='Format wyjścia',
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Ścieżka do pliku wyjściowego (dla CSV)',
            default=None,
        )

    def handle(self, *args, **options):
        username = options['user']
        output_format = options['format']
        output_file = options.get('output')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Użytkownik "{username}" nie istnieje'))
            return
        
        # Pobierz dane
        goals = BudgetGoal.objects.filter(user=user)
        transactions = Transaction.objects.filter(account__user=user)
        
        if output_format == 'text':
            self._output_text(user, goals, transactions)
        else:
            self._output_csv(user, goals, transactions, output_file)
    
    def _output_text(self, user, goals, transactions):
        """Wyjście tekstowe (tabelaryczne)"""
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS(f'RAPORT BUDŻETU - {user.username.upper()}'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        # Podsumowanie całkowite
        total_expenses = transactions.filter(transaction_type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        total_income = transactions.filter(transaction_type='INCOME').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        balance = total_income - total_expenses
        
        self.stdout.write(self.style.WARNING(f'Przychody:     {total_income:>10.2f} zł'))
        self.stdout.write(self.style.ERROR(f'Wydatki:       {total_expenses:>10.2f} zł'))
        self.stdout.write(self.style.SUCCESS(f'Bilans:        {balance:>10.2f} zł'))
        
        self.stdout.write(self.style.SUCCESS('\n' + '-'*60))
        self.stdout.write(self.style.SUCCESS('CELE BUDŻETOWE'))
        self.stdout.write(self.style.SUCCESS('-'*60 + '\n'))
        
        if goals.exists():
            for goal in goals:
                spent = goal.transactions.filter(transaction_type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
                progress = (spent / goal.allocated_amount * 100) if goal.allocated_amount > 0 else 0
                
                self.stdout.write(f'📊 {goal.name}')
                self.stdout.write(f'   Konto: {goal.account.name}')
                self.stdout.write(f'   Alokacja: {goal.allocated_amount:.2f} zł')
                self.stdout.write(f'   Wydano: {spent:.2f} zł')
                self.stdout.write(f'   Ostatało: {goal.balance:.2f} zł')
                self.stdout.write(f'   Postęp: {progress:.1f}%')
                self.stdout.write('')
        else:
            self.stdout.write('Brak celów budżetowych')
        
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
    
    def _output_csv(self, user, goals, transactions, output_file=None):
        """Wyjście CSV"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Nagłówek
        writer.writerow(['Raport Budżetu', user.username])
        writer.writerow([])
        
        # Podsumowanie
        total_expenses = transactions.filter(transaction_type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        total_income = transactions.filter(transaction_type='INCOME').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        writer.writerow(['Przychody', float(total_income)])
        writer.writerow(['Wydatki', float(total_expenses)])
        writer.writerow(['Bilans', float(total_income - total_expenses)])
        writer.writerow([])
        
        # Cele
        writer.writerow(['Cel', 'Konto', 'Alokacja', 'Wydano', 'Pozostało', 'Postęp %'])
        for goal in goals:
            spent = goal.transactions.filter(transaction_type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            progress = (spent / goal.allocated_amount * 100) if goal.allocated_amount > 0 else 0
            
            writer.writerow([
                goal.name,
                goal.account.name,
                float(goal.allocated_amount),
                float(spent),
                float(goal.balance),
                f'{progress:.1f}'
            ])
        
        csv_content = output.getvalue()
        
        if output_file:
            # Zapisz do pliku
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(csv_content)
                self.stdout.write(self.style.SUCCESS(f'✅ Raport zapisany: {output_file}'))
            except IOError as e:
                self.stdout.write(self.style.ERROR(f'❌ Błąd zapisu: {e}'))
        else:
            # Wyświetl na stdout
            self.stdout.write(csv_content)
