from models import (
    Base,
    AgentType,
    Agent,
    Ledger,
    LedgerAccount,
    AccountTypeEnum,
    TransactionType,  # Correct model name
    engine,
    SessionLocal,
)

DATABASE_URL = "sqlite:///ecosimv2.db"  # Changed filename


def create_db_structure():
    """Creates the database tables based on the defined models.
    Deletes all existing tables first to ensure a clean structure."""
    print("Dropping existing tables (if any)...")
    Base.metadata.drop_all(bind=engine)
    print("Creating new database structure...")
    Base.metadata.create_all(bind=engine)
    print("Database structure created.")


def seed_initial_data():
    """Seeds the database with initial data as per README."""
    db = SessionLocal()
    try:
        # Basic agent_types (IDs adjusted to match README)
        if not db.query(AgentType).count():
            individual = AgentType(
                id=1, name="individual", description="a basic individual"
            )
            shop = AgentType(id=2, name="shop", description="a retailer")
            bank = AgentType(id=3, name="bank", description="commercial bank")
            central_bank = AgentType(
                id=4, name="central_bank", description="a central bank"
            )
            producer = AgentType(
                id=5, name="producer", description="a producer of goods and services"
            )
            public = AgentType(id=6, name="public", description="a public entity")
            realisedrisk = AgentType(
                id=7, name="realisedrisk", description="sometimes things happen"
            )

            db.add_all(
                [individual, shop, bank, central_bank, producer, public, realisedrisk]
            )
            db.commit()
            print("Added basic agent types.")
        else:
            # Fetch existing types if needed for agent creation
            individual = db.query(AgentType).filter_by(id=1).first()
            shop = db.query(AgentType).filter_by(id=2).first()
            bank = db.query(AgentType).filter_by(id=3).first()
            producer = db.query(AgentType).filter_by(id=5).first()
            public = db.query(AgentType).filter_by(id=6).first()
            realisedrisk = db.query(AgentType).filter_by(id=7).first()

        # Basic agents and ledgers (IDs and names adjusted to match README)
        if not db.query(Agent).count():
            agent1 = Agent(
                id=1,
                name="Enrique",
                agent_type_id=individual.id,
                description="a smart consumer",
            )
            agent2 = Agent(
                id=2,
                name="Amazon",
                agent_type_id=shop.id,
                description="a big online retailer",
            )
            agent3 = Agent(
                id=3,
                name="AEAT",
                agent_type_id=public.id,
                description="agencia estatal de la administracion tributaria",
            )
            agent4 = Agent(
                id=4,
                name="ChinHuan",
                agent_type_id=producer.id,
                description="a chinese factory",
            )
            agent5 = Agent(
                id=5, name="HSBC", agent_type_id=bank.id, description="a global bank"
            )
            agent6 = Agent(
                id=6, name="TheAbyss", agent_type_id=realisedrisk.id, description=""
            )
            agent7 = Agent(
                id=7, name="Insurer", agent_type_id=realisedrisk.id, description=""
            )

            db.add_all([agent1, agent2, agent3, agent4, agent5, agent6, agent7])
            db.flush()  # Use flush instead of commit to keep transaction open

            # Create ledgers for each agent
            ledgers = [
                Ledger(agent_id=agent.id)
                for agent in [agent1, agent2, agent3, agent4, agent5, agent6, agent7]
            ]
            db.add_all(ledgers)
            db.commit()  # Commit agents and ledgers together
            print("Added basic agents and ledgers.")
        else:
            pass

        # Basic ledger accounts (IDs and names adjusted to match README)
        if not db.query(LedgerAccount).count():
            acc_merch = LedgerAccount(
                id=1, name="merchandises", type=AccountTypeEnum.balance_sheet
            )
            acc_banks = LedgerAccount(
                id=2, name="banks", type=AccountTypeEnum.balance_sheet
            )
            acc_creditors = LedgerAccount(
                id=3, name="creditors", type=AccountTypeEnum.balance_sheet
            )
            acc_debitors = LedgerAccount(
                id=4, name="debitors", type=AccountTypeEnum.balance_sheet
            )
            acc_sales = LedgerAccount(
                id=5, name="sales", type=AccountTypeEnum.profit_loss
            )
            acc_expenses = LedgerAccount(
                id=6, name="expenses", type=AccountTypeEnum.profit_loss
            )
            acc_income = LedgerAccount(
                id=7, name="income", type=AccountTypeEnum.profit_loss
            )
            acc_unwanted = LedgerAccount(
                id=8, name="unwanted", type=AccountTypeEnum.off_balance_sheet
            )

            db.add_all(
                [
                    acc_merch,
                    acc_banks,
                    acc_creditors,
                    acc_debitors,
                    acc_sales,
                    acc_expenses,
                    acc_income,
                    acc_unwanted,
                ]
            )
            db.commit()
            print("Added basic ledger accounts.")
        else:
            acc_merch = db.query(LedgerAccount).filter_by(name="merchandises").first()
            acc_banks = db.query(LedgerAccount).filter_by(name="banks").first()
            acc_creditors = db.query(LedgerAccount).filter_by(name="creditors").first()
            acc_debitors = db.query(LedgerAccount).filter_by(name="debitors").first()
            acc_sales = db.query(LedgerAccount).filter_by(name="sales").first()
            acc_expenses = db.query(LedgerAccount).filter_by(name="expenses").first()
            acc_income = db.query(LedgerAccount).filter_by(name="income").first()
            acc_unwanted = db.query(LedgerAccount).filter_by(name="unwanted").first()

        # Basic transaction_types (Using TransactionType model)
        if not db.query(TransactionType).count():
            if not all(
                [
                    acc_merch,
                    acc_banks,
                    acc_creditors,
                    acc_debitors,
                    acc_sales,
                    acc_expenses,
                    acc_income,
                    acc_unwanted,
                ]
            ):
                raise Exception(
                    "One or more required ledger accounts not found during seeding."
                )

            tt1 = TransactionType(
                id=1,
                name="buy",
                dt_account_id=acc_merch.id,
                cr_account_id=acc_creditors.id,
                function_name="buy",
            )
            tt2 = TransactionType(
                id=2,
                name="pay",
                dt_account_id=acc_creditors.id,
                cr_account_id=acc_banks.id,
                function_name="pay",
            )
            tt3 = TransactionType(
                id=3,
                name="sell",
                dt_account_id=acc_debitors.id,
                cr_account_id=acc_sales.id,
                function_name="sell",
            )
            tt4 = TransactionType(
                id=4,
                name="borrow",
                dt_account_id=acc_banks.id,
                cr_account_id=acc_creditors.id,
                function_name="borrow",
            )
            tt5 = TransactionType(
                id=5,
                name="lend",
                dt_account_id=acc_debitors.id,
                cr_account_id=acc_banks.id,
                function_name="lend",
            )
            tt6 = TransactionType(
                id=6,
                name="receive",
                dt_account_id=acc_banks.id,
                cr_account_id=acc_debitors.id,
                function_name="receive",
            )
            tt7 = TransactionType(
                id=7,
                name="interest_pay",
                dt_account_id=acc_expenses.id,
                cr_account_id=acc_banks.id,
                function_name="interest_pay",
            )
            tt8 = TransactionType(
                id=8,
                name="interest_receive",
                dt_account_id=acc_banks.id,
                cr_account_id=acc_income.id,
                function_name="interest_receive",
            )
            tt9 = TransactionType(
                id=9,
                name="unwanted_event",
                dt_account_id=acc_expenses.id,
                cr_account_id=acc_unwanted.id,
                function_name="unwanted_event",
            )
            tt10 = TransactionType(
                id=10,
                name="wanted_event",
                dt_account_id=acc_unwanted.id,
                cr_account_id=acc_income.id,
                function_name="wanted_event",
            )

            db.add_all([tt1, tt2, tt3, tt4, tt5, tt6, tt7, tt8, tt9, tt10])
            db.commit()
            print("Added basic transaction types.")

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
    print("\nSetup finished.")
