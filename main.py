from contextlib import asynccontextmanager
from enum import StrEnum
from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select

# ---- enum ----
class Status(StrEnum):
  APPLIED = "applied"
  INTERVIEWING = "interviewing"
  OFFER = "offer"
  REJECTED = "rejected"
  WITHDRAWN = "withdrawn"

# ---- the model ----
class Application(SQLModel, table=True):
  id: int | None = Field(default=None, primary_key=True)
  company: str
  role: str
  status: Status = Status.APPLIED

# ---- # Non-table model so FastAPI validates request bodies (table models don't) ----
class ApplicationCreate(SQLModel):
  company: str
  role: str
  status: Status = Status.APPLIED

# define patch schema
class ApplicationUpdate(SQLModel):
  company: str | None = None
  role: str | None = None
  status: Status | None = None

# ---- the database ----
engine = create_engine("sqlite:///applications.db")

def init_db():
  SQLModel.metadata.create_all(engine) # creates the table if it doesn't exist


# ---- app startup ----
@asynccontextmanager
async def lifespan(app: FastAPI):
  init_db()   # run once when the app starts
  yield

app = FastAPI(lifespan=lifespan)

# ---- endpoints ----
@app.post("/applications")
def create_application(application: ApplicationCreate) -> Application:
  with Session(engine) as session:
    db_application = Application.model_validate(application)
    session.add(db_application)      # stage the new row
    session.commit()              # write it to the db
    session.refresh(db_application)  # reload so it has new id
    return db_application


@app.get("/applications")
def list_applications() -> list[Application]:
  with Session(engine) as session:
    return session.exec(select(Application)).all()

# define patch endpoint
@app.patch("/applications/{application_id}")
def patch_application(application_id: int, application_update: ApplicationUpdate) -> Application:
  with Session(engine) as session:
    # find the stored record based, throw exception if not found
    application_item = session.get(Application, application_id)
    if not application_item:
      raise HTTPException(status_code = 404, detail="Application not found")

    # update the data passed using model_dump
    update_data = application_update.model_dump(exclude_unset=True, exclude_none=True)

    # update db instance with dict data
    application_item.sqlmodel_update(update_data)

    # persist changes and return
    session.add(application_item)
    session.commit()
    session.refresh(application_item)

    return application_item
