from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import (
    Base,
    AgentType,
    Agent,
    Ledger,
    LedgerAccount,
    AccountType,
    LedgerLogic,
)

DATABASE_URL = "sqlite:///ecosim.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_db_structure():
    """Creates the database tables based on the defined models.
    Deletes all existing tables first to ensure a clean structure."""
    print("Dropping existing tables (if any)...")
    Base.metadata.drop_all(bind=engine)  # Delete all tables defined in Base metadata
    print("Creating new database structure...")
    Base.metadata.create_all(bind=engine)  # Create tables
    print("Database structure created.")


def seed_initial_data():
    """Seeds the database with initial data as per README."""
    db = SessionLocal()
    try:
        # Basic agent_types
        if not db.query(AgentType).count():
            individual = AgentType(
                id=1, name="individual", description="a basic individual"
            )
            shop = AgentType(id=2, name="shop", description="a retailer")
            bank = AgentType(id=3, name="bank", description="a financial institution")
            public_entity = AgentType(
                id=4, name="public_entity", description="a government body"
            )
            producer = AgentType(
                id=5, name="producer", description="a producer of goods and services"
            )
            db.add_all([individual, shop, bank, public_entity, producer])
            db.commit()
            print("Added basic agent types.")
        else:
            individual = db.query(AgentType).filter_by(id=1).first()
            shop = db.query(AgentType).filter_by(id=2).first()
            bank = db.query(AgentType).filter_by(id=3).first()
            public_entity = db.query(AgentType).filter_by(id=4).first()
            producer = db.query(AgentType).filter_by(id=5).first()  # Fetch the new type

        # Basic agents and ledgers
        if not db.query(Agent).count():
            agent1 = Agent(
                id=1,
                name="enrique",
                agent_type_id=individual.id,
                description="a smart consumer",
            )
            agent2 = Agent(
                id=2,
                name="amazon",
                agent_type_id=shop.id,
                description="a big online retailer",
            )
            agent3 = Agent(
                id=3,
                name="hsbc",
                agent_type_id=bank.id,
                description="a global bank",
            )
            agent4 = Agent(
                id=4,
                name="agencia tributaria",
                agent_type_id=public_entity.id,
                description="the spanish tax agency",
            )
            agent5 = Agent(  # New agent
                id=5,
                name="chinese factory",
                agent_type_id=producer.id,
                description="a large scale producer",
            )
            db.add_all([agent1, agent2, agent3, agent4, agent5])  # Add agent5
            db.commit()  # Commit agents first to get their IDs

            ledger1 = Ledger(agent_id=agent1.id)
            ledger2 = Ledger(agent_id=agent2.id)
            ledger3 = Ledger(agent_id=agent3.id)
            ledger4 = Ledger(agent_id=agent4.id)
            ledger5 = Ledger(agent_id=agent5.id)  # New ledger
            db.add_all([ledger1, ledger2, ledger3, ledger4, ledger5])  # Add ledger5
            db.commit()
            print("Added basic agents and ledgers.")

        # Basic ledger accounts
        if not db.query(LedgerAccount).count():
            acc1 = LedgerAccount(
                id=1,
                name="merchandises",
                type=AccountType.balance_sheet,
            )
            acc2 = LedgerAccount(
                id=2,
                name="banks",
                type=AccountType.balance_sheet,
            )
            acc3 = LedgerAccount(
                id=3,
                name="creditors",
                type=AccountType.balance_sheet,
            )
            acc4 = LedgerAccount(
                id=4,
                name="debitors",
                type=AccountType.balance_sheet,
            )
            acc5 = LedgerAccount(
                id=5,
                name="sales",
                type=AccountType.profit_loss,
            )
            acc6 = LedgerAccount(
                id=6,
                name="expenses",
                type=AccountType.profit_loss,
            )
            db.add_all([acc1, acc2, acc3, acc4, acc5, acc6])
            db.commit()
            print("Added basic ledger accounts.")
        else:
            # Fetch accounts if they exist for logic seeding
            acc1 = db.query(LedgerAccount).filter_by(id=1).first()
            acc2 = db.query(LedgerAccount).filter_by(id=2).first()
            acc3 = db.query(LedgerAccount).filter_by(id=3).first()
            acc4 = db.query(LedgerAccount).filter_by(id=4).first()
            acc5 = db.query(LedgerAccount).filter_by(id=5).first()
            acc6 = db.query(LedgerAccount).filter_by(id=6).first()

        # Basic ledger_logic instances
        # Note: README links logic to accounts directly, not specific events yet.
        # Mapping based on common accounting principles for the names given.
        if not db.query(LedgerLogic).count():
            # Assuming 'purchase' increases merchandise (debit) and increases creditors (credit)
            # README says cr_account: merchandises, dt_account: creditors - this seems reversed for standard accounting.
            # Sticking to README for now, but this might need review.
            logic1 = LedgerLogic(
                id=1,
                name="purchase",
                description="Purchase event logic",
                cr_account_id=acc1.id,  # merchandises
                dt_account_id=acc3.id,  # creditors
            )

            # Assuming 'payment' decreases bank (credit) and decreases creditors (debit)
            # README says dt_account: banks, cr_account: suppliers (creditors) - seems reversed.
            # Using 'creditors' (id=3) as 'suppliers' isn't defined.
            logic2 = LedgerLogic(
                id=2,
                name="payment",
                description="Payment event logic",
                dt_account_id=acc2.id,  # banks
                cr_account_id=acc3.id,  # creditors
            )

            # Assuming 'sale' increases debtors (debit) and increases sales (credit)
            # README says dt_account: clients (debitors), cr_account: sales
            # Using 'debitors' (id=4) as 'clients' isn't defined.
            logic3 = LedgerLogic(
                id=3,
                name="sale",
                description="Sale event logic",
                dt_account_id=acc4.id,  # debitors
                cr_account_id=acc5.id,  # sales
            )

            # Assuming 'receipt' increases bank (debit) and decreases debtors (credit)
            logic4 = LedgerLogic(
                id=4,
                name="receipt",
                description="Receipt event logic",
                cr_account_id=acc2.id,  # banks
                dt_account_id=acc4.id,  # debitors
            )

            db.add_all([logic1, logic2, logic3, logic4])
            db.commit()
            print("Added basic ledger logic.")

        print("Initial data seeding complete (if tables were empty).")

    except Exception as e:
        print(f"An error occurred during seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating database structure...")
    create_db_structure()
    print("\nSeeding initial data...")
    seed_initial_data()
