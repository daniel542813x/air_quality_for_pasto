from aiohttp import WebSocketError
from models.main import get_db
from fastapi import APIRouter
from enums import URL_OPEN_MATEO_API, AVAILABLE_GASES
from models import *
import requests
from models.schema import  AirQualitySchema

db = get_db()

router = APIRouter(
    prefix="/air_quality",
)


@router.get("/")
async def read_root():
    return db.query(AirQuality).all()


@router.get("/api/data")
async def get_air_quality(latitude: float, longitude: float, type_gas: str, forecast_days: int):
    if type_gas not in AVAILABLE_GASES:
        return {
            "error": "Invalid type of gas"
        }
    
    url_params = f"?latitude={latitude}&longitude={longitude}&hourly={type_gas}&forecast_days={forecast_days}"
    url = URL_OPEN_MATEO_API + url_params 

    response = requests.get(url)
    
    data = response.json()
    
    result_by_hour = []
    
    for idx, hour in enumerate(data["hourly"]['time']):
        result_by_hour.append({
            "hour": hour,
            "value": data["hourly"][type_gas][idx]
        })
            
    
    return {
        "elevation": data["elevation"],
        "type_gas": type_gas,
        "latitude": latitude,
        "longitude": longitude,
        "forecast_days": forecast_days,
        "data": result_by_hour
    }
    
    
@router.post("/api/data")
async def create_air_quality(air_quality: AirQualitySchema):
    db.add(air_quality)
    db.commit()
    db.refresh(air_quality)
    return air_quality


@router.websocket("/ws")
async def websocket_endpoint(websocket):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
            print(data)
            await websocket.send_text(data)
        except WebSocketError:
            break
    await websocket.close()


