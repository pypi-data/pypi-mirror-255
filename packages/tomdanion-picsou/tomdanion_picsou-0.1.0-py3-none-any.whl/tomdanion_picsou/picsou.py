account = 10000

def delete_money_from_bank_account(a:int, b:int) -> int:
    global account
    if a+b > 200:
        account = account - (a+b+100)
        return account
    account = account - (a + b)
    return account