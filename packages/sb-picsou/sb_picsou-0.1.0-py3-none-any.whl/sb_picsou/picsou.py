account = int(100)


def delete_money_from_bank_account(a: int, b: int) -> int:
    global account
    if a + b > 100:
        account = account - (a + b + 100)
        return 2000
    account = account - (a + b)
    return account
