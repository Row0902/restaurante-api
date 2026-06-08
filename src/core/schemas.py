from pydantic import BaseModel


class PlatoCreate(BaseModel):
    nombre: str
    descripcion: str
    precio: float


class PlatoUpdate(BaseModel):
    nombre: str
    descripcion: str
    precio: float


class PlatoRead(BaseModel):
    id: int
    nombre: str
    descripcion: str
    precio: float


class EstadoOrdenUpdate(BaseModel):
    estado: str

class OrdenItem(BaseModel):
    plato_id: int
    cantidad: int


class OrdenCreate(BaseModel):
    items: list[OrdenItem]


class OrdenRead(BaseModel):
    id: int
    items: list
    total: float
    estado: str
