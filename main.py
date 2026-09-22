from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel, Field, Session, create_engine, select

# ---- the model ----
# This single class is BOTH the database table and the API schema
class Application(SQLModel, table=True):
  id: int | None = Field(default=None, primary_key=True)
  company: str
  role: str
  status: str = "applied"


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
def create_application(application: Application) -> Application:
  with Session(engine) as session:
    session.add(application)      # stage the new row
    session.commit()              # write it to the db
    session.refresh(application)  # reload so it has new id
    return application


@app.get("/applications")
def list_applications() -> list[Application]:
  with Session(engine) as session:
    return session.exec(select(Application)).all()

