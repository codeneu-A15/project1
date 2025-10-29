from sqlalchemy import Column, Integer, String, Text
from .database import Base

class Feedback(Base):
    _tablename_ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    teacher = Column(String(100))
    rating = Column(Integer)
    comment = Column(Text)