from models import LedgerEvent, LedgerEntry, LedgerLogic, Ledger
import datetime

# Define the mapping for mirror events
MIRROR_EVENT_MAP = {
    "purchase": "sale",
    "sale": "purchase",
    "payment": "receipt",  # Example: payment from agent1 is a receipt for agent2
    "receipt": "payment",  # Example: receipt for agent1 is a payment from agent2
    # Add other necessary mappings, ensure corresponding LedgerLogic exists
}


def create_ledger_entry(
    db_session, event_name, description, agent_id, agent2_id, ccy, ccy2, amount, amount2
):
    """Handles an economic event: records the event and creates ledger entries based on logic, including mirror entries for agent2."""

    # 1. Record the LedgerEvent (common to both agents)
    event_datetime = datetime.datetime.now(
        datetime.timezone.utc
    )  # Use a single timestamp
    new_event = LedgerEvent(
        name=event_name,
        description=description,
        agent_id=agent_id,
        agent2_id=agent2_id,
        ccy=ccy,
        ccy2=ccy2,
        amount=amount,
        amount2=amount2,
        datetime=event_datetime,
    )
    db_session.add(new_event)
    # Flush might be needed if LedgerEntry needs the event ID before commit
    # db_session.flush()
    print(
        f"Recorded LedgerEvent: {event_name} involving agent {agent_id}"
        + (f" and agent {agent2_id}" if agent2_id else "")
    )

    entries_to_add = []  # Collect entries to add together

    # --- Process entry for agent_id ---
    logic = db_session.query(LedgerLogic).filter_by(name=event_name).first()
    if not logic:
        print(
            f"Error: No LedgerLogic found for event name '{event_name}'. Rolling back."
        )
        db_session.rollback()  # Rollback event creation
        return None

    agent_ledger = db_session.query(Ledger).filter_by(agent_id=agent_id).first()
    if not agent_ledger:
        print(f"Error: No Ledger found for agent ID '{agent_id}'. Rolling back.")
        db_session.rollback()  # Rollback event creation
        return None

    # Determine amounts and currencies for agent1's entry
    # Assuming primary amount/ccy for now. Refine if needed.
    dt_amount_agent1 = amount
    cr_amount_agent1 = amount
    dt_ccy_agent1 = ccy
    cr_ccy_agent1 = ccy

    ledger_entry_agent1 = LedgerEntry(
        datetime=event_datetime,
        currency=dt_ccy_agent1,  # Base currency for the entry
        ledger_id=agent_ledger.id,
        dt_ccy=dt_ccy_agent1,
        dt_amount=dt_amount_agent1,
        cr_ccy=cr_ccy_agent1,
        cr_amount=cr_amount_agent1,
        dt_account_id=logic.dt_account_id,
        cr_account_id=logic.cr_account_id,
        # ledger_event_id=new_event.id # Optional: link entry to event after flush
    )
    entries_to_add.append(ledger_entry_agent1)
    print(
        f"Prepared LedgerEntry for agent {agent_id}: DtAcc={logic.dt_account_id}, CrAcc={logic.cr_account_id}, Amount={dt_amount_agent1} {dt_ccy_agent1}"
    )

    # --- Process mirror entry for agent2_id if applicable ---
    if agent2_id:
        mirror_event_name = MIRROR_EVENT_MAP.get(event_name)
        if not mirror_event_name:
            # If no mirror is defined, we only create the first entry.
            # Commit handled later.
            print(
                f"Warning: No mirror event mapping found for '{event_name}'. Only creating entry for agent {agent_id}."
            )
        else:
            print(
                f"Processing mirror event '{mirror_event_name}' for agent {agent2_id}"
            )

            mirror_logic = (
                db_session.query(LedgerLogic).filter_by(name=mirror_event_name).first()
            )
            if not mirror_logic:
                print(
                    f"Error: No LedgerLogic found for mirror event name '{mirror_event_name}'. Rolling back."
                )
                db_session.rollback()  # Rollback event and agent1 entry prep
                return None

            agent2_ledger = (
                db_session.query(Ledger).filter_by(agent_id=agent2_id).first()
            )
            if not agent2_ledger:
                print(
                    f"Error: No Ledger found for agent ID '{agent2_id}'. Rolling back."
                )
                db_session.rollback()  # Rollback event and agent1 entry prep
                return None

            # Determine amounts and currencies for agent2's entry
            # ASSUMPTION: Using primary amount/ccy for mirror entry as well.
            # Adjust this logic if amount2/ccy2 or different amounts are needed for the mirror.
            dt_amount_agent2 = amount
            cr_amount_agent2 = amount
            dt_ccy_agent2 = ccy
            cr_ccy_agent2 = ccy

            ledger_entry_agent2 = LedgerEntry(
                datetime=event_datetime,
                currency=dt_ccy_agent2,  # Base currency for the entry
                ledger_id=agent2_ledger.id,
                dt_ccy=dt_ccy_agent2,
                dt_amount=dt_amount_agent2,
                cr_ccy=cr_ccy_agent2,
                cr_amount=cr_amount_agent2,
                dt_account_id=mirror_logic.dt_account_id,
                cr_account_id=mirror_logic.cr_account_id,
                # ledger_event_id=new_event.id # Optional: link entry to event after flush
            )
            entries_to_add.append(ledger_entry_agent2)
            print(
                f"Prepared LedgerEntry for agent {agent2_id}: DtAcc={mirror_logic.dt_account_id}, CrAcc={mirror_logic.cr_account_id}, Amount={dt_amount_agent2} {dt_ccy_agent2}"
            )

    # Add all prepared entries and commit transactionally
    if entries_to_add:
        db_session.add_all(entries_to_add)
        try:
            db_session.commit()
            print(
                f"Successfully processed event '{event_name}' and committed {len(entries_to_add)} entries."
            )
            return new_event  # Return the created event
        except Exception as e:
            db_session.rollback()
            print(f"Error committing changes for event '{event_name}': {e}")
            return None
    else:
        # This case should not be reached if agent1 processing was successful
        # but added for safety. Rollback the event if no entries generated.
        print(
            f"Error: No ledger entries were prepared for event '{event_name}'. Rolling back event creation."
        )
        db_session.rollback()
        return None


# Define specific event functions as wrappers around the core logic


def payment(db_session, description, agent_id, agent2_id, ccy, ccy2, amount, amount2):
    return create_ledger_entry(
        db_session,
        "payment",
        description,
        agent_id,
        agent2_id,
        ccy,
        ccy2,
        amount,
        amount2,
    )


def purchase(db_session, description, agent_id, agent2_id, ccy, ccy2, amount, amount2):
    return create_ledger_entry(
        db_session,
        "purchase",
        description,
        agent_id,
        agent2_id,
        ccy,
        ccy2,
        amount,
        amount2,
    )


def sale(db_session, description, agent_id, agent2_id, ccy, ccy2, amount, amount2):
    return create_ledger_entry(
        db_session, "sale", description, agent_id, agent2_id, ccy, ccy2, amount, amount2
    )


# Example usage moved to test_events.py
