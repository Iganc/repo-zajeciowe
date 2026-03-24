import csv
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from accounts.models import Account
from transactions.models import Transaction, Category
from decimal import Decimal
from datetime import datetime


class Command(BaseCommand):
    help = 'Import transakcji z pliku CSV. Format: data,account_id,kategoria,typ,kwota,opis'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='Ścieżka do pliku CSV')
        parser.add_argument(
            '--user',
            type=str,
            help='Username użytkownika (weryfikacja że konto należy do użytkownika)',
            default=None,
        )

    def handle(self, *args, **options):
        file_path = options['file']
        username = options['user']
        user = None
        
        # Jeśli podano username, weryfikuj że konta należą do tego użytkownika
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f'Użytkownik "{username}" nie istnieje')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                if not reader.fieldnames:
                    raise CommandError('Plik CSV jest pusty')
                
                imported = 0
                skipped = 0
                
                for row in reader:
                    try:
                        # Parse data
                        date_str = row.get('data', '').strip()
                        account_id_str = row.get('account_id', '').strip()
                        category_name = row.get('kategoria', '').strip()
                        transaction_type = row.get('typ', '').strip().upper()
                        amount_str = row.get('kwota', '').strip()
                        description = row.get('opis', '').strip()
                        
                        # Walidacja
                        if not all([date_str, account_id_str, category_name, transaction_type, amount_str]):
                            self.stdout.write(f'⚠️  Pominięto wiersz: brakuje wymaganych pól')
                            skipped += 1
                            continue
                        
                        # Parsuj datę
                        try:
                            transaction_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        except ValueError:
                            self.stdout.write(f'⚠️  Pominięto wiersz: nieprawidłowa data "{date_str}"')
                            skipped += 1
                            continue
                        
                        # Parsuj kwotę
                        try:
                            amount = Decimal(amount_str)
                        except:
                            self.stdout.write(f'⚠️  Pominięto wiersz: nieprawidłowa kwota "{amount_str}"')
                            skipped += 1
                            continue
                        
                        # Parsuj account_id
                        try:
                            account_id = int(account_id_str)
                        except ValueError:
                            self.stdout.write(f'⚠️  Pominięto wiersz: nieprawidłowe ID konta "{account_id_str}"')
                            skipped += 1
                            continue
                        
                        # Pobierz konto
                        try:
                            account = Account.objects.get(id=account_id)
                        except Account.DoesNotExist:
                            self.stdout.write(f'⚠️  Pominięto wiersz: konto z ID {account_id} nie znalezione')
                            skipped += 1
                            continue
                        
                        # Weryfikuj że konto należy do podanego użytkownika
                        if user and account.user != user:
                            self.stdout.write(f'⚠️  Pominięto wiersz: konto ID {account_id} nie należy do użytkownika {username}')
                            skipped += 1
                            continue
                        
                        # Pobierz kategorię
                        category = Category.objects.filter(
                            name__iexact=category_name
                        ).first()
                        if not category:
                            # Stwórz kategorię jeśli nie istnieje
                            category = Category.objects.create(
                                name=category_name,
                                type='EXPENSE' if transaction_type == 'EXPENSE' else 'INCOME'
                            )
                        
                        # Waliduj typ transakcji
                        if transaction_type not in ['EXPENSE', 'INCOME']:
                            self.stdout.write(f'⚠️  Pominięto wiersz: nieprawidłowy typ "{transaction_type}"')
                            skipped += 1
                            continue
                        
                        # Utwórz transakcję
                        transaction = Transaction.objects.create(
                            account=account,
                            category=category,
                            amount=amount,
                            transaction_type=transaction_type,
                            date=transaction_date,
                            description=description
                        )
                        
                        # Aktualizuj saldo konta
                        if transaction_type == 'EXPENSE':
                            account.balance -= amount
                        else:
                            account.balance += amount
                        account.save()
                        
                        imported += 1
                        
                    except Exception as e:
                        self.stdout.write(f'❌ Błąd w wierszu: {str(e)}')
                        skipped += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✅ Import zakończony:\n'
                        f'   Zaimportowane: {imported}\n'
                        f'   Pominięte: {skipped}'
                    )
                )
        
        except FileNotFoundError:
            raise CommandError(f'Plik "{file_path}" nie znaleziony')
