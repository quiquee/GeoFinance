import os
from sqlalchemy.orm import Session
from models import (
    Base,
    engine,
    AgentType,
    Agent,
    Region,
    Sector,
    Account,
    Ledger,
    EconomicEventTemplate,
    AccountingRule,
    Currency,
    ExchangeRate,
)


def create_tables():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")


def drop_tables():
    """Drop all tables from the database."""
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped.")


def reset_database():
    """Reset the database by dropping and recreating all tables."""
    drop_tables()
    create_tables()
    print("Database reset complete.")


def populate_initial_data(db: Session):
    """Populate the database with initial records."""
    # Create currencies
    currencies = [
        Currency(code="USD", name="US Dollar", is_base=True),
        Currency(code="EUR", name="Euro"),
        Currency(code="GBP", name="British Pound"),
        Currency(code="CNY", name="Chinese Yuan"),
    ]
    db.add_all(currencies)
    db.commit()
    print("Currencies created.")

    # Create exchange rates
    exchange_rates = []
    for curr in db.query(Currency).filter(Currency.code != "USD").all():
        # Example rates
        rate = 1.0
        if curr.code == "EUR":
            rate = 0.85
        elif curr.code == "GBP":
            rate = 0.75
        elif curr.code == "CNY":
            rate = 6.4

        exchange_rates.append(
            ExchangeRate(
                source_currency_id=db.query(Currency)
                .filter(Currency.code == "USD")
                .first()
                .id,
                target_currency_id=curr.id,
                rate=rate,
            )
        )

    db.add_all(exchange_rates)
    db.commit()
    print("Exchange rates created.")

    # Create regions
    world = Region(name="World", description="Global region")
    db.add(world)
    db.commit()

    spain = Region(name="Spain", description="Spain region", parent_region_id=world.id)
    china = Region(name="China", description="China region", parent_region_id=world.id)
    db.add_all([spain, china])
    db.commit()
    print("Regions created.")

    # Create sectors
    economy = Sector(name="Economy", description="Main economic sector")
    db.add(economy)
    db.commit()

    individuals = Sector(
        name="Individuals",
        description="Individual consumers",
        parent_sector_id=economy.id,
    )
    retail = Sector(
        name="Online Retail",
        description="Online retail sector",
        parent_sector_id=economy.id,
    )
    public = Sector(
        name="Public", description="Public sector", parent_sector_id=economy.id
    )
    electronics = Sector(
        name="Electronics",
        description="Electronics industry",
        parent_sector_id=economy.id,
    )
    financial = Sector(
        name="Financial", description="Financial sector", parent_sector_id=economy.id
    )

    db.add_all([individuals, retail, public, electronics, financial])
    db.commit()
    print("Sectors created.")

    # Create agent types
    agent_types_data = [
        {"name": "individual", "description": "a basic individual"},
        {"name": "shop", "description": "a retailer"},
        {"name": "bank", "description": "commercial bank"},
        {"name": "central_bank", "description": "a central bank"},
        {"name": "producer", "description": "a producer of goods and services"},
        {"name": "public", "description": "a public entity"},
        {"name": "realisedrisk", "description": "sometimes things happen"},
    ]

    agent_types = []
    for data in agent_types_data:
        agent_types.append(AgentType(**data))

    db.add_all(agent_types)
    db.commit()
    print("Agent types created.")

    # Create basic agents
    agents_data = [
        {
            "name": "Enrique",
            "agent_type_id": db.query(AgentType)
            .filter(AgentType.name == "individual")
            .first()
            .id,
            "description": "a smart consumer",
            "region_id": spain.id,
            "sector_id": individuals.id,
        },
        {
            "name": "Amazon",
            "agent_type_id": db.query(AgentType)
            .filter(AgentType.name == "shop")
            .first()
            .id,
            "description": "a big online retailer",
            "region_id": spain.id,
            "sector_id": retail.id,
        },
        {
            "name": "AEAT",
            "agent_type_id": db.query(AgentType)
            .filter(AgentType.name == "public")
            .first()
            .id,
            "description": "agencia estatal de la administracion tributaria",
            "region_id": spain.id,
            "sector_id": public.id,
        },
        {
            "name": "ChinHuan",
            "agent_type_id": db.query(AgentType)
            .filter(AgentType.name == "producer")
            .first()
            .id,
            "description": "a chinese factory",
            "region_id": china.id,
            "sector_id": electronics.id,
        },
        {
            "name": "HSBC",
            "agent_type_id": db.query(AgentType)
            .filter(AgentType.name == "bank")
            .first()
            .id,
            "description": "a global bank",
            "region_id": spain.id,
            "sector_id": financial.id,
        },
        {
            "name": "TheAbyss",
            "agent_type_id": db.query(AgentType)
            .filter(AgentType.name == "realisedrisk")
            .first()
            .id,
            "description": "the chaos agent",
            "region_id": world.id,
            "sector_id": economy.id,
        },
        {
            "name": "Insurer",
            "agent_type_id": db.query(AgentType)
            .filter(AgentType.name == "realisedrisk")
            .first()
            .id,
            "description": "insurance provider",
            "region_id": world.id,
            "sector_id": economy.id,
        },
    ]

    agents = []
    for data in agents_data:
        agent = Agent(**data)
        agents.append(agent)
        db.add(agent)
        db.commit()
        # Create a ledger for each agent
        ledger = Ledger(agent_id=agent.id)
        db.add(ledger)

    db.commit()
    print("Agents and their ledgers created.")

    # Create basic ledger accounts
    account_data = [
        {"name": "merchandises", "account_type": "balance_sheet", "nature": "Right"},
        {"name": "banks", "account_type": "balance_sheet", "nature": "Right"},
        {"name": "creditors", "account_type": "balance_sheet", "nature": "Obligation"},
        {"name": "debitors", "account_type": "balance_sheet", "nature": "Right"},
        {"name": "sales", "account_type": "profit_loss", "nature": "Source"},
        {"name": "expenses", "account_type": "profit_loss", "nature": "Destination"},
        {"name": "income", "account_type": "profit_loss", "nature": "Source"},
        {"name": "suppliers", "account_type": "balance_sheet", "nature": "Obligation"},
        {"name": "clients", "account_type": "balance_sheet", "nature": "Right"},
    ]

    accounts = []
    for data in account_data:
        accounts.append(Account(**data))

    db.add_all(accounts)
    db.commit()
    print("Basic ledger accounts created.")

    # Create basic economic event templates
    event_templates_data = [
        {
            "name": "purchase",
            "frequency": "Once",
            "time_decay_periods": 1,
            "probability": 100.0,
        },
        {
            "name": "pay",
            "frequency": "Once",
            "time_decay_periods": 1,
            "probability": 100.0,
        },
        {
            "name": "sale",
            "frequency": "Once",
            "time_decay_periods": 1,
            "probability": 100.0,
        },
        {
            "name": "borrow",
            "frequency": "Once",
            "time_decay_periods": 1,
            "probability": 100.0,
        },
        {
            "name": "lend",
            "frequency": "Once",
            "time_decay_periods": 1,
            "probability": 100.0,
        },
        {
            "name": "receipt",
            "frequency": "Once",
            "time_decay_periods": 1,
            "probability": 100.0,
        },
        {
            "name": "interest_pay",
            "frequency": "Once",
            "time_decay_periods": 1,
            "probability": 100.0,
        },
        {
            "name": "interest_receive",
            "frequency": "Once",
            "time_decay_periods": 1,
            "probability": 100.0,
        },
    ]

    event_templates = []
    for data in event_templates_data:
        event_templates.append(EconomicEventTemplate(**data))

    db.add_all(event_templates)
    db.commit()
    print("Economic event templates created.")

    # Create basic accounting rules
    accounting_rules_data = [
        {
            "name": "purchase_rule",
            "event_template_id": db.query(EconomicEventTemplate)
            .filter(EconomicEventTemplate.name == "purchase")
            .first()
            .id,
            "dt_account_id": db.query(Account)
            .filter(Account.name == "merchandises")
            .first()
            .id,
            "cr_account_id": db.query(Account)
            .filter(Account.name == "creditors")
            .first()
            .id,
            "source_account_name": "creditors",
            "destination_account_name": "merchandises",
        },
        {
            "name": "pay_rule",
            "event_template_id": db.query(EconomicEventTemplate)
            .filter(EconomicEventTemplate.name == "pay")
            .first()
            .id,
            "dt_account_id": db.query(Account)
            .filter(Account.name == "suppliers")
            .first()
            .id,
            "cr_account_id": db.query(Account)
            .filter(Account.name == "banks")
            .first()
            .id,
            "source_account_name": "banks",
            "destination_account_name": "suppliers",
        },
        {
            "name": "sale_rule",
            "event_template_id": db.query(EconomicEventTemplate)
            .filter(EconomicEventTemplate.name == "sale")
            .first()
            .id,
            "dt_account_id": db.query(Account)
            .filter(Account.name == "clients")
            .first()
            .id,
            "cr_account_id": db.query(Account)
            .filter(Account.name == "sales")
            .first()
            .id,
            "source_account_name": "sales",
            "destination_account_name": "clients",
        },
        {
            "name": "borrow_rule",
            "event_template_id": db.query(EconomicEventTemplate)
            .filter(EconomicEventTemplate.name == "borrow")
            .first()
            .id,
            "dt_account_id": db.query(Account)
            .filter(Account.name == "banks")
            .first()
            .id,
            "cr_account_id": db.query(Account)
            .filter(Account.name == "creditors")
            .first()
            .id,
            "source_account_name": "creditors",
            "destination_account_name": "banks",
        },
        {
            "name": "lend_rule",
            "event_template_id": db.query(EconomicEventTemplate)
            .filter(EconomicEventTemplate.name == "lend")
            .first()
            .id,
            "dt_account_id": db.query(Account)
            .filter(Account.name == "debitors")
            .first()
            .id,
            "cr_account_id": db.query(Account)
            .filter(Account.name == "banks")
            .first()
            .id,
            "source_account_name": "banks",
            "destination_account_name": "debitors",
        },
        {
            "name": "receipt_rule",
            "event_template_id": db.query(EconomicEventTemplate)
            .filter(EconomicEventTemplate.name == "receipt")
            .first()
            .id,
            "dt_account_id": db.query(Account)
            .filter(Account.name == "banks")
            .first()
            .id,
            "cr_account_id": db.query(Account)
            .filter(Account.name == "debitors")
            .first()
            .id,
            "source_account_name": "debitors",
            "destination_account_name": "banks",
        },
        {
            "name": "interest_pay_rule",
            "event_template_id": db.query(EconomicEventTemplate)
            .filter(EconomicEventTemplate.name == "interest_pay")
            .first()
            .id,
            "dt_account_id": db.query(Account)
            .filter(Account.name == "expenses")
            .first()
            .id,
            "cr_account_id": db.query(Account)
            .filter(Account.name == "banks")
            .first()
            .id,
            "source_account_name": "banks",
            "destination_account_name": "expenses",
        },
        {
            "name": "interest_receive_rule",
            "event_template_id": db.query(EconomicEventTemplate)
            .filter(EconomicEventTemplate.name == "interest_receive")
            .first()
            .id,
            "dt_account_id": db.query(Account)
            .filter(Account.name == "banks")
            .first()
            .id,
            "cr_account_id": db.query(Account)
            .filter(Account.name == "income")
            .first()
            .id,
            "source_account_name": "income",
            "destination_account_name": "banks",
        },
    ]

    accounting_rules = []
    for data in accounting_rules_data:
        accounting_rules.append(AccountingRule(**data))

    db.add_all(accounting_rules)
    db.commit()
    print("Accounting rules created.")

    print("Initial data population complete.")


def setup_database():
    """Set up the database by creating tables and populating initial data."""
    from models import SessionLocal

    create_tables()

    db = SessionLocal()
    try:
        populate_initial_data(db)
    finally:
        db.close()


if __name__ == "__main__":
    setup_database()
