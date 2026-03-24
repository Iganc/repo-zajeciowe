from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from transactions.models import Transaction


class Command(BaseCommand):
    help = 'Usuwanie transakcji starszych niż X dni'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Liczba dni wstecz (domyślnie: 90)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Pokaż co będzie usunięte bez faktycznego usuwania',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Pobierz transakcje do usunięcia
        old_transactions = Transaction.objects.filter(date__lt=cutoff_date.date())
        count = old_transactions.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Brak transakcji starszych niż {days} dni')
            )
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'🔍 DRY RUN: Zostałoby usunięte {count} transakcji:\n'
                )
            )
            for trans in old_transactions[:10]:
                self.stdout.write(
                    f'  - {trans.date} | {trans.amount} zł | {trans.category.name if trans.category else "Brak"}'
                )
            if count > 10:
                self.stdout.write(f'  ... i {count - 10} więcej')
        else:
            # Zwróć pieniądze do kont przed usunięciem
            for transaction in old_transactions:
                account = transaction.account
                
                if transaction.budget_goal:
                    # Zwróć z celu
                    if transaction.transaction_type == 'EXPENSE':
                        transaction.budget_goal.balance += transaction.amount
                    else:
                        transaction.budget_goal.balance -= transaction.amount
                    transaction.budget_goal.save()
                else:
                    # Zwróć na konto
                    if transaction.transaction_type == 'EXPENSE':
                        account.balance += transaction.amount
                    else:
                        account.balance -= transaction.amount
                    account.save()
            
            # Usuń transakcje
            old_transactions.delete()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Usunięto {count} transakcji starszych niż {days} dni'
                )
            )
