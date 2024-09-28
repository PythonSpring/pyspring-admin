import datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated, Optional
from typing_extensions import ReadOnly
from py_spring import PySpringModel
from sqlmodel import Field

from pydantic import EmailStr
from sqlmodel import Field, Relationship

import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Annotated
from pydantic import EmailStr
from sqlmodel import Field, Relationship

class AccountType(str, Enum):
    SAVINGS = "SAVINGS"
    CHECKING = "CHECKING"
    BUSINESS = "BUSINESS"

class BankAccount(PySpringModel, table=True):
    __tablename__: str = "bank_account"
    
    id: Optional[int] = Field(default=None, primary_key=True)  # INTEGER
    user_name: str  # VARCHAR
    email: EmailStr = Field(unique=True)  # EMAIL
    password: Annotated[str, ReadOnly] = Field(exclude=True)  # VARCHAR
    
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)  # TIMESTAMP
    birthday: Optional[datetime.date]  # DATE
    active: bool = Field(default=True)  # BOOLEAN
    balance: Decimal = Field(default=0.0)  # DECIMAL
    description: Optional[str] = Field(default=None)  # TEXT
    
    account_type: AccountType = Field(default=AccountType.SAVINGS)  # ENUM
    
    # Foreign Key to BankBranch
    branch_id: Optional[int] = Field(default=None, foreign_key="bank_branch.id")
    
    # Relationships
    branch: Optional["BankBranch"] = Relationship(back_populates="bank_accounts")
    transactions: list["Transaction"] = Relationship(back_populates="bank_account")

class Transaction(PySpringModel, table=True):
    __tablename__: str = "transaction"
    
    id: Optional[int] = Field(default=None, primary_key=True)  # INTEGER
    amount: Decimal = Field(default=0.0)  # DECIMAL
    transaction_date: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)  # TIMESTAMP
    description: Optional[str] = Field(default=None)  # TEXT
    
    # Foreign Key to BankAccount
    bank_account_id: Optional[int] = Field(default=None, foreign_key="bank_account.id")
    
    # Relationship back to BankAccount
    bank_account: Optional[BankAccount] = Relationship(back_populates="transactions")

class BankBranch(PySpringModel, table=True):
    __tablename__: str = "bank_branch"
    
    id: Optional[int] = Field(default=None, primary_key=True)  # INTEGER
    branch_name: str  # VARCHAR
    branch_code: str = Field(unique=True)  # VARCHAR
    location: str  # VARCHAR
    
    # One-to-Many Relationship: A branch can manage multiple accounts
    bank_accounts: list[BankAccount] = Relationship(back_populates="branch")
    
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)  # TIMESTAMP