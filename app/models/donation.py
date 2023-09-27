from sqlalchemy import Column, ForeignKey, Integer, Text

from app.core.db import Base
from app.models.base import BaseModel


class Donation(Base, BaseModel):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)
