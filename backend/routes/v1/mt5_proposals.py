from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.subscription import require_premium_plan
from models.broker_account import BrokerAccount
from models.mt5_trade_proposal import MT5TradeProposal
from models.strategy_profile import StrategyProfile
from models.user import User
from schemas.mt5_trade_proposal import MT5TradeProposalResponse
from services.brokers.approval_rules import (
    daily_trade_limit_reached,
    proposal_rule_violation,
)


router = APIRouter(
    prefix="/mt5/proposals",
    tags=["MT5 Trade Proposals"],
)


def _get_owned_proposal(
    proposal_id: int,
    current_user: User,
    db: Session,
) -> MT5TradeProposal:
    proposal = (
        db.query(MT5TradeProposal)
        .filter(
            MT5TradeProposal.id == proposal_id,
            MT5TradeProposal.user_id == current_user.id,
        )
        .first()
    )

    if proposal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade proposal not found.",
        )

    return proposal


def _expire_if_needed(
    proposal: MT5TradeProposal,
    db: Session,
) -> bool:
    if (
        proposal.status == "pending"
        and proposal.expires_at <= datetime.utcnow()
    ):
        proposal.status = "expired"
        db.commit()
        db.refresh(proposal)
        return True

    return False


def _validate_approval_safety(
    proposal: MT5TradeProposal,
    current_user: User,
    db: Session,
) -> None:
    if proposal.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending trade proposals can be approved.",
        )

    if proposal.expires_at <= datetime.utcnow():
        proposal.status = "expired"
        db.commit()
        db.refresh(proposal)

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This trade proposal has expired.",
        )

    account = (
        db.query(BrokerAccount)
        .filter(
            BrokerAccount.id == proposal.broker_account_id,
            BrokerAccount.user_id == current_user.id,
        )
        .first()
    )

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The MT5 account for this proposal is no longer available.",
        )

    if not account.connected:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The MT5 account is not currently marked as connected.",
        )

    if not account.autotrader_enabled:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="AutoTrader monitoring is no longer enabled for this MT5 account.",
        )

    if account.strategy_profile_id != proposal.strategy_profile_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The Strategy Brain strategy linked to this account has changed.",
        )

    strategy = (
        db.query(StrategyProfile)
        .filter(
            StrategyProfile.id == proposal.strategy_profile_id,
            StrategyProfile.user_id == current_user.id,
        )
        .first()
    )

    if strategy is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The Strategy Brain strategy for this proposal is no longer available.",
        )

    if strategy.is_archived:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The Strategy Brain strategy has been archived.",
        )

    if not strategy.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The Strategy Brain strategy is no longer active.",
        )

    if not strategy.requires_user_approval:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="TradePilot requires explicit trader approval for every AutoTrader trade.",
        )

    normalized_markets = {
        str(market).strip().lower()
        for market in (strategy.markets or [])
    }

    if "forex" not in normalized_markets:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="AutoTrader proposals are restricted to Forex strategies.",
        )

    if proposal.max_hold_minutes not in (30, 60):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The proposal has an invalid maximum holding duration.",
        )

    if proposal.max_hold_minutes != account.max_hold_minutes:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The AutoTrader maximum holding duration has changed since this proposal was created.",
        )

    if proposal.stop_loss is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A stop loss is required.",
        )

    if proposal.take_profit is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A take profit is required.",
        )

    violation = proposal_rule_violation(
        proposal.direction,
        proposal.entry_price,
        proposal.stop_loss,
        proposal.take_profit,
        proposal.risk_percent,
        strategy.max_risk_percent,
    )

    if violation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=violation,
        )

    if strategy.max_trades_per_day is not None:
        day_start = datetime.utcnow().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        approved_today = (
            db.query(MT5TradeProposal)
            .filter(
                MT5TradeProposal.user_id == current_user.id,
                MT5TradeProposal.broker_account_id
                == proposal.broker_account_id,
                MT5TradeProposal.id != proposal.id,
                MT5TradeProposal.status.in_(
                    ["approved", "executed"]
                ),
                MT5TradeProposal.approved_at >= day_start,
            )
            .count()
        )

        if daily_trade_limit_reached(
            approved_today,
            strategy.max_trades_per_day,
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The strategy's daily trade limit has been reached.",
            )

@router.get(
    "",
    response_model=list[MT5TradeProposalResponse],
)
def list_trade_proposals(
    proposal_status: Optional[str] = Query(
        default=None,
        alias="status",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_premium_plan),
):
    query = (
        db.query(MT5TradeProposal)
        .filter(
            MT5TradeProposal.user_id == current_user.id
        )
    )

    if proposal_status is not None:
        allowed_statuses = {
            "pending",
            "approved",
            "rejected",
            "expired",
            "executed",
            "failed",
        }

        normalized_status = proposal_status.strip().lower()

        if normalized_status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid proposal status.",
            )

        query = query.filter(
            MT5TradeProposal.status == normalized_status
        )

    proposals = (
        query.order_by(
            MT5TradeProposal.created_at.desc()
        )
        .all()
    )

    changed = False
    now = datetime.utcnow()

    for proposal in proposals:
        if (
            proposal.status == "pending"
            and proposal.expires_at <= now
        ):
            proposal.status = "expired"
            changed = True

    if changed:
        db.commit()

        for proposal in proposals:
            db.refresh(proposal)

    if proposal_status is not None:
        if proposal_status.strip().lower() == "pending":
            proposals = [
                proposal
                for proposal in proposals
                if proposal.status == "pending"
            ]

    return proposals


@router.get(
    "/{proposal_id}",
    response_model=MT5TradeProposalResponse,
)
def get_trade_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_premium_plan),
):
    proposal = _get_owned_proposal(
        proposal_id,
        current_user,
        db,
    )

    _expire_if_needed(
        proposal,
        db,
    )

    return proposal


@router.post(
    "/{proposal_id}/approve",
    response_model=MT5TradeProposalResponse,
)
def approve_trade_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_premium_plan),
):
    proposal = _get_owned_proposal(
        proposal_id,
        current_user,
        db,
    )

    _validate_approval_safety(
        proposal,
        current_user,
        db,
    )

    updated = (
        db.query(MT5TradeProposal)
        .filter(
            MT5TradeProposal.id == proposal.id,
            MT5TradeProposal.status == "pending",
        )
        .update(
            {
                "status": "approved",
                "approved_at": datetime.utcnow(),
            },
            synchronize_session=False,
        )
    )

    if updated != 1:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This trade proposal was already handled.",
        )

    db.commit()
    db.refresh(proposal)

    # Approval is recorded only.
    # No MT5 order is submitted here.
    return proposal


@router.post(
    "/{proposal_id}/reject",
    response_model=MT5TradeProposalResponse,
)
def reject_trade_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_premium_plan),
):
    proposal = _get_owned_proposal(
        proposal_id,
        current_user,
        db,
    )

    if proposal.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending trade proposals can be rejected.",
        )

    if proposal.expires_at <= datetime.utcnow():
        proposal.status = "expired"

        db.commit()
        db.refresh(proposal)

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This trade proposal has expired.",
        )

    proposal.status = "rejected"
    proposal.rejected_at = datetime.utcnow()

    db.commit()
    db.refresh(proposal)

    return proposal
