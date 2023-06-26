"""Module containing debt classes (mortgage and personal lines)."""

import numpy_financial as npf
import math
import pandas as pd
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Union


class Debt(ABC):
    """Abstract class representing debt objects.
    
    Parameters
    ==========
    principal: int | float
        The principal outstanding at inception of debt.

    interest_rate: float
        Annual interest rate on debt.
    """
    def __init__(self, principal: Union[int, float], interest_rate: float) -> None:
        self.principal = principal
        self.interest_rate = interest_rate

    @abstractmethod
    def calculate_payment(self) -> None:
        """Abstract method to calculate required payment."""
        raise NotImplementedError
    
    @abstractmethod
    def calculate_current_balance(self) -> None:
        """Abstract method to calculate current balance outstanding."""
        raise NotImplementedError
    

class PersonalDebt(Debt):
    """Class representing non-mortgage debt"""
    def __init__(self, principal: Union[int, float], interest_rate: float) -> None:
        super().__init__(principal, interest_rate)

    def calculate_payment(self) -> None:
        pass

    def calculate_current_balance(self) -> None:
        pass


class Mortgage(Debt):
    """Class representing mortgages.
    
    Parameters
    ==========
    principal: int | float
        The principal outstanding at inception of debt.

    interest_rate: float
        Annual interest rate on debt.

    term: int
        Term, in years, of current mortgage contract.

    amortization: int
        Amortization period, in years, of mortgage.

    start_date: Union[datetime, str]
        Calendar start date of mortgage contract.

    prepayment_per_period: Optional, int | float, default=0
        Amount of prepayment each period, in dollars.

    product: str, default = "fixed"
        Type of mortage (fixed or variable)

    payments_per_year: int, default = 12
        Number of mortgage payments in a calendar year.

    Attributes
    ==========
    period_rate: float
        Interest rate per period.

    num_periods: int
        Total number of payments during life of mortgage.

    current_period: int
        Current period of mortgage (for example: the 12th mortgage payment)

    current_balance: float
        Current outstanding balance of the mortgage.

    payment: float
        Required payment, per period, in dollars.
    """
    def __init__(
            self,
            *,
            principal: Union[int, float],
            interest_rate: float,
            term: int,
            amortization: int,
            start_date: Union[datetime, str], 
            prepayment_per_period: Union[float, int] = 0,
            product: str = "fixed",
            payments_per_year: int = 12,
        ) -> None:
        super().__init__(principal, interest_rate)
        self.term = term
        self.amortization = amortization
        self.start_date = start_date
        self.prepayment_per_period = prepayment_per_period
        self.product = product
        self.payments_per_year = payments_per_year
        self.period_rate = interest_rate / payments_per_year
        self.num_periods = amortization * payments_per_year
        self.current_period = 1
        self.current_balance = principal
        self.payment = -npf.pmt(
            interest_rate / payments_per_year,
            amortization * payments_per_year,
            principal,
        )
        self.amortization_table: pd.DataFrame = None
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.term_end_date = start_date + relativedelta(years=term)


    # TODO: create properties

    def calculate_payment(self) -> None:
        self.payment = -npf.pmt(self.period_rate, self.num_periods, self.current_balance)

    def _calculate_interest_portion(
        self,
        current_period: int,
        current_balance: Union[float, int],
    ) -> float:
        """Calculate the portfion of payment that goes towards interest."""
        return -npf.ipmt(
            self.period_rate,
            current_period,
            self.num_periods,
            current_balance,
        )

    def _calculate_principal_portion(
        self,
        current_period: int,
        current_balance: Union[float, int],
    ) -> float:
        """Calculate the portion of payment that goes towards the principal."""
        return -npf.ppmt(
            self.period_rate,
            current_period,
            self.num_periods,
            current_balance,
        )

    def calculate_current_balance(self, principal_payment: Union[float, int]) -> None:
        """Calculate the current oustanding balance after a payment."""
        # TODO: is this method necessary?
        self.current_balance -= principal_payment

    def _calculate_num_periods_between_dates(self,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
    ) -> int:
        """Calculate number of payment periods between two dates."""
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        return math.floor((end_date - start_date).months / 12)

    def create_amortization_table(self) -> None:
        """Create an amortization table using object attributes at init."""
        payment_dates = [self.start_date + relativedelta(months=i) for i in range(self.num_periods)]
        payment_num = [i+1 for i in range(self.num_periods)]
        payments = [self.payment] * self.num_periods
        balance = [self.principal] * self.num_periods
        interest_portion = [0] * self.num_periods
        principal_portion = [0] * self.num_periods
        for i in range(self.num_periods):
            interest_portion[i] = self._calculate_interest_portion(i+1, balance[i])
            principal_portion[i] = self._calculate_principal_portion(i+1, balance[i])
            if i > 0:
                balance[i] = balance[i-1] - principal_portion[i]
            else:
                balance[i] = self.principal - principal_portion[i]
        self.amortization_table = pd.DataFrame(
            data = {
                "payment_dates": payment_dates,
                "payment_num": payment_num,
                "payment": payments,
                "balance": balance,
                "interest_portion": interest_portion,
                "principal_portion": principal_portion,
            }
        )

    def make_lumpsum_payment(
        self,
        payment: Union[float, int],
        date: Union[str, datetime],
    ) -> None:
        # TODO - needs to update the balance at the appropriate period, then recalculate amort table
        pass

    def _recalculate_amortization_table(self) -> None:
        # TODO
        pass

    def renew_mortgage(
        self,
        *,
        term: int,
        interest_rate: float,
        type: str,
        amortization_period: int,
        start_date: Union[str, datetime],
    ) -> None:
        # TODO
        pass
