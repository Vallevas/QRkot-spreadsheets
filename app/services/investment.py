from datetime import datetime
from typing import Union

from app.models.charity_project import CharityProject
from app.models.donation import Donation

InvestableModel = Union[CharityProject, Donation]


def close_charity_obj(charity_obj: InvestableModel) -> None:
    """Close object (consider it fully invested)."""
    charity_obj.invested_amount = charity_obj.full_amount
    charity_obj.fully_invested = True
    charity_obj.close_date = datetime.now()


def invest(
    target: InvestableModel,
    sources: list[InvestableModel],
) -> InvestableModel:
    """
    Distribute available funds from 'sources' to the 'target' charity project.

    Goes through the 'sources' (sorted from oldest), moving the available
    funds into 'target' until either the 'sources' run out of funds or the
    'target' is fully invested. Closes both the 'sources' that are spent and
    the 'target' when it's fully funded.

    Does NOT commit - the caller has to commit the entire transaction.
    """
    for source in sources:
        needed = target.full_amount - target.invested_amount
        if needed <= 0:
            break
        available = source.full_amount - source.invested_amount
        transferred = min(available, needed)

        source.invested_amount += transferred
        target.invested_amount += transferred

        if source.invested_amount >= source.full_amount:
            close_charity_obj(source)
        if target.invested_amount >= target.full_amount:
            close_charity_obj(target)
            break
    return target
