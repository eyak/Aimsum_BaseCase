from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass

class DAS(Base):
    __tablename__ = "DAS"
    row_id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int] = mapped_column(primary_key=True)
    tour_no: Mapped[int] = mapped_column(primary_key=True)
    tour_type: Mapped[str]
    stop_no: Mapped[int] = mapped_column(primary_key=True)
    stop_type: Mapped[str]
    stop_location: Mapped[str]
    stop_zone: Mapped[int]
    stop_zone_aimsum: Mapped[int]
    stop_mode: Mapped[str]
    primary_stop: Mapped[str]
    arrival_time: Mapped[str]
    departure_time: Mapped[str]
    prev_stop_location: Mapped[str]
    prev_stop_zone: Mapped[int]
    prev_stop_zone_aimsum: Mapped[int]
    prev_stop_departure_time: Mapped[str]
    drivetrain: Mapped[str]
    make: Mapped[str]
    model: Mapped[str]
    
    def __repr__(self) -> str:
        return f"DAS(person_id={self.person_id!r}, tour_no={self.tour_no!r}, tour_type={self.tour_type!r}, stop_no={self.stop_no!r}, stop_type={self.stop_type!r}, stop_location={self.stop_location!r}, stop_zone={self.stop_zone!r}, stop_mode={self.stop_mode!r}, primary_stop={self.primary_stop!r}, arrival_time={self.arrival_time!r}, departure_time={self.departure_time!r}, prev_stop_location={self.prev_stop_location!r}, prev_stop_zone={self.prev_stop_zone!r}, prev_stop_departure_time={self.prev_stop_departure_time!r}, drivetrain={self.drivetrain!r}, make={self.make!r}, model={self.model!r})"


