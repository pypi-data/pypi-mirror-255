from dataclasses import dataclass
from datetime import datetime
import inspect

class DataclassMixin:
    @classmethod
    def from_dict(cls, *args, **kwars):      
        return cls(*args, **{
            k: v for k, v in kwars.items() 
            if k in inspect.signature(cls).parameters
        })



@dataclass
class BillingUser(DataclassMixin):
    unique_id: str
    credit_limit: float
    balance: float
    first_name: str
    last_name: str
    mobile_number: str
    work_number: str
    email: str
    company_name: str
    country: str
    city: str
    address: str
    zip_code: str
    description: str 


@dataclass
class Transfer(DataclassMixin):
    income: bool
    user: BillingUser

    def __post_init__(self):
        if self.user is not None:
            self.user = BillingUser.from_dict(**self.user)


@dataclass
class OutSystemService(DataclassMixin):
    unique_id: str
    prefix: str
    title: str
    description: str
    cost: float


@dataclass
class Transaction(DataclassMixin):
    id: int
    type: str
    status: str
    comment: str
    created_at: datetime
    amount: float
    fee: float
    balance_before: float
    balance_after: float
    transfer: Transfer
    out_system_service: OutSystemService

    def __post_init__(self):
        if self.transfer is not None:
            self.transfer = Transfer.from_dict(**self.transfer)
        if self.out_system_service is not None:
            self.out_system_service = OutSystemService.from_dict(**self.out_system_service)

        self.created_at = datetime.fromisoformat(self.created_at.rsplit('.', maxsplit=1)[0])


@dataclass
class SubscriptionPlan(DataclassMixin):
    unique_id: str
    out_system_service: OutSystemService
    first_payment_amount: float
    amount: float
    days_frequency: float
    type: str

    def __post_init__(self): 
        if self.out_system_service is not None:
            self.out_system_service = OutSystemService.from_dict(**self.out_system_service)


@dataclass
class Subscription(DataclassMixin):
    id: int
    plan: SubscriptionPlan
    count: int
    amount: float
    comment: str
    first_payment_at: datetime
    next_payment_at: datetime
    is_active: bool
    is_disabled: bool

    def __post_init__(self):
        self.plan = SubscriptionPlan.from_dict(**self.plan)
        self.first_payment_at = datetime.fromisoformat(self.first_payment_at.rsplit('.', maxsplit=1)[0])
        self.next_payment_at = datetime.fromisoformat(self.next_payment_at.rsplit('.', maxsplit=1)[0])