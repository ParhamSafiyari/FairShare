# -*- coding: utf-8 -*-
"""
FairShare CLI (English / Persian)
----------------------------------
Log each expense separately - who paid, and who's splitting it - so a
purchase like cigarettes can be split only among the people who actually
want it, while dinner still splits across everyone.

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


def get_roster():
    """Collect the names of everyone splitting this outing. Returns a list of names."""
    roster = []
    print(t("roster_intro"))

    while True:
        name = input(t("roster_name_prompt")).strip()
        if name.lower() == "done":
            break
        if not name:
            print(t("empty_name"))
            continue
        if name in roster:
            print(t("duplicate_name_warning", name=name))
            continue
        roster.append(name)

    return roster


def print_roster(roster):
    for i, name in enumerate(roster, start=1):
        print(f"  {i}) {name}")


def pick_one_person(roster, prompt_key):
    """Ask the user to pick exactly one person from the roster by number."""
    while True:
        print_roster(roster)
        raw = input(t(prompt_key)).strip()
        try:
            index = int(raw) - 1
            if 0 <= index < len(roster):
                return roster[index]
        except ValueError:
            pass
        print(t("invalid_choice"))


def pick_many_people(roster, prompt_key):
    """Ask the user to pick one or more people from the roster, or 'all'."""
    while True:
        print_roster(roster)
        raw = input(t(prompt_key)).strip()
        if raw.lower() == "all":
            return list(roster)

        try:
            indices = [int(part.strip()) - 1 for part in raw.split(",") if part.strip()]
            chosen = []
            valid = True
            for index in indices:
                if 0 <= index < len(roster) and roster[index] not in chosen:
                    chosen.append(roster[index])
                else:
                    valid = False
                    break
            if valid and chosen:
                return chosen
        except ValueError:
            pass
        print(t("invalid_choice"))


def read_positive_amount():
    """Keep asking until the user enters a valid positive number."""
    while True:
        raw = input(t("amount_prompt")).strip()
        try:
            amount = float(raw)
            if amount <= 0:
                print(t("negative_amount"))
                continue
            return amount
        except ValueError:
            print(t("invalid_number"))


def get_expenses(roster):
    """
    Collect a list of expenses, each with a description, amount, who paid,
    and who's splitting it. Returns a list of dicts:
    {description, amount, paid_by, participants}
    """
    expenses = []
    print(t("expense_intro"))

    while True:
        description = input(t("expense_desc_prompt")).strip()
        if description.lower() == "done":
            break
        if not description:
            description = t("default_expense_label")

        amount = read_positive_amount()
        paid_by = pick_one_person(roster, "expense_paid_by_prompt")
        participants = pick_many_people(roster, "expense_participants_prompt")

        expenses.append({
            "description": description,
            "amount": amount,
            "paid_by": paid_by,
            "participants": participants,
        })
        print(t("expense_added", description=description, amount=amount))

    return expenses


def calculate_balances(roster, expenses):
    """
    Given the roster and a list of expenses, return a dict {name: balance}
    where a positive balance means that person is owed money, and negative
    means they owe money. Each expense is split only among its own
    participants, not the whole roster.
    """
    paid_totals = {name: 0.0 for name in roster}
    owed_totals = {name: 0.0 for name in roster}

    for expense in expenses:
        paid_totals[expense["paid_by"]] += expense["amount"]
        share = expense["amount"] / len(expense["participants"])
        for person in expense["participants"]:
            owed_totals[person] += share

    balances = {name: paid_totals[name] - owed_totals[name] for name in roster}
    return balances

def to_balanced_cents(balances):
    """
    Round each person's balance to cents, then correct the total so it sums
    to exactly zero. Rounding independently can leave the group's total
    slightly off (e.g. splitting $100 seven ways) - this nudges the leftover
    cent(s) onto whoever's rounding error was largest, so everyone can be
    fully settled with no stray pennies left unassigned to anyone.
    """
    raw = {name: amount * 100 for name, amount in balances.items()}
    rounded = {name: round(value) for name, value in raw.items()}
    total = sum(rounded.values())

    if total != 0:
        errors = sorted(
            raw.keys(),
            key=lambda name: (rounded[name] - raw[name]),
            reverse=(total > 0),
        )
        remaining = abs(total)
        i = 0
        while remaining > 0 and i < len(errors):
            rounded[errors[i]] += -1 if total > 0 else 1
            remaining -= 1
            i += 1

    return rounded

def settle_balances(balances):
    """
    Greedy settlement algorithm.
    Repeatedly match the biggest debtor with the biggest creditor
    until everyone is settled. Returns a list of (payer, receiver, amount).

    Works in integer cents rather than floating-point dollars, and the loop
    is capped at len(balances) iterations as a hard guarantee it can never hang.
    """
    cents = to_balanced_cents(balances)
    transactions = []

    for _ in range(len(cents)):
        debtor = min(cents, key=cents.get)
        creditor = max(cents, key=cents.get)

        if cents[debtor] >= 0 or cents[creditor] <= 0:
            break

        amount_cents = min(-cents[debtor], cents[creditor])
        if amount_cents <= 0:
            break

        transactions.append((debtor, creditor, amount_cents / 100))
        cents[debtor] += amount_cents
        cents[creditor] -= amount_cents

    return transactions


def print_report(roster, expenses, balances, transactions):
    total = sum(e["amount"] for e in expenses)

    print("\n" + "=" * 40)
    print(t("report_title"))
    print("=" * 40)

    print(f"\n{t('total_spent', total=total)}")
    print(t("num_people", count=len(roster)))

    print(f"\n{t('expenses_header')}")
    for e in expenses:
        participant_names = ", ".join(e["participants"])
        print(f"  {e['description']}: {e['amount']:.2f} ({t('paid_by_label', name=e['paid_by'])}, {t('split_between_label', names=participant_names)})")

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

    roster = get_roster()
    if len(roster) < 2:
        print(t("need_two_people"))
        return

    expenses = get_expenses(roster)
    if not expenses:
        print(t("need_one_expense"))
        return

    balances = calculate_balances(roster, expenses)
    transactions = settle_balances(balances)
    print_report(roster, expenses, balances, transactions)


if __name__ == "__main__":
    main()
