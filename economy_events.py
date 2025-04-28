from sqlalchemy.orm import Session
from models import (
    Agent,
    EconomicEvent,
    LedgerEntry,
    AccountingRule,
)
import datetime


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
    region_id: int | None = None,  # Optional region/sector for the event itself
    sector_id: int | None = None,
    event_datetime: datetime.datetime | None = None,  # Allow specifying event time
) -> EconomicEvent:
    """
    Processes an economic event, creates the event record, finds the corresponding
    accounting rule, and generates the necessary ledger entries.
    """
    print(f"Processing event: {event_type_name} - {description}")

    # --- 1. Validate Agents ---
    agent1 = db.query(Agent).get(agent1_id)
    if not agent1:
        raise ValueError(f"Agent 1 with ID {agent1_id} not found.")
    if not agent1.ledger:
        raise ValueError(
            f"Agent 1 (ID: {agent1_id}, Name: {agent1.name}) does not have an associated ledger."
        )

    agent2 = None
    if agent2_id is not None:
        agent2 = db.query(Agent).get(agent2_id)
        if not agent2:
            raise ValueError(f"Agent 2 with ID {agent2_id} not found.")
        if not agent2.ledger:
            raise ValueError(
                f"Agent 2 (ID: {agent2_id}, Name: {agent2.name}) does not have an associated ledger."
            )

    # --- 2. Find Accounting Rule ---
    rule = (
        db.query(AccountingRule).filter(AccountingRule.name == event_type_name).first()
    )
    if not rule:
        raise ValueError(
            f"Accounting rule for event type '{event_type_name}' not found."
        )

    # --- 3. Create Economic Event Record ---
    if event_datetime is None:
        event_datetime = datetime.datetime.now(datetime.timezone.utc)

    # Determine region/sector for the event (default to agent1's if not provided)
    event_region_id = region_id if region_id is not None else agent1.region_id
    event_sector_id = sector_id if sector_id is not None else agent1.sector_id

    new_event = EconomicEvent(
        event_type_name=event_type_name,
        description=description,
        datetime=event_datetime,
        region_id=event_region_id,
        sector_id=event_sector_id,
        agent1_id=agent1_id,
        agent2_id=agent2_id,
        ccy=ccy,
        amount=amount,
        ccy2=ccy2,
        amount2=amount2,
    )
    db.add(new_event)
    db.flush()  # Get the ID for the new event

    # --- 4. Create Ledger Entries based on Rule ---
    # This assumes a simple one-to-one mapping from event to a double-entry.
    # More complex scenarios might need multiple entries or different logic.

    # Entry for Agent 1's Ledger
    # Determine if Agent 1 is the 'debit' or 'credit' side based on the rule's perspective
    # This requires defining the perspective of the rule (e.g., 'purchase' rule applies to the buyer)
    # For simplicity, let's assume the rule defines the entry for Agent 1 directly.
    # A more robust system might need flags on the rule or event type.

    # *** Simplified Assumption: The rule directly applies to Agent 1's books ***
    # If Agent 2 exists, a corresponding (often mirrored) entry might be needed in Agent 2's ledger.

    ledger_entry_agent1 = LedgerEntry(
        ledger_id=agent1.ledger.id,
        economic_event_id=new_event.id,
        datetime=new_event.datetime,
        dt_account_id=rule.dt_account_id,
        cr_account_id=rule.cr_account_id,
        dt_ccy=ccy,
        dt_amount=amount,
        cr_ccy=ccy,  # Assuming same currency for debit and credit side
        cr_amount=amount,
    )
    db.add(ledger_entry_agent1)
    print(
        f"  Created ledger entry {ledger_entry_agent1.id} for Agent {agent1_id} (Ledger {agent1.ledger.id})"
    )

    # --- 5. Create Mirrored Entry for Agent 2 (if applicable) ---
    # This is crucial for double-entry across the system.
    # The accounts used for Agent 2 will often be the inverse or related accounts.
    # Example: If Agent 1 buys (Debit Merch, Credit Creditor-to-Agent2),
    # Agent 2 sells (Debit Debtor-from-Agent1, Credit Sales).
    # This requires more sophisticated rule definition or logic.

    # *** Placeholder for Agent 2's entry - Requires more complex rule definition ***
    if agent2 and agent2.ledger:
        # TODO: Determine the correct accounts for Agent 2 based on the event type and rule.
        # This might involve looking up a 'counterparty' rule or having specific logic.
        # For now, we'll create a placeholder mirrored entry using the *same* accounts,
        # which is INCORRECT accounting but demonstrates the structure.
        # A real system needs to map rule.dt_account_id -> agent2_cr_account_id and
        # rule.cr_account_id -> agent2_dt_account_id based on the transaction type.

        print(
            f"  Placeholder: Creating mirrored entry for Agent {agent2_id} (Ledger {agent2.ledger.id}) - Needs correct account mapping!"
        )
        # ledger_entry_agent2 = LedgerEntry(
        #     ledger_id=agent2.ledger.id,
        #     economic_event_id=new_event.id,
        #     datetime=new_event.datetime,
        #     # --- !!! THIS IS LIKELY WRONG - NEEDS CORRECT MAPPING !!! ---
        #     dt_account_id=rule.cr_account_id, # Example: Mirroring accounts
        #     cr_account_id=rule.dt_account_id, # Example: Mirroring accounts
        #     # --- !!! ------------------------------------------ !!! ---
        #     dt_ccy=ccy,
        #     dt_amount=amount,
        #     cr_ccy=ccy,
        #     cr_amount=amount,
        # )
        # db.add(ledger_entry_agent2)
        pass  # Skip incorrect entry for now

    # --- 6. Commit (handled by the caller in app.py) ---
    # db.commit() is typically called in the API endpoint after this function returns

    print(f"Event {new_event.id} processed successfully.")
    return new_event
