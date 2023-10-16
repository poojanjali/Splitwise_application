from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from .validators import validate_participants_limit,validate_expense_amount

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


# class CustomUserManager(BaseUserManager):
#     def create_user(self, userId, name, email, mobile_number, password=None, **extra_fields):
#         if not email:
#             raise ValueError('The Email field must be set')
#         email = self.normalize_email(email)
#         user = self.model(userId=userId, name=name, email=email, mobile_number=mobile_number, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, userId, name, email, mobile_number, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)

#         return self.create_user(userId, name, email, mobile_number, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    # userId = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    # mobile_number = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.name
    

class UserBalance(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    simplify_expense = models.BooleanField(default=False)


class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(CustomUser, related_name='groups_members')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Expense(models.Model):
    description = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True,related_name='group_type')
    payer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='expenses_paid')
    participants = models.ManyToManyField(CustomUser, related_name='expenses_participated',validators = [validate_participants_limit])
    expense_type = models.CharField(
        max_length=10,
        choices=[('EQUAL', 'Equal'), ('EXACT', 'Exact'), ('PERCENT', 'Percent')],
        default='EQUAL', validators=[validate_expense_amount]
    )

    def __str__(self):
        return self.description

class EqualExpense(models.Model):
    expense = models.OneToOneField(Expense, on_delete=models.CASCADE, related_name='equal_expense')
    split_amount = models.DecimalField(max_digits=10, decimal_places=2)

class ExactExpense(models.Model):
    expense = models.OneToOneField(Expense, on_delete=models.CASCADE, related_name='exact_expense')
    participant = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='exact_expense_participant')
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Calculate the total sum of shares for this exact expense
        total_shares = self.__class__.objects.filter(expense=self.expense).aggregate(total_shares=models.Sum('amount'))['total_shares']
        
        # If total_shares is not equal to the total amount, raise a ValidationError
        if total_shares is not None and total_shares != self.expense.total_amount:
            raise ValidationError("The total sum of shares must be equal to the total amount of the expense.")

        super(ExactExpense, self).save(*args, **kwargs)


class PercentExpense(models.Model):
    expense = models.OneToOneField(Expense, on_delete=models.CASCADE, related_name='percent_expense')
    participants = models.ManyToManyField(CustomUser)
    percentages = models.JSONField()  # Store participant-specific percentages

    def save(self, *args, **kwargs):
        # Verify if the total sum of percentages equals 100
        total_percentage = sum(self.percentages.values())

        if total_percentage != 100:
            raise ValidationError("Total percentage shares must add up to 100%.")

        super(PercentExpense, self).save(*args, **kwargs)

class Transaction(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    lender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='lender_transactions')
    borrower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='borrower_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    settled = models.BooleanField(default=False)
    date = models.DateField()
    

    def __str__(self):
        return f'{self.lender} to {self.borrower}: {self.amount}'

   






