from py_spring import EntityProvider

from py_spring_admin.dev.repository.models import BankAccount, BankBranch, Transaction


def provide_test_tables() -> EntityProvider:
    provider = EntityProvider(
        model_classes=[
            BankAccount, BankBranch, Transaction
        ]
    )
    return provider