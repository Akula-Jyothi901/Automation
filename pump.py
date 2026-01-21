from enum import Enum, IntEnum

"""Level and gradeprice are parameters for Authorisepump method
       API.idl has the details
       
       Created a Enum function for increasing the code readability.

       Note: If we have ENUMs from developer, we shall implement the same.
 """
class PumpSetting(IntEnum):
    GRADE_PRICE_NA = 0
    CASH = 1
    CREDIT = 2
    SYNC_NA = 0
    LEVEL= 0
    GRADE_PRICE = 1
    PREPAY_CANCEL = 4096
    FLAG = 1
    
class MaxValue(IntEnum):
    AMT_NA = 0
    VOLUME_NA = 0
    FLAG_AMT = 2
    FLAG_VOLUME = 4

class PriceMode(Enum):
    SELF = 0
    FULL = 1

class PriceFlag(Enum):
    DEFAULT = 4096  # Could represent standard update flag

class TrsState(IntEnum):
    NOT_ON_OFFER = 0
    ON_OFFER = 1        #CheckOut  - on offer at single POS
    ACCEPTED = 2        #Accepted by customer 
    FORCE_RELEASE = 3
    PAID = 4            #Paid at POS  
    SUPRESS_TIMOUT = 5
    STATE_FORCE_REMOVE=6

class QueryType(IntEnum):
    UNPAID_PAK_BY_PUMP = 0x100
    
class GPIInit(IntEnum):
    pos_number = 1
    version = 0

class MP_Lock(Enum):
    ALL = 0
    LOCK = 1
    UNLOCK = 2

class GPIRetCode(Enum):
    GPI_OK = 0
    GPI_PUMP_LOCKED = 28
    GPI_INVALID_PUMP_NUMBER = 6

class ShiftSetting(IntEnum):
    GET_SHIFT_GPI = 15
    DAY_OF_WEEK = 2           #The day of the week (e.g., 1=Sunday, 2=Monday, etc.)
    SHIFT_NUMBER = 2          #The shift number for that day (e.g., 1=first shift, 2=second shift, etc.)
    START_TIME = 0

class ShiftFlags(IntEnum):
    DO_PUMP_TOTALS = 2             #shift with  pump total 
    DO_TANK_READING = 4            #shift with tank reading
    SET_SHIFT = 8                  #start shift, by the cashier.  
    DO_FORCE_LOCK_PUMP = 20        #lock forecourt after end of shift.
    FORCE_SHIFT_OLA_NOT_EMPTY = 72 #Force shift


class SoftKey(Enum):
    CANCEL = (4,1)
    YES = (3,1)
    NO = (2,1)

    @property
    def row(self):
        return self.value[0]

    @property
    def col(self):
        return self.value[1]
    
class FuelControllerState(Enum):
    """Fuel controller states mapped from pump status"""
    IDLE = 'Idle'
    PRE_FUELING = 'PreFueling'
    FUELING = 'Fueling' 
    POST_FUELING = 'PostFueling'
    UNKNOWN = 'Unknown'


# Mapping from pump status to fuel controller states
PUMP_STATUS_TO_FUEL_STATE = {
    'Ready': FuelControllerState.IDLE.value,
    'Authorized': FuelControllerState.PRE_FUELING.value,
    'Dispensing': FuelControllerState.FUELING.value,
    'Stopped By Operator': FuelControllerState.POST_FUELING.value,
    'Nozzle Left Out': FuelControllerState.POST_FUELING.value
}

    
