from datetime import datetime

from pydantic import BaseModel

class Member(BaseModel):
    name: str
    member_id: str

class Feedback(BaseModel):
    member_id: str
    farmer_name: str
    address: str
    mobile: str
    total_land: str
    used_area: str
    crops: str
    products_used: str
    feedback: str
    date: str  # You can use datetime.date if you want to parse it
    created_at: datetime
