from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class AccountType(enum.Enum):
    profit_loss = "profit_loss"
    balance_sheet = "balance_sheet"
    off_balance_sheet = "off_balance_sheet"
    fx_position = "fx_position"


class AgentType(Base):
    __tablename__ = "agent_type"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    agents = relationship("Agent", back_populates="agent_type")


class Agent(Base):
    __tablename__ = "agent"
    id = Column(Integer, primary_key=True)
    agent_type_id = Column(Integer, ForeignKey("agent_type.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    agent_type = relationship("AgentType", back_populates="agents")
    ledger = relationship("Ledger", back_populates="agent", uselist=False)  # One-to-one


class Ledger(Base):
    __tablename__ = "ledger"
    id = Column(Integer, primary_key=True)
    agent_id = Column(
        Integer, ForeignKey("agent.id"), nullable=False, unique=True
    )  # Ensure one ledger per agent
    agent = relationship("Agent", back_populates="ledger")
    entries = relationship("LedgerEntry", back_populates="ledger")


class LedgerAccount(Base):
    __tablename__ = "ledger_account"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(Enum(AccountType), nullable=False)  # Use Enum for type
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


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime(timezone=True), server_default=func.now())
    currency = Column(String(3), nullable=False)  # Assuming 3-letter currency codes
    ledger_id = Column(Integer, ForeignKey("ledger.id"), nullable=False)
    dt_ccy = Column(String(3), nullable=False)
    dt_amount = Column(Float, nullable=False)
    cr_ccy = Column(String(3), nullable=False)
    cr_amount = Column(Float, nullable=False)
    dt_account_id = Column(Integer, ForeignKey("ledger_account.id"), nullable=False)
    cr_account_id = Column(Integer, ForeignKey("ledger_account.id"), nullable=False)

    ledger = relationship("Ledger", back_populates="entries")
    debit_account = relationship(
        "LedgerAccount", foreign_keys=[dt_account_id], back_populates="debit_entries"
    )
    credit_account = relationship(
        "LedgerAccount", foreign_keys=[cr_account_id], back_populates="credit_entries"
    )
    # Consider adding relationship to LedgerEvent if needed


class LedgerEvent(Base):
    __tablename__ = "ledger_event"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # Name of the event function
    datetime = Column(DateTime(timezone=True), server_default=func.now())
    description = Column(String)
    agent_id = Column(Integer, ForeignKey("agent.id"))  # Primary agent involved
    agent2_id = Column(
        Integer, ForeignKey("agent.id"), nullable=True
    )  # Optional second agent
    ccy = Column(String(3))
    ccy2 = Column(String(3), nullable=True)
    amount = Column(Float)
    amount2 = Column(Float, nullable=True)

    agent = relationship("Agent", foreign_keys=[agent_id])
    agent2 = relationship("Agent", foreign_keys=[agent2_id])
    logic_rules = relationship("LedgerLogic", back_populates="ledger_event")


class LedgerLogic(Base):
    __tablename__ = "ledger_logic"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # Corresponds to event name
    ledger_event_id = Column(
        Integer, ForeignKey("ledger_event.id"), nullable=True
    )  # Link to specific event type if needed, or use name matching
    description = Column(String)
    cr_account_id = Column(Integer, ForeignKey("ledger_account.id"), nullable=False)
    dt_account_id = Column(Integer, ForeignKey("ledger_account.id"), nullable=False)
    function = Column(
        String, nullable=True
    )  # Optional: Store function logic/name if needed beyond simple mapping

    cr_account = relationship("LedgerAccount", foreign_keys=[cr_account_id])
    dt_account = relationship("LedgerAccount", foreign_keys=[dt_account_id])
    ledger_event = relationship(
        "LedgerEvent", back_populates="logic_rules"
    )  # Relationship back to LedgerEvent
