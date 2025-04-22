from flask import Flask, request, jsonify, abort
from models import (
    Base,
    engine,
    SessionLocal,
    Agent,
    Ledger,
    LedgerEntry,
)
import economy_events
import db_setup  # To potentially call setup functions if needed

app = Flask(__name__)


# Dependency injector for DB session
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.route("/")
def hello():
    return "Welcome to Ecosim!"


@app.route("/setup_database", methods=["POST"])
def setup_database():
    """
    Endpoint to initialize the database structure and seed data.
    Use with caution, as it drops existing tables.
    """
    try:
        print("Setting up database via API call...")
        db_setup.create_db_structure()
        db_setup.seed_initial_data()
        print("Database setup complete.")
        return jsonify({"message": "Database created and seeded successfully."}), 200
    except Exception as e:
        print(f"Error during database setup: {e}")
        return jsonify({"error": f"Database setup failed: {str(e)}"}), 500


@app.route("/event", methods=["POST"])
def create_event():
    """
    Endpoint to trigger an economic event.
    Expects JSON body with:
    - event_type: str (e.g., "buy", "pay")
    - description: str
    - agent1_id: int
    - agent2_id: int | None
    - ccy: str (e.g., "USD")
    - amount: float
    - ccy2: str | None (optional)
    - amount2: float | None (optional)
    """
    if not request.json:
        abort(400, description="Request body must be JSON.")

    data = request.json
    required_fields = ["event_type", "description", "agent1_id", "ccy", "amount"]
    if not all(field in data for field in required_fields):
        abort(400, description=f"Missing required fields: {required_fields}")

    event_type = data.get("event_type")
    description = data.get("description")
    agent1_id = data.get("agent1_id")
    agent2_id = data.get("agent2_id")  # Can be None
    ccy = data.get("ccy")
    amount = data.get("amount")
    ccy2 = data.get("ccy2")
    amount2 = data.get("amount2")

    # Validate data types (basic example)
    if (
        not isinstance(event_type, str)
        or not isinstance(description, str)
        or not isinstance(agent1_id, int)
        or (agent2_id is not None and not isinstance(agent2_id, int))
        or not isinstance(ccy, str)
        or not isinstance(amount, (int, float))
    ):
        abort(400, description="Invalid data types in request.")

    db_gen = get_db_session()
    db = next(db_gen)
    try:
        event = economy_events.process_economic_event(
            db=db,
            event_type_name=event_type,
            description=description,
            agent1_id=agent1_id,
            agent2_id=agent2_id,
            ccy=ccy,
            amount=float(amount),  # Ensure float
            ccy2=ccy2,
            amount2=float(amount2) if amount2 is not None else None,
        )
        return jsonify(
            {"message": "Event processed successfully", "event_id": event.id}
        ), 201
    except ValueError as ve:
        db.rollback()
        abort(400, description=str(ve))
    except Exception as e:
        db.rollback()
        print(f"Error processing event: {e}")  # Log the error server-side
        abort(500, description="An internal error occurred while processing the event.")
    finally:
        # Ensure db session is closed using the generator's finally block
        try:
            next(db_gen)  # This will trigger the finally block in get_db_session
        except StopIteration:
            pass  # Expected when generator finishes


# --- Add more endpoints as needed ---
# Example: Get agent details
@app.route("/agent/<int:agent_id>", methods=["GET"])
def get_agent(agent_id):
    db_gen = get_db_session()
    db = next(db_gen)
    try:
        agent = db.query(Agent).get(agent_id)
        if not agent:
            abort(404, description="Agent not found")
        # Ensure ledger relationship is loaded or handled if None
        ledger_id = agent.ledger.id if agent.ledger else None
        return jsonify(
            {
                "id": agent.id,
                "name": agent.name,
                "description": agent.description,
                "agent_type_id": agent.agent_type_id,
                "ledger_id": ledger_id,
            }
        )
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass


# Example: Get ledger entries for an agent
@app.route("/ledger/<int:ledger_id>/entries", methods=["GET"])
def get_ledger_entries(ledger_id):
    db_gen = get_db_session()
    db = next(db_gen)
    try:
        # Check if ledger exists first
        ledger = db.query(Ledger).filter_by(id=ledger_id).first()
        if not ledger:
            abort(404, description="Ledger not found")

        entries = (
            db.query(LedgerEntry)
            .filter(LedgerEntry.ledger_id == ledger_id)
            .order_by(LedgerEntry.datetime.desc())
            .all()
        )
        result = [
            {
                "id": entry.id,
                "datetime": entry.datetime.isoformat(),
                "event_id": entry.ledger_event_id,
                "dt_account_id": entry.dt_account_id,
                "cr_account_id": entry.cr_account_id,
                "dt_ccy": entry.dt_ccy,
                "dt_amount": entry.dt_amount,
                "cr_ccy": entry.cr_ccy,
                "cr_amount": entry.cr_amount,
            }
            for entry in entries
        ]
        return jsonify(result)
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass


if __name__ == "__main__":
    # Ensure the DB exists before running the app
    # You might want a more robust check or separate setup script execution
    try:
        # Check if tables exist, create if not. Avoids dropping data on every run.
        # This requires inspecting the engine, a simpler approach for dev is just create_all
        Base.metadata.create_all(bind=engine)  # Create tables if they don't exist
        print("Database tables checked/created.")
        # Optionally run seeding if DB was just created or specific tables are empty
        # db_setup.seed_initial_data() # Be careful with re-seeding
    except Exception as e:
        print(f"Error checking/creating database tables: {e}")

    app.run(debug=True)  # Runs on http://127.0.0.1:5000 by default
