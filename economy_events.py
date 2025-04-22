import datetime
from sqlalchemy.orm import Session
from models import (
    LedgerEvent,
    LedgerEntry,
    TransactionType,
    Agent,
)

# Define mirror transaction relationships
MIRROR_TRANSACTIONS = {
    "buy": "sell",
    "sell": "buy",
    "borrow": "lend",
    "lend": "borrow",
    "pay": "receive",
    "receive": "pay",
    "interest_pay": "interest_receive",
    "interest_receive": "interest_pay",
    "unwanted_event": "wanted_event",
    "wanted_event": "unwanted_event",
}


def _create_ledger_entry(
    db: Session,
    ledger_id: int,
    event_id: int,
    transaction_type: TransactionType,
    amount: float,
    ccy: str,
    is_mirror: bool = False,
):
    """Helper function to create a single ledger entry."""
    # Swap debit/credit for mirror transactions based on the *mirror* transaction type's definition
    # The original logic incorrectly swapped based on the *original* transaction type
    dt_account_id = transaction_type.dt_account_id
    cr_account_id = transaction_type.cr_account_id

    entry = LedgerEntry(
        datetime=datetime.datetime.now(datetime.timezone.utc),
        ledger_id=ledger_id,
        ledger_event_id=event_id,
        dt_ccy=ccy,
        dt_amount=amount,
        cr_ccy=ccy,
        cr_amount=amount,
        dt_account_id=dt_account_id,
        cr_account_id=cr_account_id,
    )
    db.add(entry)


def process_economic_event(
    db: Session,
    event_type_name: str,
    description: str,
    agent1_id: int,
    agent2_id: int | None,
    ccy: str,
    amount: float,
    ccy2: str | None = None,
    amount2: float | None = None,
):
    """
    Processes an economic event, creates the LedgerEvent,
    and generates corresponding LedgerEntry records for involved agents.
    """
    # 1. Find the TransactionType for the primary event
    transaction_type = db.query(TransactionType).filter_by(name=event_type_name).first()
    if not transaction_type:
        raise ValueError(f"Transaction type '{event_type_name}' not found.")

    # 2. Create the LedgerEvent
    event = LedgerEvent(
        transaction_type_id=transaction_type.id,
        name=description,  # Using description as event name for now
        description=description,
        agent1_id=agent1_id,
        agent2_id=agent2_id,
        ccy=ccy,
        amount=amount,
        ccy2=ccy2,
        amount2=amount2,
    )
    db.add(event)
    db.flush()  # Flush to get the event ID

    # 3. Create LedgerEntry for Agent 1
    agent1 = db.query(Agent).get(agent1_id)
    if not agent1 or not agent1.ledger:
        db.rollback()  # Rollback event creation if agent/ledger missing
        raise ValueError(f"Agent 1 (ID: {agent1_id}) or their ledger not found.")

    _create_ledger_entry(
        db=db,
        ledger_id=agent1.ledger.id,
        event_id=event.id,
        transaction_type=transaction_type,  # Use primary transaction type for agent 1
        amount=amount,
        ccy=ccy,
        is_mirror=False,  # Not a mirror entry
    )

    # 4. Handle Mirror Transaction for Agent 2 (if applicable)
    mirror_event_name = MIRROR_TRANSACTIONS.get(event_type_name)
    if agent2_id and mirror_event_name:
        mirror_transaction_type = (
            db.query(TransactionType).filter_by(name=mirror_event_name).first()
        )
        if not mirror_transaction_type:
            # Don't rollback, just warn. The primary transaction is still valid.
            print(
                f"Warning: Mirror transaction type '{mirror_event_name}' not found for event '{event_type_name}'. Skipping mirror entry."
            )
        else:
            agent2 = db.query(Agent).get(agent2_id)
            if not agent2 or not agent2.ledger:
                # Don't rollback, just warn.
                print(
                    f"Warning: Agent 2 (ID: {agent2_id}) or their ledger not found. Skipping mirror entry."
                )
            else:
                # Determine amount/ccy for mirror entry (simple case: use primary amount/ccy)
                mirror_amount = amount
                mirror_ccy = ccy
                if amount2 is not None and ccy2 is not None:
                    # Potentially use amount2/ccy2 if relevant for the mirror side,
                    # requires more specific logic per transaction type if amounts differ.
                    # For now, we assume the primary amount applies to both sides.
                    pass

                _create_ledger_entry(
                    db=db,
                    ledger_id=agent2.ledger.id,
                    event_id=event.id,  # Link mirror entry to the same event
                    transaction_type=mirror_transaction_type,  # Use the MIRROR transaction type
                    amount=mirror_amount,
                    ccy=mirror_ccy,
                    is_mirror=True,  # Indicate this is a mirror entry (used by helper if needed, but logic now uses mirror_transaction_type)
                )

    db.commit()
    print(f"Processed event '{event_type_name}' (ID: {event.id}) successfully.")
    return event


# Example wrapper functions for specific events (optional, could be called from API)


def buy(
    db: Session,
    description: str,
    agent1_id: int,
    agent2_id: int,
    ccy: str,
    amount: float,
):
    return process_economic_event(
        db, "buy", description, agent1_id, agent2_id, ccy, amount
    )


def pay(
    db: Session,
    description: str,
    agent1_id: int,
    agent2_id: int,
    ccy: str,
    amount: float,
):
    return process_economic_event(
        db, "pay", description, agent1_id, agent2_id, ccy, amount
    )


def sell(
    db: Session,
    description: str,
    agent1_id: int,
    agent2_id: int,
    ccy: str,
    amount: float,
):
    return process_economic_event(
        db, "sell", description, agent1_id, agent2_id, ccy, amount
    )


def borrow(
    db: Session,
    description: str,
    agent1_id: int,
    agent2_id: int,
    ccy: str,
    amount: float,
):
    return process_economic_event(
        db, "borrow", description, agent1_id, agent2_id, ccy, amount
    )


def lend(
    db: Session,
    description: str,
    agent1_id: int,
    agent2_id: int,
    ccy: str,
    amount: float,
):
    return process_economic_event(
        db, "lend", description, agent1_id, agent2_id, ccy, amount
    )


def receive(
    db: Session,
    description: str,
    agent1_id: int,
    agent2_id: int,
    ccy: str,
    amount: float,
):
    return process_economic_event(
        db, "receive", description, agent1_id, agent2_id, ccy, amount
    )


def interest_pay(
    db: Session,
    description: str,
    agent1_id: int,
    agent2_id: int,
    ccy: str,
    amount: float,
):
    return process_economic_event(
        db, "interest_pay", description, agent1_id, agent2_id, ccy, amount
    )


def interest_receive(
    db: Session,
    description: str,
    agent1_id: int,
    agent2_id: int,
    ccy: str,
    amount: float,
):
    return process_economic_event(
        db, "interest_receive", description, agent1_id, agent2_id, ccy, amount
    )


def unwanted_event(
    db: Session,
    description: str,
    agent1_id: int,
    agent2_id: int | None,
    ccy: str,
    amount: float,
):
    # Agent 2 might not always apply here, depends on context
    return process_economic_event(
        db, "unwanted_event", description, agent1_id, agent2_id, ccy, amount
    )


def wanted_event(
    db: Session,
    description: str,
    agent1_id: int,
    agent2_id: int | None,
    ccy: str,
    amount: float,
):
    # Agent 2 might not always apply here, depends on context
    return process_economic_event(
        db, "wanted_event", description, agent1_id, agent2_id, ccy, amount
    )


# Add other event functions as needed following the pattern...
