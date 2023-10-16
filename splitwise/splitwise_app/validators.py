from django.core.exceptions import ValidationError

def validate_participants_limit(participants):
    if len(participants) > 1000:
        raise ValidationError('The maximum number of participants allowed is 1000.')
    
def validate_expense_amount(value):
    if value > 10000000:  # The maximum amount is 1 crore, which is 10,000,000
        raise ValidationError('The maximum amount allowed is INR 1,00,00,000.')
