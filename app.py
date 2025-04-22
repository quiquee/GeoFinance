from flask import Flask, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select

from models import (
    Base,
    Agent,
    AgentType,
    Ledger,
    LedgerAccount,
    LedgerEntry,
    LedgerEvent,
    LedgerLogic,
    AccountType,
)
from db_setup import DATABASE_URL, SessionLocal, seed_initial_data, create_db_structure
import economy_events

app = Flask(__name__)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.cli.command("init-db")
def init_db_command():
    """Creates the database tables and seeds initial data."""
    print("Initializing the database...")
    create_db_structure()
    seed_initial_data()
    print("Database initialized.")


# --- Ledger Logic API ---


@app.route("/ledger_logic", methods=["POST"])
def create_ledger_logic():
    """Creates a new ledger logic rule."""
    data = request.get_json()
    if not data or not all(
        k in data for k in ("name", "cr_account_id", "dt_account_id")
    ):
        return jsonify(
            {"error": "Missing required fields: name, cr_account_id, dt_account_id"}
        ), 400

    db = next(get_db())
    try:
        # Check if accounts exist
        cr_account = db.get(LedgerAccount, data["cr_account_id"])
        dt_account = db.get(LedgerAccount, data["dt_account_id"])
        if not cr_account or not dt_account:
            return jsonify({"error": "Invalid cr_account_id or dt_account_id"}), 404

        new_logic = LedgerLogic(
            name=data["name"],
            description=data.get("description"),
            cr_account_id=data["cr_account_id"],
            dt_account_id=data["dt_account_id"],
            ledger_event_id=data.get("ledger_event_id"),  # Optional link
            function=data.get("function"),  # Optional
        )
        db.add(new_logic)
        db.commit()
        db.refresh(new_logic)
        return jsonify(
            {"message": "Ledger logic created successfully", "id": new_logic.id}
        ), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": f"Failed to create ledger logic: {e}"}), 500
    finally:
        db.close()


@app.route("/ledger_logic/event/<event_name>", methods=["GET"])
def get_ledger_logic_by_event(event_name):
    """Gets ledger logic rules associated with a specific event name."""
    db = next(get_db())
    try:
        logics = db.query(LedgerLogic).filter(LedgerLogic.name == event_name).all()
        if not logics:
            return jsonify(
                {"message": f"No ledger logic found for event: {event_name}"}
            ), 404

        result = [
            {
                "id": logic.id,
                "name": logic.name,
                "description": logic.description,
                "cr_account_id": logic.cr_account_id,
                "dt_account_id": logic.dt_account_id,
                "ledger_event_id": logic.ledger_event_id,
                "function": logic.function,
            }
            for logic in logics
        ]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve ledger logic: {e}"}), 500
    finally:
        db.close()


# --- Economy Event API ---


@app.route("/event/<event_type>", methods=["POST"])
def trigger_event(event_type):
    """Triggers an economy event (e.g., payment, purchase, sale)."""
    data = request.get_json()
    required_fields = ["description", "agent_id", "ccy", "amount"]
    if not data or not all(k in data for k in required_fields):
        return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

    event_func = getattr(economy_events, event_type, None)
    if not event_func or not callable(event_func):
        return jsonify({"error": f"Invalid event type: {event_type}"}), 400

    db = next(get_db())
    try:
        # Check if agent exists
        agent = db.get(Agent, data["agent_id"])
        if not agent:
            return jsonify(
                {"error": f"Agent with id {data['agent_id']} not found"}
            ), 404

        # Check optional agent2
        agent2_id = data.get("agent2_id")
        if agent2_id:
            agent2 = db.get(Agent, agent2_id)
            if not agent2:
                return jsonify({"error": f"Agent2 with id {agent2_id} not found"}), 404

        # Call the appropriate function from economy_events
        result_event = event_func(
            db_session=db,  # Pass the session
            description=data["description"],
            agent_id=data["agent_id"],
            agent2_id=agent2_id,
            ccy=data["ccy"],
            ccy2=data.get("ccy2"),
            amount=data["amount"],
            amount2=data.get("amount2"),
        )

        if result_event:
            # Note: economy_events now handles commit/rollback per event
            return jsonify(
                {
                    "message": f"Event '{event_type}' processed successfully.",
                    "event_id": result_event.id,
                }
            ), 201
        else:
            # Error message should have been printed by economy_events
            return jsonify(
                {
                    "error": f"Failed to process event '{event_type}'. Check logs for details."
                }
            ), 500

    except Exception as e:
        # Catch any unexpected errors here, although economy_events should handle DB errors
        # db.rollback() # Rollback might have already happened in economy_events
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500
    # finally:
    # db session is closed by the context manager in economy_events or here if exception before call
    # db.close() # Already handled by get_db context manager


if __name__ == "__main__":
    # Note: Use 'flask run' to start the server after setting FLASK_APP=app.py
    # Use 'flask init-db' to setup the database first.
    print("To run the application:")
    print("1. Set FLASK_APP=app.py (export FLASK_APP=app.py or set FLASK_APP=app.py)")
    print("2. Run 'flask init-db' to create and seed the database.")
    print("3. Run 'flask run' to start the development server.")
    # app.run(debug=True) # Avoid running directly like this for production/standard dev
