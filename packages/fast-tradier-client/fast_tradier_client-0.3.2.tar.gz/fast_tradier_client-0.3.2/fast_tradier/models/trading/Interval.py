from enum import Enum

class Interval(Enum):
    """Timescale interval for getting history data"""
    Daily = "daily"
    Weekly = "weekly"
    Monthly = "monthly"