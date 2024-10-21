from py_spring_core import EntityProvider


def provide_test_tables() -> EntityProvider:
    from py_spring_admin.dev.repository.models import BankAccount, BankBranch, Transaction
    provider = EntityProvider(
        extneral_dependencies=[BankAccount, BankBranch, Transaction]
    )
    return provider
