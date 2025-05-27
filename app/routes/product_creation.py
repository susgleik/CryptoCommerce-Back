from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Any
from ..database.database import get_db
from ..models.product_model import Product, Category
from ..schemas import product_schemas


