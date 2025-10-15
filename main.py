from fastapi import FastAPI
from typing import Dict

from fastapi.params import Depends
from pydantic import BaseModel  # Để type hint cho data echo

app = FastAPI(
    title="My First Backend API",  # Tiêu đề hiển thị trong docs
    description="API cơ bản để học FastAPI - Ngày 1",
    version="1.0.0"
)

@app.get("/hello/{name}")
def home(name: str):
    """
    Endpoint trả về lời chào với tên được cung cấp.
    - **name**: Tên người dùng để chào hỏi.
    """
    return {"message": f"Hello {name}"}

class CalcData(BaseModel):
    a: int
    b: int

@app.post("/calculate")
def calculate(data: CalcData):
    """
    Endpoint thực hiện phép cộng hai số nguyên.
    - **data**: Đối tượng JSON chứa hai số nguyên `a` và `b`.
    """
    result = data.a + data.b
    return {"result": result}


products = ['Apple', 'Banana', 'Orange', 'Grapes', 'Mango', 
            'Pineapple', 'Strawberry', 'Blueberry', 'Watermelon', 'Peach']

class ProductsParam(BaseModel):
    limit: int = 5

@app.get("/products")
def get_products(params: ProductsParam = Depends()):
    """
    Returns a list of products with a limit.
    """
    return {"products": products[:params.limit]}
