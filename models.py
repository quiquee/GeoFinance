import enum
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
)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy.sql import func
import datetime

Base = declarative_base()

DATABASE_URL = "sqlite:///ecosimv2.db"  # Changed filename
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class AccountTypeEnum(enum.Enum):  # Renamed to avoid conflict
    balance_sheet = "balance_sheet"
    profit_loss = "profit_loss"
    off_balance_sheet = "off_balance_sheet"
    fx_position = "fx_position"


class AgentType(Base):
    __tablename__ = "agent_type"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    agents = relationship("Agent", back_populates="agent_type")


class Agent(Base):
    __tablename__ = "agent"
    id = Column(Integer, primary_key=True, index=True)
    agent_type_id = Column(Integer, ForeignKey("agent_type.id"), nullable=False)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    agent_type = relationship("AgentType", back_populates="agents")
    ledger = relationship("Ledger", back_populates="agent", uselist=False)  # One-to-one
    events_as_agent1 = relationship(
        "LedgerEvent", back_populates="agent1", foreign_keys="LedgerEvent.agent1_id"
    )
    events_as_agent2 = relationship(
        "LedgerEvent", back_populates="agent2", foreign_keys="LedgerEvent.agent2_id"
    )


class Ledger(Base):
    __tablename__ = "ledger"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(
        Integer, ForeignKey("agent.id"), unique=True, nullable=False
    )  # Ensure one ledger per agent
    agent = relationship("Agent", back_populates="ledger")
    entries = relationship("LedgerEntry", back_populates="ledger")


class LedgerAccount(Base):
    __tablename__ = "ledger_account"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    type = Column(Enum(AccountTypeEnum), nullable=False)  # Use renamed Enum
    # Relationships for entries
    debit_entries = relationship(
        "LedgerEntry",
        back_populates="debit_account",
        foreign_keys="LedgerEntry.dt_account_id",
    )
    credit_entries = relationship(
        "LedgerEntry",
        back_populates="credit_account",
        foreign_keys="LedgerEntry.cr_account_id",
    )
    # Relationships for transaction types
    transaction_type_debits = relationship(
        "TransactionType",
        back_populates="debit_account",
        foreign_keys="TransactionType.dt_account_id",
    )
    transaction_type_credits = relationship(
        "TransactionType",
        back_populates="credit_account",
        foreign_keys="TransactionType.cr_account_id",
    )


class TransactionType(Base):
    # Renamed from LedgerLogic to match README
    __tablename__ = "transaction_type"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    dt_account_id = Column(Integer, ForeignKey("ledger_account.id"), nullable=False)
    cr_account_id = Column(Integer, ForeignKey("ledger_account.id"), nullable=False)
    function_name = Column(
        String, nullable=True
    )  # To link to economy_events.py functions as per README
    # Relationships to accounts
    debit_account = relationship(
        "LedgerAccount",
        back_populates="transaction_type_debits",
        foreign_keys=[dt_account_id],
    )
    credit_account = relationship(
        "LedgerAccount",
        back_populates="transaction_type_credits",
        foreign_keys=[cr_account_id],
    )
    events = relationship("LedgerEvent", back_populates="transaction_type")


class LedgerEvent(Base):
    __tablename__ = "ledger_event"
    id = Column(Integer, primary_key=True, index=True)
    transaction_type_id = Column(
        Integer, ForeignKey("transaction_type.id"), nullable=False
    )  # Changed from ledger_logic_id
    name = Column(String, index=True)  # Name of the event (e.g., 'purchase_groceries')
    datetime = Column(DateTime(timezone=True), server_default=func.now())
    description = Column(Text)
    agent1_id = Column(
        Integer, ForeignKey("agent.id"), nullable=False
    )  # Renamed from agent
    agent2_id = Column(
        Integer, ForeignKey("agent.id"), nullable=True
    )  # Renamed from agent2
    ccy = Column(String(3), nullable=False, default="USD")
    amount = Column(Float, nullable=False)
    ccy2 = Column(String(3), nullable=True)
    amount2 = Column(Float, nullable=True)

    transaction_type = relationship(
        "TransactionType", back_populates="events"
    )  # Changed from logic
    agent1 = relationship(
        "Agent", back_populates="events_as_agent1", foreign_keys=[agent1_id]
    )
    agent2 = relationship(
        "Agent", back_populates="events_as_agent2", foreign_keys=[agent2_id]
    )
    entries = relationship("LedgerEntry", back_populates="event")


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    id = Column(Integer, primary_key=True, index=True)
    datetime = Column(DateTime(timezone=True), server_default=func.now())
    ledger_id = Column(Integer, ForeignKey("ledger.id"), nullable=False)
    ledger_event_id = Column(Integer, ForeignKey("ledger_event.id"), nullable=False)
    # Reverted to dt_ccy/cr_ccy as per README
    dt_ccy = Column(String(3), nullable=False)
    dt_amount = Column(Float, nullable=False)
    cr_ccy = Column(String(3), nullable=False)
    cr_amount = Column(Float, nullable=False)
    dt_account_id = Column(Integer, ForeignKey("ledger_account.id"), nullable=False)
    cr_account_id = Column(Integer, ForeignKey("ledger_account.id"), nullable=False)

    ledger = relationship("Ledger", back_populates="entries")
    event = relationship("LedgerEvent", back_populates="entries")
    debit_account = relationship(
        "LedgerAccount", back_populates="debit_entries", foreign_keys=[dt_account_id]
    )
    credit_account = relationship(
        "LedgerAccount", back_populates="credit_entries", foreign_keys=[cr_account_id]
    )

    def __repr__(self):
        return f"<LedgerEntry(id={self.id}, dt_acc={self.dt_account_id}, cr_acc={self.cr_account_id}, dt_amt={self.dt_amount}, cr_amt={self.cr_amount})>"


# Utility function to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
