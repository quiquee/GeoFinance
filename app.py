from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
from pydantic import BaseModel, Field

from models import (
    get_db,
    Region,
    Sector,
    AgentType,
    Agent,
    Ledger,
    Account,
    AccountingRule,
    EconomicEvent,
    EconomicEventTemplate,
    LedgerEntry,
    Currency,
    ExchangeRate,
)

app = FastAPI(
    title="EcoSim API",
    description="API for the Economy Simulator",
    version="0.1.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic models for request/response ---


# Region models
class RegionBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_region_id: Optional[int] = None


class RegionCreate(RegionBase):
    pass


class RegionResponse(RegionBase):
    id: int

    class Config:
        orm_mode = True


# Sector models
class SectorBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_sector_id: Optional[int] = None


class SectorCreate(SectorBase):
    pass


class SectorResponse(SectorBase):
    id: int

    class Config:
        orm_mode = True


# AgentType models
class AgentTypeBase(BaseModel):
    name: str
    description: Optional[str] = None


class AgentTypeCreate(AgentTypeBase):
    pass


class AgentTypeResponse(AgentTypeBase):
    id: int

    class Config:
        orm_mode = True


# Agent models
class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    agent_type_id: int
    region_id: int
    sector_id: int


class AgentCreate(AgentBase):
    pass


class AgentResponse(AgentBase):
    id: int

    class Config:
        orm_mode = True


# Account models
class AccountBase(BaseModel):
    name: str
    description: Optional[str] = None
    account_type: str
    nature: Optional[str] = None


class AccountCreate(AccountBase):
    pass


class AccountResponse(AccountBase):
    id: int

    class Config:
        orm_mode = True


# Currency models
class CurrencyBase(BaseModel):
    code: str
    name: str
    is_base: bool = False


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyResponse(CurrencyBase):
    id: int

    class Config:
        orm_mode = True


# ExchangeRate models
class ExchangeRateBase(BaseModel):
    source_currency_id: int
    target_currency_id: int
    rate: float
    effective_date: Optional[datetime.datetime] = None


class ExchangeRateCreate(ExchangeRateBase):
    pass


class ExchangeRateResponse(ExchangeRateBase):
    id: int

    class Config:
        orm_mode = True


# EconomicEventTemplate models
class EconomicEventTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    probability: float = 100.0
    frequency: str
    time_decay_periods: int = 1


class EconomicEventTemplateCreate(EconomicEventTemplateBase):
    pass


class EconomicEventTemplateResponse(EconomicEventTemplateBase):
    id: int

    class Config:
        orm_mode = True


# AccountingRule models
class AccountingRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    event_template_id: int
    dt_account_id: int
    cr_account_id: int
    source_account_name: str
    destination_account_name: str


class AccountingRuleCreate(AccountingRuleBase):
    pass


class AccountingRuleResponse(AccountingRuleBase):
    id: int

    class Config:
        orm_mode = True


# EconomicEvent models
class EconomicEventBase(BaseModel):
    event_type_name: str
    description: str
    region_id: Optional[int] = None
    sector_id: Optional[int] = None
    agent1_id: int
    agent2_id: Optional[int] = None
    ccy: str
    amount: float
    ccy2: Optional[str] = None
    amount2: Optional[float] = None
    probability: Optional[float] = None
    frequency: Optional[str] = None
    time_decay_periods: Optional[int] = None
    template_id: Optional[int] = None


class EconomicEventCreate(EconomicEventBase):
    pass


class EconomicEventResponse(EconomicEventBase):
    id: int
    datetime: datetime.datetime

    class Config:
        orm_mode = True


# LedgerEntry models
class LedgerEntryBase(BaseModel):
    ledger_id: int
    economic_event_id: int
    dt_account_id: int
    cr_account_id: int
    dt_ccy: str
    dt_amount: float
    cr_ccy: str
    cr_amount: float
    agent_id: int
    source_account_id: int
    destination_account_id: int
    currency: str
    economic_amount: float
    is_mirror: bool = False


class LedgerEntryCreate(LedgerEntryBase):
    pass


class LedgerEntryResponse(LedgerEntryBase):
    id: int
    datetime: datetime.datetime

    class Config:
        orm_mode = True


# Simulation request model
class SimulationRequest(BaseModel):
    start_date: datetime.datetime
    end_date: datetime.datetime
    region_id: Optional[int] = None
    sector_id: Optional[int] = None


# Wealth calculation request
class WealthCalculationRequest(BaseModel):
    agent_id: int
    date: Optional[datetime.datetime] = None


# Wealth response
class WealthResponse(BaseModel):
    agent_id: int
    agent_name: str
    total_wealth: float
    currency: str
    as_of_date: datetime.datetime
    account_balances: dict


# --- API Routes ---


# Health check
@app.get("/")
def read_root():
    return {"status": "ok", "message": "EcoSim API is running"}


# --- CRUD operations for Regions ---
@app.post("/regions/", response_model=RegionResponse)
def create_region(region: RegionCreate, db: Session = Depends(get_db)):
    db_region = Region(**region.dict())
    db.add(db_region)
    db.commit()
    db.refresh(db_region)
    return db_region


@app.get("/regions/", response_model=List[RegionResponse])
def read_regions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    regions = db.query(Region).offset(skip).limit(limit).all()
    return regions


@app.get("/regions/{region_id}", response_model=RegionResponse)
def read_region(region_id: int, db: Session = Depends(get_db)):
    region = db.query(Region).filter(Region.id == region_id).first()
    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return region


@app.put("/regions/{region_id}", response_model=RegionResponse)
def update_region(region_id: int, region: RegionCreate, db: Session = Depends(get_db)):
    db_region = db.query(Region).filter(Region.id == region_id).first()
    if db_region is None:
        raise HTTPException(status_code=404, detail="Region not found")

    for key, value in region.dict().items():
        setattr(db_region, key, value)

    db.commit()
    db.refresh(db_region)
    return db_region


@app.delete("/regions/{region_id}")
def delete_region(region_id: int, db: Session = Depends(get_db)):
    db_region = db.query(Region).filter(Region.id == region_id).first()
    if db_region is None:
        raise HTTPException(status_code=404, detail="Region not found")

    db.delete(db_region)
    db.commit()
    return {"message": "Region deleted successfully"}


# --- CRUD operations for Sectors ---
@app.post("/sectors/", response_model=SectorResponse)
def create_sector(sector: SectorCreate, db: Session = Depends(get_db)):
    db_sector = Sector(**sector.dict())
    db.add(db_sector)
    db.commit()
    db.refresh(db_sector)
    return db_sector


@app.get("/sectors/", response_model=List[SectorResponse])
def read_sectors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sectors = db.query(Sector).offset(skip).limit(limit).all()
    return sectors


@app.get("/sectors/{sector_id}", response_model=SectorResponse)
def read_sector(sector_id: int, db: Session = Depends(get_db)):
    sector = db.query(Sector).filter(Sector.id == sector_id).first()
    if sector is None:
        raise HTTPException(status_code=404, detail="Sector not found")
    return sector


@app.put("/sectors/{sector_id}", response_model=SectorResponse)
def update_sector(sector_id: int, sector: SectorCreate, db: Session = Depends(get_db)):
    db_sector = db.query(Sector).filter(Sector.id == sector_id).first()
    if db_sector is None:
        raise HTTPException(status_code=404, detail="Sector not found")

    for key, value in sector.dict().items():
        setattr(db_sector, key, value)

    db.commit()
    db.refresh(db_sector)
    return db_sector


@app.delete("/sectors/{sector_id}")
def delete_sector(sector_id: int, db: Session = Depends(get_db)):
    db_sector = db.query(Sector).filter(Sector.id == sector_id).first()
    if db_sector is None:
        raise HTTPException(status_code=404, detail="Sector not found")

    db.delete(db_sector)
    db.commit()
    return {"message": "Sector deleted successfully"}


# --- Additional endpoints for the other models would follow the same pattern ---
# For brevity, I'll include only key endpoints below and highlight special features


# --- Agent Type endpoints ---
@app.post("/agent-types/", response_model=AgentTypeResponse)
def create_agent_type(agent_type: AgentTypeCreate, db: Session = Depends(get_db)):
    db_agent_type = AgentType(**agent_type.dict())
    db.add(db_agent_type)
    db.commit()
    db.refresh(db_agent_type)
    return db_agent_type


@app.get("/agent-types/", response_model=List[AgentTypeResponse])
def read_agent_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    agent_types = db.query(AgentType).offset(skip).limit(limit).all()
    return agent_types


# --- Agent endpoints ---
@app.post("/agents/", response_model=AgentResponse)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    # Create the agent
    db_agent = Agent(**agent.dict())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)

    # Create an empty ledger for the agent
    ledger = Ledger(agent_id=db_agent.id)
    db.add(ledger)
    db.commit()

    return db_agent


@app.get("/agents/", response_model=List[AgentResponse])
def read_agents(
    skip: int = 0,
    limit: int = 100,
    region_id: Optional[int] = None,
    sector_id: Optional[int] = None,
    agent_type_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Agent)

    # Apply filters if provided
    if region_id:
        query = query.filter(Agent.region_id == region_id)
    if sector_id:
        query = query.filter(Agent.sector_id == sector_id)
    if agent_type_id:
        query = query.filter(Agent.agent_type_id == agent_type_id)

    agents = query.offset(skip).limit(limit).all()
    return agents


# --- Currency and Exchange Rate endpoints ---
@app.post("/currencies/", response_model=CurrencyResponse)
def create_currency(currency: CurrencyCreate, db: Session = Depends(get_db)):
    db_currency = Currency(**currency.dict())
    db.add(db_currency)
    db.commit()
    db.refresh(db_currency)
    return db_currency


@app.post("/exchange-rates/", response_model=ExchangeRateResponse)
def create_exchange_rate(
    exchange_rate: ExchangeRateCreate, db: Session = Depends(get_db)
):
    db_exchange_rate = ExchangeRate(**exchange_rate.dict())
    db.add(db_exchange_rate)
    db.commit()
    db.refresh(db_exchange_rate)
    return db_exchange_rate


@app.get("/exchange-rates/latest")
def get_latest_exchange_rates(db: Session = Depends(get_db)):
    # Get the latest exchange rate for each currency pair
    # This is a more advanced query with subquery
    from sqlalchemy import func

    subq = (
        db.query(
            ExchangeRate.source_currency_id,
            ExchangeRate.target_currency_id,
            func.max(ExchangeRate.effective_date).label("max_date"),
        )
        .group_by(ExchangeRate.source_currency_id, ExchangeRate.target_currency_id)
        .subquery("latest_rates")
    )

    latest_rates = (
        db.query(ExchangeRate)
        .join(
            subq,
            (ExchangeRate.source_currency_id == subq.c.source_currency_id)
            & (ExchangeRate.target_currency_id == subq.c.target_currency_id)
            & (ExchangeRate.effective_date == subq.c.max_date),
        )
        .all()
    )

    return latest_rates


# --- Economic Event Template endpoints ---
@app.post("/event-templates/", response_model=EconomicEventTemplateResponse)
def create_event_template(
    template: EconomicEventTemplateCreate, db: Session = Depends(get_db)
):
    db_template = EconomicEventTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


# --- Economic Event endpoints ---
@app.post("/economic-events/", response_model=EconomicEventResponse)
def create_economic_event(event: EconomicEventCreate, db: Session = Depends(get_db)):
    # Create the economic event
    db_event = EconomicEvent(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # Find accounting rules for this event type
    template_id = db_event.template_id
    if template_id:
        accounting_rules = (
            db.query(AccountingRule)
            .filter(AccountingRule.event_template_id == template_id)
            .all()
        )

        if accounting_rules:
            # Process each accounting rule
            for rule in accounting_rules:
                # Create ledger entry for first agent
                ledger1 = (
                    db.query(Ledger)
                    .filter(Ledger.agent_id == db_event.agent1_id)
                    .first()
                )
                if ledger1:
                    entry = LedgerEntry(
                        ledger_id=ledger1.id,
                        economic_event_id=db_event.id,
                        dt_account_id=rule.dt_account_id,
                        cr_account_id=rule.cr_account_id,
                        dt_ccy=db_event.ccy,
                        dt_amount=db_event.amount,
                        cr_ccy=db_event.ccy,
                        cr_amount=db_event.amount,
                        agent_id=db_event.agent1_id,
                        source_account_id=rule.dt_account_id,  # Simplified mapping
                        destination_account_id=rule.cr_account_id,  # Simplified mapping
                        currency=db_event.ccy,
                        economic_amount=db_event.amount,
                        is_mirror=False,
                    )
                    db.add(entry)

                # If there's a second agent, create mirror entries
                if db_event.agent2_id:
                    ledger2 = (
                        db.query(Ledger)
                        .filter(Ledger.agent_id == db_event.agent2_id)
                        .first()
                    )
                    if ledger2:
                        mirror_entry = LedgerEntry(
                            ledger_id=ledger2.id,
                            economic_event_id=db_event.id,
                            dt_account_id=rule.cr_account_id,  # Swapped for mirror
                            cr_account_id=rule.dt_account_id,  # Swapped for mirror
                            dt_ccy=db_event.ccy,
                            dt_amount=db_event.amount,
                            cr_ccy=db_event.ccy,
                            cr_amount=db_event.amount,
                            agent_id=db_event.agent2_id,
                            source_account_id=rule.cr_account_id,  # Swapped for mirror
                            destination_account_id=rule.dt_account_id,  # Swapped for mirror
                            currency=db_event.ccy,
                            economic_amount=db_event.amount,
                            is_mirror=True,
                        )
                        db.add(mirror_entry)

            db.commit()

    return db_event


# --- Simulation endpoints ---
@app.post("/simulate/")
def run_simulation(request: SimulationRequest, db: Session = Depends(get_db)):
    """Run a simulation for the specified time period"""
    # This would process all event templates, create events based on frequency and probability
    # Simplified implementation - in a real system this would be more complex

    # Find all event templates
    templates = db.query(EconomicEventTemplate).all()
    events_created = []

    for template in templates:
        # Process based on frequency
        # This is simplified - a real implementation would have more complex date handling
        if template.frequency == "Once":
            # For Once events, just create a single instance at the start date
            # And based on probability
            import random

            if random.random() * 100 <= template.probability:
                # Create the event
                # In a real implementation, we'd need to match agents by region and sector
                agents = db.query(Agent).limit(2).all()
                if len(agents) >= 2:
                    event = EconomicEvent(
                        event_type_name=template.name,
                        description=f"Simulated {template.name} event",
                        agent1_id=agents[0].id,
                        agent2_id=agents[1].id,
                        template_id=template.id,
                        ccy="USD",  # Simplified
                        amount=100.0,  # Simplified - would need a more realistic calculation
                        region_id=request.region_id,
                        sector_id=request.sector_id,
                        datetime=request.start_date,
                    )
                    db.add(event)
                    db.commit()
                    db.refresh(event)
                    events_created.append(event)

        # Add handlers for other frequencies (Daily, Weekly, Monthly, etc.)

    return {"message": "Simulation completed", "events_created": len(events_created)}


# --- Wealth calculation endpoint ---
@app.post("/calculate-wealth/", response_model=WealthResponse)
def calculate_wealth(request: WealthCalculationRequest, db: Session = Depends(get_db)):
    """Calculate wealth for a given agent as of a specific date"""
    agent = db.query(Agent).filter(Agent.id == request.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Get the date for calculation
    as_of_date = request.date or datetime.datetime.now()

    # Get the agent's ledger
    ledger = db.query(Ledger).filter(Ledger.agent_id == agent.id).first()
    if not ledger:
        raise HTTPException(status_code=404, detail="Ledger not found for agent")

    # Get all ledger entries up to the given date
    entries = (
        db.query(LedgerEntry)
        .filter(LedgerEntry.ledger_id == ledger.id, LedgerEntry.datetime <= as_of_date)
        .all()
    )

    # Calculate balances by account
    account_balances = {}
    for entry in entries:
        # Simplified - in a real system would need to handle currencies and exchange rates
        if entry.dt_account_id not in account_balances:
            account_balances[entry.dt_account_id] = 0
        if entry.cr_account_id not in account_balances:
            account_balances[entry.cr_account_id] = 0

        # Debit increases the debit account
        account_balances[entry.dt_account_id] += entry.dt_amount
        # Credit decreases the credit account
        account_balances[entry.cr_account_id] -= entry.cr_amount

    # Calculate total wealth (simplified - would consider account types in a real implementation)
    total_wealth = sum(account_balances.values())

    # Map account IDs to names for better readability
    named_balances = {}
    for account_id, balance in account_balances.items():
        account = db.query(Account).filter(Account.id == account_id).first()
        if account:
            named_balances[account.name] = balance

    return WealthResponse(
        agent_id=agent.id,
        agent_name=agent.name,
        total_wealth=total_wealth,
        currency="USD",  # Simplified - would use base currency
        as_of_date=as_of_date,
        account_balances=named_balances,
    )


# --- Database reset endpoint (for testing) ---
@app.post("/admin/reset-database")
def admin_reset_database():
    """Reset the database (for testing purposes)"""
    from db_setup import reset_database, setup_database

    reset_database()
    setup_database()

    return {"message": "Database reset and initialized with default data."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
