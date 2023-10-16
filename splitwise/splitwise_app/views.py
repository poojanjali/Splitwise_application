from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect,get_object_or_404
from .models import Group,Expense, EqualExpense, ExactExpense, PercentExpense,Transaction,UserBalance
from .forms import GroupForm,ExpenseForm, EqualExpenseForm, ExactExpenseForm, PercentExpenseForm,TransactionForm,UserBalanceForm
# from django.contrib.auth.decorators import login_required
from django.urls import reverse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from splitwise_app import serializers
from django.views.generic.edit import UpdateView
from django.contrib.auth import get_user_model
User = get_user_model()

# def register(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('profile')  
#     else:
#         form = UserCreationForm()
#     return render(request, 'register.html', {'form': form})

# def user_login(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user = authenticate(request, username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect('profile') 
#     else:
#         form = AuthenticationForm()
#     return render(request, 'login.html', {'form': form})

class UserRegisterationAPIView(GenericAPIView):
    """
    An endpoint for the client to create a new User.
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.UserRegisterationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        return Response(data, status=status.HTTP_201_CREATED)

class UserLoginAPIView(GenericAPIView):
    """
    An endpoint to authenticate existing users using their email and password.
    """
    permission_classes = (AllowAny,)
    serializer_class = serializers.UserLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        serializer = serializers.CustomUserSerializer(user)
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        return Response(data, status=status.HTTP_200_OK)

class UserLogoutAPIView(GenericAPIView):
    """
    An endpoint to logout users.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# group management


def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            group.members.add(request.user)
            return redirect('group_list')
    else:
        form = GroupForm()
    return render(request, 'create_group.html', {'form': form})


def group_list(request):
    user = request.user
    user_groups = user.groups.all()
    return render(request, 'group_list.html', {'user_groups': user_groups})


def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    return render(request, 'group_detail.html', {'group': group})


def update_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user == group.creator:
        if request.method == 'POST':
            form = GroupForm(request.POST, instance=group)
            if form.is_valid():
                form.save()
                return redirect('group_list')
        else:
            form = GroupForm(instance=group)
        return render(request, 'update_group.html', {'form': form, 'group': group})
    else:
        return redirect('group_list')


def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user == group.creator:
        if request.method == 'POST':
            group.delete()
            return redirect('group_list')
        return render(request, 'delete_group.html', {'group': group})
    else:
        return redirect('group_list')

# Expense management


def create_expense(request):
    #creating an expense, based on the type (equal, exact, percent)
    if request.method == 'POST':
        expense_type = request.POST.get('expense_type')
        if expense_type == 'EQUAL':
            form = EqualExpenseForm(request.POST)
        elif expense_type == 'EXACT':
            form = ExactExpenseForm(request.POST)
        elif expense_type == 'PERCENT':
            form = PercentExpenseForm(request.POST)
        else:
            return redirect('expense_list')
        if form.is_valid():
            expense = form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    context = {'form': form}
    # if form.errors:
    #     context['participant_limit_error'] = "The maximum number of participants allowed is 1000."
    participant_limit_error = ''
    if 'participants' in form.errors:
        participant_limit_error = "The maximum number of participants allowed is 1000."

            # Check for expense amount error
    amount_limit_error = ''
    if 'amount' in form.errors:
        amount_limit_error = "The maximum amount allowed is INR 1,00,00,000."

    context = {'form': form,'participant_limit_error': participant_limit_error,'amount_limit_error': amount_limit_error}
    return render(request, 'create_expense.html', context)


def expense_list(request):
    expenses = Expense.objects.all()
    return render(request, 'expense_list.html', {'expenses': expenses})


def expense_detail(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    if expense.expense_type == 'EQUAL':
        return render(request, 'equal_expense_detail.html', {'expense': expense})
    elif expense.expense_type == 'EXACT':
        return render(request, 'exact_expense_detail.html', {'expense': expense})
    elif expense.expense_type == 'PERCENT':
        return render(request, 'percent_expense_detail.html', {'expense': expense})
    else:
        return render(request, 'expense_detail.html', {'expense': expense})


def update_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    # updating an expense based on the type
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'update_expense.html', {'form': form, 'expense': expense})

def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    # deleting an expense based on the type
    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')
    return render(request, 'delete_expense.html', {'expense': expense})

# Transaction management


def create_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    return render(request, 'create_transaction.html', {'form': form})


def transaction_list(request):
    transactions = Transaction.objects.all()
    return render(request, 'transaction_list.html', {'transactions': transactions})


def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    return render(request, 'transaction_detail.html', {'transaction': transaction})


def update_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'update_transaction.html', {'form': form, 'transaction': transaction})


def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    if request.method == 'POST':
        transaction.delete()
        return redirect('transaction_list')
    return render(request, 'delete_transaction.html', {'transaction': transaction})

#Simplify_balance option


def simplify_expenses(request):
    if request.method == 'POST':
        if request.POST.get('simplify_expenses') == 'on':
            expenses = Expense.objects.all()
            transactions = Transaction.objects.all()
            balances = UserBalance.objects.all()
            new_balances = {}
            for balance in balances:
                new_balances[balance.user.id] = balance.balance
            for expense in expenses:
                if not expense.settled:
                    for transaction in transactions.filter(expense=expense):
                        new_balances[transaction.lender.id] -= transaction.amount
                        new_balances[transaction.borrower.id] += transaction.amount

            for user_id, new_balance in new_balances.items():
                user_balance = UserBalance.objects.get(user_id=user_id)
                user_balance.balance = new_balance
                user_balance.save()

    return render(request, 'simplify_expenses.html')


#user_balances


def update_balance(request):
    user_profile = UserBalance.objects.get(user=request.user)

    if request.method == 'POST':
        form = UserBalanceForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect(reverse('profile'))
    else:
        form = UserBalanceForm(instance=user_profile)

    return render(request, 'balance_update.html', {'form': form})






