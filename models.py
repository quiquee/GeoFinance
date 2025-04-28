from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Enum,
    Text,
    MetaData,
    Boolean,
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.sql import func

DATABASE_URL = "sqlite:///./ecosim.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
metadata = MetaData()  # Recommended for Alembic or manual checks

# --- Enums (Consider defining these more robustly if needed) ---
AccountTypeEnum = Enum(
    "balance_sheet", "profit_loss", "off_balance_sheet", name="account_type"
)
FrequencyEnum = Enum(
    "Once", "Daily", "Weekly", "Monthly", "Quarterly", "Annually", name="frequency"
)

# --- Model Definitions ---


# Add Currency model to track exchange rates
class Currency(Base):
    __tablename__ = "currencies"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(3), unique=True, index=True, nullable=False)  # e.g., USD, EUR
    name = Column(String, nullable=False)
    is_base = Column(Boolean, default=False)  # Whether this is the base currency

    # Track exchange rates where this is the source currency
    exchange_rates_source = relationship(
        "ExchangeRate",
        foreign_keys="[ExchangeRate.source_currency_id]",
        back_populates="source_currency",
    )
    exchange_rates_target = relationship(
        "ExchangeRate",
        foreign_keys="[ExchangeRate.target_currency_id]",
        back_populates="target_currency",
    )


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    id = Column(Integer, primary_key=True, index=True)
    source_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    target_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    rate = Column(Float, nullable=False)
    effective_date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    source_currency = relationship(
        "Currency",
        foreign_keys=[source_currency_id],
        back_populates="exchange_rates_source",
    )
    target_currency = relationship(
        "Currency",
        foreign_keys=[target_currency_id],
        back_populates="exchange_rates_target",
    )


class Region(Base):
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    parent_region_id = Column(
        Integer, ForeignKey("regions.id"), nullable=True
    )  # Self-referential FK

    parent_region = relationship(
        "Region", remote_side=[id], back_populates="sub_regions"
    )
    sub_regions = relationship("Region", back_populates="parent_region")
    agents = relationship("Agent", back_populates="region")
    economic_events = relationship("EconomicEvent", back_populates="region")


class Sector(Base):
    __tablename__ = "sectors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    parent_sector_id = Column(
        Integer, ForeignKey("sectors.id"), nullable=True
    )  # Self-referential FK

    parent_sector = relationship(
        "Sector", remote_side=[id], back_populates="sub_sectors"
    )
    sub_sectors = relationship("Sector", back_populates="parent_sector")
    agents = relationship("Agent", back_populates="sector")
    economic_events = relationship("EconomicEvent", back_populates="sector")


class AgentType(Base):
    __tablename__ = "agent_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    agents = relationship("Agent", back_populates="agent_type")


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    account_type = Column(AccountTypeEnum, nullable=False)
    nature = Column(
        Enum("Right", "Obligation", "Source", "Destination", name="account_nature"),
        nullable=True,
    )

    # Relationships for ledger entries where this account is debited or credited
    debit_entries = relationship(
        "LedgerEntry",
        foreign_keys="[LedgerEntry.dt_account_id]",
        back_populates="debit_account",
    )
    credit_entries = relationship(
        "LedgerEntry",
        foreign_keys="[LedgerEntry.cr_account_id]",
        back_populates="credit_account",
    )
    # Relationships for accounting rules
    debit_rules = relationship(
        "AccountingRule",
        foreign_keys="[AccountingRule.dt_account_id]",
        back_populates="debit_account_rule",
    )
    credit_rules = relationship(
        "AccountingRule",
        foreign_keys="[AccountingRule.cr_account_id]",
        back_populates="credit_account_rule",
    )


class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    agent_type_id = Column(Integer, ForeignKey("agent_types.id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=False)

    agent_type = relationship("AgentType", back_populates="agents")
    region = relationship("Region", back_populates="agents")
    sector = relationship("Sector", back_populates="agents")
    ledger = relationship("Ledger", back_populates="agent", uselist=False)  # One-to-one

    # Relationships for economic events where this agent is agent1 or agent2
    events_as_agent1 = relationship(
        "EconomicEvent",
        foreign_keys="[EconomicEvent.agent1_id]",
        back_populates="agent1",
    )
    events_as_agent2 = relationship(
        "EconomicEvent",
        foreign_keys="[EconomicEvent.agent2_id]",
        back_populates="agent2",
    )


class Ledger(Base):
    __tablename__ = "ledgers"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(
        Integer, ForeignKey("agents.id"), unique=True, nullable=False
    )  # One-to-one link

    agent = relationship("Agent", back_populates="ledger")
    entries = relationship("LedgerEntry", back_populates="ledger")


class EconomicEvent(Base):
    __tablename__ = "economic_events"
    id = Column(Integer, primary_key=True, index=True)
    event_type_name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    datetime = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=True)
    agent1_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    agent2_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    ccy = Column(String(3), nullable=False)
    amount = Column(Float, nullable=False)
    ccy2 = Column(String(3), nullable=True)
    amount2 = Column(Float, nullable=True)

    # Add fields from README that were previously commented out
    probability = Column(
        Float, nullable=True
    )  # Probability of event happening (0-100%)
    frequency = Column(FrequencyEnum, nullable=True)  # How often this event occurs
    time_decay_periods = Column(
        Integer, nullable=True
    )  # Number of periods for time decay

    # Relationships
    region = relationship("Region", back_populates="economic_events")
    sector = relationship("Sector", back_populates="economic_events")
    agent1 = relationship(
        "Agent", foreign_keys=[agent1_id], back_populates="events_as_agent1"
    )
    agent2 = relationship(
        "Agent", foreign_keys=[agent2_id], back_populates="events_as_agent2"
    )
    ledger_entries = relationship("LedgerEntry", back_populates="economic_event")

    # Link to template if this is an instance of an event template
    template_id = Column(
        Integer, ForeignKey("economic_event_templates.id"), nullable=True
    )
    template = relationship("EconomicEventTemplate", back_populates="event_instances")


# Add EconomicEventTemplate model to represent event templates
class EconomicEventTemplate(Base):
    __tablename__ = "economic_event_templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    probability = Column(Float, nullable=False, default=100.0)  # Default 100%
    frequency = Column(FrequencyEnum, nullable=False)
    time_decay_periods = Column(Integer, nullable=False, default=1)

    # Relationships
    event_instances = relationship("EconomicEvent", back_populates="template")
    accounting_rules = relationship("AccountingRule", back_populates="event_template")


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    id = Column(Integer, primary_key=True, index=True)
    ledger_id = Column(Integer, ForeignKey("ledgers.id"), nullable=False)
    economic_event_id = Column(
        Integer, ForeignKey("economic_events.id"), nullable=False
    )
    datetime = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Double Entry Fields
    dt_account_id = Column(
        Integer, ForeignKey("accounts.id"), nullable=False
    )  # Debit Account
    cr_account_id = Column(
        Integer, ForeignKey("accounts.id"), nullable=False
    )  # Credit Account
    dt_ccy = Column(String(3), nullable=False)
    dt_amount = Column(Float, nullable=False)
    cr_ccy = Column(String(3), nullable=False)
    cr_amount = Column(Float, nullable=False)

    # Additional fields to match README's Transaction formal structure
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    source_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    destination_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    currency = Column(String(3), nullable=False)
    economic_amount = Column(Float, nullable=False)
    is_mirror = Column(Boolean, default=False)  # Whether this is a mirror transaction

    # Relationships
    ledger = relationship("Ledger", back_populates="entries")
    economic_event = relationship("EconomicEvent", back_populates="ledger_entries")
    debit_account = relationship(
        "Account", foreign_keys=[dt_account_id], back_populates="debit_entries"
    )
    credit_account = relationship(
        "Account", foreign_keys=[cr_account_id], back_populates="credit_entries"
    )
    source_account = relationship("Account", foreign_keys=[source_account_id])
    destination_account = relationship("Account", foreign_keys=[destination_account_id])
    agent = relationship("Agent", foreign_keys=[agent_id])


class AccountingRule(Base):
    __tablename__ = "accounting_rules"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    # Link to event template
    event_template_id = Column(
        Integer, ForeignKey("economic_event_templates.id"), nullable=False
    )
    # Define which accounts are typically debited/credited for this type of event
    dt_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    cr_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    # Map to source/destination accounts in the README
    source_account_name = Column(String, nullable=False)  # e.g., "banks", "creditors"
    destination_account_name = Column(
        String, nullable=False
    )  # e.g., "suppliers", "merchandises"

    # Relationships
    event_template = relationship(
        "EconomicEventTemplate", back_populates="accounting_rules"
    )
    debit_account_rule = relationship(
        "Account", foreign_keys=[dt_account_id], back_populates="debit_rules"
    )
    credit_account_rule = relationship(
        "Account", foreign_keys=[cr_account_id], back_populates="credit_rules"
    )


# --- Helper function ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
