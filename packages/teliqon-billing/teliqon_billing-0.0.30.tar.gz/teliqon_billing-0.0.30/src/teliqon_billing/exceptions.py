class LowBalanceException(Exception):
    status_code = 402
    error_message = "low balance"
    error_code = "0001"


class CouponAlreadyUsedException(Exception):
    status_code = 498
    error_message = "coupon already used"
    error_code = "0002"


class IncorrectValueException(Exception):
    status_code = 400
    error_message = "incorrect value"
    error_code = "0003"


class SameUserException(Exception):
    status_code = 400
    error_message = "same user for transfer"
    error_code = "0004"


class BillingUserNotFoundException(Exception):
    status_code = 404
    error_message = "billing user not found"
    error_code = "0005"


class EnvironmentNotFoundException(Exception):
    status_code = 404
    error_message = "environment not found"
    error_code = "0006"


class CouponNotFoundException(Exception):
    status_code = 404
    error_message = "coupon not found"
    error_code = "0007"


class OutSystemServiceNotFoundException(Exception):
    status_code = 404
    error_message = "out system service not found"
    error_code = "0008"


class TransactionNotFoundException(Exception):
    status_code = 404
    error_message = "transaction not found"
    error_code = "0009"


class SubscriptionPlanNotFoundException(Exception):
    status_code = 404
    error_message = "subscription plan not found"
    error_code = "0010"


class BillingUserSubscriptionNotFoundException(Exception):
    status_code = 409
    error_message = "billing user subscription not found"
    error_code = "0011"


class BillingUserSubscriptionAlreadyExistsException(Exception):
    status_code = 409
    error_message = "billing user subscription already exists"
    error_code = "0012"


class TransactionCannotBeRevertedException(Exception):
    status_code = 400
    error_message = "transaction cannot be reverted because it is unsuccessful"
    error_code = "0013"


class TransactionCannotBeProcessedException(Exception):
    status_code = 400
    error_message = "transaction cannot be processed because it isnot pending"
    error_code = "0014"


class BillingUserAlreadyExistsException(Exception):
    status_code = 409
    error_message = "billing user already exists"
    error_code = "0015"


class SubscriptionPlanTypeNotFoundException(Exception):
    status_code = 404
    error_message = "subscription plan type not found"
    error_code = "0016"


class OutSystemServiceAlreadyExistsException(Exception):
    status_code = 409
    error_message = "out system service already exists"
    error_code = "0017"


class SubscriptionPlanAlreadyExistsException(Exception):
    status_code = 409
    error_message = "subscription plan already exists"
    error_code = "0018"
    

exceptions_register = {
    "0001": LowBalanceException,
    "0002": CouponAlreadyUsedException,
    "0003": IncorrectValueException,
    "0004": SameUserException,
    "0005": BillingUserNotFoundException,
    "0006": EnvironmentNotFoundException,
    "0007": CouponNotFoundException,
    "0008": OutSystemServiceNotFoundException,
    "0009": TransactionNotFoundException,
    "0010": SubscriptionPlanNotFoundException,
    "0011": BillingUserSubscriptionNotFoundException,
    "0012": BillingUserSubscriptionAlreadyExistsException,
    "0013": TransactionCannotBeRevertedException,
    "0014": TransactionCannotBeProcessedException,
    "0015": BillingUserAlreadyExistsException,
    "0016": SubscriptionPlanTypeNotFoundException,
    "0017": OutSystemServiceAlreadyExistsException,
    "0018": SubscriptionPlanAlreadyExistsException,
}