# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from .models import CustomUser  # Import your CustomUser model

# class CustomUserCreationForm(UserCreationForm):
#     userId = forms.IntegerField(help_text='Required. Enter a unique User ID.')
#     name = forms.CharField(max_length=100)
#     email = forms.EmailField()
#     mobile_number = forms.CharField(max_length=15, help_text='Required. Enter a valid mobile number.')

#     class Meta:
#         model = CustomUser
#         fields = ('userId', 'name', 'email', 'mobile_number', 'password1', 'password2')

from .models import Group,Expense,EqualExpense, ExactExpense, PercentExpense,Transaction,UserBalance
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
User = get_user_model()

from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django import forms
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email",)

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("email",)



class UserBalanceForm(forms.ModelForm):
    class Meta:
        model = UserBalance
        fields = ['simplify_expense']

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description','total_amount','expense_type']

class EqualExpenseForm(forms.ModelForm):
    class Meta:
        model = EqualExpense
        fields = ['expense','split_amount']

class ExactExpenseForm(forms.ModelForm):
    class Meta:
        model = ExactExpense
        fields = ['expense','participant','amount']

class PercentExpenseForm(forms.ModelForm):
    class Meta:
        model = PercentExpense
        fields = ['expense','participants','percentages']

    percents = forms.CharField(
        label='Percentage Splits',
        help_text='Enter user percentages separated by commas (e.g., "user1:40, user2:30, user3:30")'
    )

    def clean_percents(self):
        data = self.cleaned_data['percents']
        # Implement custom validation to ensure correct percentage splits
        # You can split the input data, calculate total percentage, and validate it.
        return data
    
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['expense', 'lender', 'borrower', 'amount', 'settled']

class AddUserToGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['members']

class UpdateUserToGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['members']  # Field to manage group members

    def __init__(self, *args, **kwargs):
        super(UpdateUserToGroupForm, self).__init__(*args, **kwargs)

        # Add a field for the user you want to add to or remove from the group
        self.fields['user_to_add'] = forms.ModelChoiceField(
            queryset=User.objects.all(),
            required=False,
            label="User to Add to the Group",
        )

        self.fields['user_to_remove'] = forms.ModelChoiceField(
            queryset=User.objects.all(),
            required=False,
            label="User to Remove from the Group",
        )

# class DeleteGroupMemberForm(forms.Form):
#     member_to_delete = forms.ModelChoiceField(
#         queryset=Group.members.filter(id=id).delete(),
#         label="Select member to delete",
#     )


