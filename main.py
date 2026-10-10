from datetime import datetime, timedelta

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine, extract
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./expenses.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Expense(Base):
    __tablename__ = "expenses"

    expense_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Management API")


class ExpenseCreate(BaseModel):
    name: str
    amount: float
    category: str
    date: datetime | None = None


class ExpenseResponse(BaseModel):
    expense_id: int
    name: str
    amount: float
    category: str
    date: datetime

    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "Expense Management API is running"}


@app.post("/expenses/", response_model=ExpenseResponse)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    new_expense = Expense(
        name=expense.name,
        amount=expense.amount,
        category=expense.category,
        date=expense.date or datetime.utcnow(),
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense


@app.get("/expenses/", response_model=list[ExpenseResponse])
def get_expenses(db: Session = Depends(get_db)):
    return db.query(Expense).all()
@app.get("/expenses/month/{year}/{month}", response_model=list[ExpenseResponse])
def get_expenses_by_month(
    year: int,
    month: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(Expense)
        .filter(extract("year", Expense.date) == year)
        .filter(extract("month", Expense.date) == month)
        .all()
    )
@app.get("/totals/")
def get_totals(salary: float = 0, db: Session = Depends(get_db)):
    from sqlalchemy import func

    total_expenses = db.query(func.sum(Expense.amount)).scalar() or 0

    return {
        "total_expenses": total_expenses,
        "total_salary": salary,
        "remaining_amount": salary - total_expenses,
    }
@app.get("/expenses/category/{category}", response_model=list[ExpenseResponse])
def get_expenses_by_category(category: str, db: Session = Depends(get_db)):
    return db.query(Expense).filter(Expense.category == category).all()
@app.get(
    "/expenses/day/{year}/{month}/{day}",
    response_model=list[ExpenseResponse],
)
def get_expenses_by_day(
    year: int,
    month: int,
    day: int,
    db: Session = Depends(get_db),
):
    start = datetime(year, month, day)
    end = start + timedelta(days=1)

    return (
        db.query(Expense)
        .filter(Expense.date >= start)
        .filter(Expense.date < end)
        .all()
    )
@app.get(
    "/expenses/week/{year}/{week}",
    response_model=list[ExpenseResponse],
)
def get_expenses_by_week(
    year: int,
    week: int,
    db: Session = Depends(get_db),
):
    start_date = datetime.fromisocalendar(year, week, 1)
    end_date = start_date + timedelta(days=7)

    return (
        db.query(Expense)
        .filter(Expense.date >= start_date)
        .filter(Expense.date < end_date)
        .all()
    )