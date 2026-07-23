# -*- coding: utf-8 -*-
"""
FairShare CLI (English / Persian)
----------------------------------
Enter each person's name and how much they paid during a group outing.
The program calculates:
  - Total amount spent
  - Each person's fair share
  - Who owes money and who should be reimbursed
  - The minimum set of transactions needed to settle up

Translations are loaded from locales/en.json and locales/fa.json,
so adding a new language means adding a new JSON file - no code changes.
"""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOCALES_DIR = os.path.join(SCRIPT_DIR, "locales")

LANGUAGE = "en"
TEXTS = {}


def load_locale(lang):
    """Load a locale's JSON file into a dict of {key: string}."""
    path = os.path.join(LOCALES_DIR, f"{lang}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def t(key, **kwargs):
    """Look up a translated string by key and format it with the given kwargs."""
    template = TEXTS[key]
    return template.format(**kwargs)


def choose_language():
    """Ask the user to pick a language. Returns 'en' or 'fa'."""
    # We don't know the language yet, so this prompt is always bilingual
    # and lives directly in code rather than in a locale file.
    prompt = "Choose language / زبان را انتخاب کنید:\n  1) English\n  2) فارسی\n> "
    invalid_en = "Invalid choice. Please enter 1 or 2."
    invalid_fa = "انتخاب نامعتبر است. لطفاً 1 یا 2 را وارد کنید."

    while True:
        choice = input(prompt).strip()
        if choice == "1":
            return "en"
        elif choice == "2":
            return "fa"
        else:
            print(invalid_en)
            print(invalid_fa)


def get_expenses():
    """Collect names and amounts from the user. Returns a dict {name: amount_paid}."""
    expenses = {}
    print(t("intro"))

    while True:
        name = input(t("name_prompt")).strip()
        if name.lower() == "done":
            break
        if not name:
            print(t("empty_name"))
            continue
        if name in expenses:
            print(t("overwrite_warning", name=name))

        amount = read_amount()
        expenses[name] = amount

    return expenses


def read_amount():
    """Keep asking until the user enters a valid non-negative number."""
    while True:
        raw = input(t("amount_prompt")).strip()
        try:
            amount = float(raw)
            if amount < 0:
                print(t("negative_amount"))
                continue
            return amount
        except ValueError:
            print(t("invalid_number"))


def calculate_balances(expenses):
    """
    Given {name: amount_paid}, return:
      total        - sum of all payments
      fair_share   - total / number of people
      balances     - {name: amount_paid - fair_share}
                     positive = should receive money, negative = owes money
    """
    total = sum(expenses.values())
    num_people = len(expenses)
    fair_share = total / num_people

    balances = {name: paid - fair_share for name, paid in expenses.items()}
    return total, fair_share, balances


def settle_balances(balances):
    """
    Greedy settlement algorithm.
    Repeatedly match the biggest debtor with the biggest creditor
    until everyone is settled. Returns a list of (payer, receiver, amount).
    """
    balances = dict(balances)
    transactions = []

    balances = {name: round(amount, 2) for name, amount in balances.items()}

    while True:
        debtor = min(balances, key=balances.get)
        creditor = max(balances, key=balances.get)

        if abs(balances[debtor]) < 0.01 and abs(balances[creditor]) < 0.01:
            break

        amount = min(-balances[debtor], balances[creditor])
        amount = round(amount, 2)

        transactions.append((debtor, creditor, amount))

        balances[debtor] += amount
        balances[creditor] -= amount

    return transactions


def print_report(expenses, total, fair_share, balances, transactions):
    print("\n" + "=" * 40)
    print(t("report_title"))
    print("=" * 40)

    print(f"\n{t('total_spent', total=total)}")
    print(t("num_people", count=len(expenses)))
    print(t("fair_share", share=fair_share))

    print(f"\n{t('balances_header')}")
    for name, balance in balances.items():
        if balance > 0.01:
            print(t("is_owed", name=name, amount=balance))
        elif balance < -0.01:
            print(t("owes", name=name, amount=-balance))
        else:
            print(t("settled", name=name))

    print(f"\n{t('settlement_header')}")
    if not transactions:
        print(t("no_debts"))
    else:
        for payer, receiver, amount in transactions:
            print(t("pays", payer=payer, receiver=receiver, amount=amount))

    print("\n" + "=" * 40)


def main():
    global LANGUAGE, TEXTS
    LANGUAGE = choose_language()
    TEXTS = load_locale(LANGUAGE)

    expenses = get_expenses()

    if len(expenses) < 2:
        print(t("need_two_people"))
        return

    total, fair_share, balances = calculate_balances(expenses)
    transactions = settle_balances(balances)
    print_report(expenses, total, fair_share, balances, transactions)


if __name__ == "__main__":
    main()
