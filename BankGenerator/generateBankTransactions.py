import random
import calendar
from datetime import datetime, timedelta

all_variable_expenses = {
    'Water Bill': {'percentage': 0.02, 'range': (-20, 20)},
    'Trash Service': {'percentage': 0.01, 'range': (-15, 15)},
    'Gas Bill': {'percentage': 0.03, 'range': (-20, 20)},
    'Transportation Costs': {'percentage': 0.05, 'range': (-15, 15)},
    'Auto Maintenance': {'percentage': 0.04, 'range': (-10, 10)},
    'Car Registration': {'percentage': 0.02, 'range': (-5, 5)},
    'Car Insurance': {'percentage': 0.03, 'range': (-10, 10)},
    'Home Maintenance': {'percentage': 0.04, 'range': (-15, 15)},
    'Insurance (Home/Renter)': {'percentage': 0.03, 'range': (-10, 10)},
    'Health Care': {'percentage': 0.05, 'range': (-20, 20)},
    'Clothing': {'percentage': 0.03, 'range': (-30, 30)},
    'Gifts': {'percentage': 0.02, 'range': (-25, 25)},
    'Charitable Giving': {'percentage': 0.02, 'range': (-30, 30)},
    'Computer/Phone Replacement': {'percentage': 0.03, 'range': (-10, 10)},
    'Software Subscriptions': {'percentage': 0.01, 'range': (-20, 20)},
    'Entertainment Subscriptions': {'percentage': 0.02, 'range': (-15, 15)},
    'Vacation': {'percentage': 0.04, 'range': (-25, 25)},
    'Gym Membership': {'percentage': 0.02, 'range': (-20, 20)},
    'Education': {'percentage': 0.03, 'range': (-15, 15)},
    'Gaming': {'percentage': 0.02, 'range': (-30, 30)},
    'Christmas': {'percentage': 0.03, 'range': (-25, 25)},
    'Other Holidays': {'percentage': 0.02, 'range': (-20, 20)},
    'Hosting': {'percentage': 0.02, 'range': (-15, 15)},
    'Dates': {'percentage': 0.02, 'range': (-25, 25)},
    'Beauty': {'percentage': 0.02, 'range': (-20, 20)},
    'Property Taxes': {'percentage': 0.03, 'range': (-5, 5)},
    'Movies': {'percentage': 0.01, 'range': (-30, 30)},
    'Phone Bill': {'percentage': 0.02, 'range': (-10, 10)},
    'Life Insurance': {'percentage': 0.02, 'range': (-15, 15)},
    'Warehouse Membership': {'percentage': 0.01, 'range': (-10, 10)},
    'Credit Card Fee': {'percentage': 0.01, 'range': (-5, 5)},
    'House Decor': {'percentage': 0.02, 'range': (-20, 20)},
    'Banking Fees': {'percentage': 0.01, 'range': (-10, 10)},
    'Household Goods': {'percentage': 0.03, 'range': (-15, 15)},
    'Pet Care': {'percentage': 0.02, 'range': (-20, 20)},
    'Child Care': {'percentage': 0.04, 'range': (-15, 15)},
    'Kids'' Activities': {'percentage': 0.03, 'range': (-10, 10)},
    'Kids'' Sports': {'percentage': 0.03, 'range': (-15, 15)},
    'School Fees': {'percentage': 0.02, 'range': (-10, 10)},
    'Braces': {'percentage': 0.02, 'range': (-10, 10)},
    'Weddings': {'percentage': 0.03, 'range': (-20, 20)},
    'Taxes': {'percentage': 0.05, 'range': (-10, 10)},
    'Lawn Care': {'percentage': 0.02, 'range': (-15, 15)},
    'Miscellaneous': {'percentage': 0.03, 'range': (-20, 20)},
}



def random_adjustment(amount, min_percentage, max_percentage):
    """Adjusts the amount by a random percentage within the given range."""
    percentage = random.uniform(min_percentage, max_percentage)
    return amount + (amount * percentage / 100)

def calculate_expense(salary, percentage):
    """Calculates monthly expense based on annual salary and percentage."""
    return (salary * percentage) / 12

# ...

import random
import calendar

def random_adjustment(amount, min_percentage, max_percentage):
    """Adjusts the amount by a random percentage within the given range."""
    percentage = random.uniform(min_percentage, max_percentage)
    return amount + (amount * percentage / 100)

def calculate_expense(salary, percentage):
    """Calculates monthly expense based on annual salary and percentage."""
    return (salary * percentage) / 12

def simulate_monthly_transactions(year, month, start_balance, monthly_income, annual_salary, income_range, fixed_expenses, all_variable_expenses):
    """Simulates transactions for one month."""
    transactions = []
    current_balance = start_balance
    days_in_month = calendar.monthrange(year, month)[1]

    # Find paydays (Fridays) in the month
    paydays = find_fridays(year, month)

    # Distribute expenses between paydays
    last_day = 1
    for payday in paydays:
        selected_expenses = random.sample(list(all_variable_expenses.items()), random.randint(3, 5))
        for day in range(last_day, payday):
            for expense, details in selected_expenses:
                if random.random() < 0.5:  # Random chance to apply each expense
                    expense_amount = calculate_expense(annual_salary, details['percentage'])
                    adjusted_amount = random_adjustment(expense_amount, *details['range'])
                    transactions.append((day, expense, -adjusted_amount))
                    current_balance -= adjusted_amount
        last_day = payday + 1

        # Salary Deposit
        if payday <= days_in_month:
            adjusted_income = random_adjustment(monthly_income, *income_range)
            transactions.append((payday, 'Monthly Salary Deposit', adjusted_income))
            current_balance += adjusted_income

    # Final adjustments after last payday
    for day in range(last_day, days_in_month + 1):
        selected_expenses = random.sample(list(all_variable_expenses.items()), random.randint(2, 4))
        for expense, details in selected_expenses:
            if random.random() < 0.5:  # Random chance to apply each expense
                expense_amount = calculate_expense(annual_salary, details['percentage'])
                adjusted_amount = random_adjustment(expense_amount, *details['range'])
                transactions.append((day, expense, -adjusted_amount))
                current_balance -= adjusted_amount

    # Adjust remaining balance to leave a small amount
    final_adjustment = random.uniform(-100, 100)
    if current_balance + final_adjustment < 0:
        final_adjustment = -current_balance
    transactions.append((days_in_month, 'Balance Adjustment', final_adjustment))
    current_balance += final_adjustment

    # Sort transactions by day
    transactions.sort()

    return current_balance, transactions

def find_fridays(year, month):
    """Finds all Fridays in a given month."""
    fridays = []
    date = datetime(year, month, 1)
    while date.month == month:
        if date.weekday() == 4:  # 4 represents Friday
            fridays.append(date.day)
        date += timedelta(days=1)
    return fridays

def main():
    # User input for annual salary
    # annual_salary = float(input("Enter the annual salary: "))

    # User input for income variability range
    # income_min_percentage = float(input("Enter the minimum percentage variation for income (e.g., -30 for -30%): "))
    # income_max_percentage = float(input("Enter the maximum percentage variation for income (e.g., 30 for 30%): "))
    # income_range = (income_min_percentage, income_max_percentage)
    annual_salary = 15000
    income_min_percentage = -30
    income_max_percentage = 30
    income_range = (income_min_percentage, income_max_percentage)

    monthly_income = annual_salary / 12
    starting_balance = 500

    # Fixed expenses
    fixed_expenses = {
        'Rent Payment': {'percentage': 0.40, 'range': (-10, 10)},
        'Grocery Shopping': {'percentage': 0.16, 'range': (-15, 15)},
    }

    current_balance = starting_balance
    for year in range(2023, 2026):  # Example years: 2023-2025
        for month in range(1, 13):
            current_balance, monthly_transactions = simulate_monthly_transactions(
                year, month, current_balance, monthly_income, annual_salary, 
                income_range, fixed_expenses, all_variable_expenses
            )
            print(f"Year {year}, Month {month}:")
            for day, description, amount in monthly_transactions:
                print(f"  {day:02d} - {description}: {'+' if amount > 0 else ''}{amount:.2f}")
            print(f"  End of Month Balance: {current_balance:.2f}\n")


if __name__ == "__main__":
    main()
