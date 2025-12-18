from sqlalchemy import create_engine, Column, Integer, String, Float, Text, TIMESTAMP
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import urllib.parse  # <--- NEW IMPORT

# 1. SETUP CREDENTIALS
# Replace '0201#' below with your ACTUAL raw password
raw_password = "akshat@0201#"  
encoded_password = urllib.parse.quote_plus(raw_password)

# 2. CREATE CONNECTION STRING
# We inject the encoded password into the URL safely
DATABASE_URL = f"mysql+pymysql://root:{encoded_password}@localhost:3306/smart_router"

# 3. CREATE ENGINE
# pool_pre_ping=True helps reconnect if the database drops the connection
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 4. DEFINE MODEL
class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(TIMESTAMP, default=datetime.now)
    prompt_text = Column(Text)
    difficulty_level = Column(String(50))
    model_used = Column(String(100))
    token_count = Column(Integer)
    actual_cost = Column(Float)
    hypothetical_cost_gpt4 = Column(Float)
    money_saved = Column(Float)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()