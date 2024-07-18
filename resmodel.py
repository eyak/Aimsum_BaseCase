from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, CHAR, Float

class Base(DeclarativeBase):
    pass

# https://docs.aimsun.com/next/22.0.1/UsersManual/OutputDatabaseDefinition.html#mesys-table
class MESYS(Base):
    __tablename__ = 'MESYS'
    did = Column(Integer, primary_key=True, comment='Replication identifier (Origin Data ID)')
    oid = Column(Integer, nullable=False, comment='Object ID')
    eid = Column(CHAR, nullable=True, comment='External ID (optional)')
    sid = Column(Integer, nullable=True, comment='Subobject Pos (optional) to store data of an object disaggregated by a criteria')
    ent = Column(Integer, nullable=False, comment='Entry number')
    density = Column(Float, nullable=False, comment='Density (veh/km per lane)')    
    density_D = Column(Float, nullable=False, comment='Density (veh/km per lane)')
    flow = Column(Float, nullable=False, comment='Flow (veh/h)')
    flow_D = Column(Float, nullable=False, comment='Mean flow (veh/h)')
    # flow_meso_D = Column(Integer, nullable=False, comment='Mean meso flow (veh/h)')
    # flow_macro_D = Column(Integer, nullable=False, comment='Mean macro flow (veh/h)')
    # input_count_D = Column(Float, nullable=False, comment='Number of vehicles in the network')
    # input_flow_D = Column(Float, nullable=False, comment='Mean flow (veh/h) in the network')
    # ttime_D = Column(Float, nullable=False, comment='Mean travel time (sec/km)')
    # dtime_D = Column(Float, nullable=False, comment='Mean delay time (sec/km)')
    # wtimeVQ_D = Column(Float, nullable=False, comment='Mean waiting time in a virtual queue per vehicle including vehicles inside (seconds)')
    # speed_D = Column(Float, nullable=False, comment='Mean speed (km/h)')
    # spdh_D = Column(Float, nullable=False, comment='Harmonic mean speed(km/h)')
    # travel_D = Column(Float, nullable=False, comment='Total distance traveled (km)')
    # traveltime_D = Column(Float, nullable=False, comment='Total travel time experienced (hours)')
    # totalDistanceTraveledInside = Column(Float, nullable=False, comment='Total distance traveled by the vehicles inside the network (km)')
    # totalTravelTimeInside = Column(Float, nullable=False, comment='Total travel time experienced by the vehicles inside the network (hours)')
    # totalWaitingTime = Column(Float, nullable=False, comment='Total time experienced by the vehicles still waiting outside(hours)')
    # vWait_D = Column(Integer, nullable=False, comment='Number vehicles waiting to enter into the system (vehs)')
    # vIn_D = Column(Integer, nullable=False, comment='Number vehicles in system (vehs)')
    # vOut_D = Column(Integer, nullable=False, comment='Number vehicles out system (vehs)')
    # vLostIn_D = Column(Integer, nullable=False, comment='Number vehicles lost in system (vehs)')
    # vLostOut_D = Column(Integer, nullable=False, comment='Number vehicles lost out system (vehs)')
    # qmean_D = Column(Integer, nullable=False, comment='Mean vehicles in queue (vehs)')
    # qvmean_D = Column(Integer, nullable=False, comment='Mean virtual queue length (vehs)')
    # qvmax_D = Column(Integer, nullable=False, comment='Maximum virtual queue length (vehs)')
    # missedTurnings_D = Column(Integer, nullable=False, comment='Number of missed turns')
    # lane_changes_D = Column(Integer, nullable=False, comment='Number of lane changes/km')
    # total_lane_changes = Column(Integer, nullable=False, comment='Number of lane changes')

    def __repr__(self) -> str:
        return f"MESYS(did={self.did!r}, oid={self.oid!r}, eid={self.eid!r}, sid={self.sid!r}, ent={self.ent!r}), density={self.density!r}, density_D={self.density_D!r}, flow={self.flow!r}, flow_D={self.flow_D!r})"
    
    
class MESYSCAM(Base):
    __tablename__ = 'MESYSCAM'

    did = Column(Integer, primary_key=True, comment='Replication identifier (Origin Data ID)')
    oid = Column(Integer, nullable=False, comment='Object ID')
    eid = Column(CHAR, nullable=True, comment='External ID (optional)')
    ent = Column(Integer, nullable=False, comment='Entry number')
    NbDeleted = Column(Integer, nullable=False, )
    NbDeleted_D = Column(Integer, nullable=False, )
    NbStationary = Column(Integer, nullable=False, )
    NbStationary_D = Column(Integer, nullable=False, )

