from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src import crud, schemas, database, security

# 1. CREATE ROUTER
# Kapag sa ibang table, palitan niyo lang yung prefix at tags (ex: "/boardinghouse")
router = APIRouter(prefix="/users", tags=['Users'])

# 2. POST ROUTE (CREATE)
# Gagamitin ito para mag-save ng bagong user sa database.
@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # call ang "engine" natin sa crud.py
    user_crud = crud.UserCRUD(db)

    # Error Check: Kapag existing na yung email, mag-rereject tayo (400) since may unique identifier ung email sa models.py
    # Kayo na bahala kung anong possible error sa isang class
    if user_crud.get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = user.model_dump()

    hashed_pw = security.get_password_hash(user.password)
    user_dict["password"] = hashed_pw

    # Save sa database. 
    return user_crud.create(**user_dict)

# 3. GET ROUTE (READ)
# Gagamitin ito para kumuha ng specific user gamit ang ID nila sa URL.
@router.get("/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(database.get_db)):
    # call ang .get() function sa crud.py para hanapin yung user sa DB
    user = crud.UserCRUD(db).get(user_id)
    
    # Error Check: Kapag walang nahanap na user sa database (None), mag-rereject tayo (404)
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")
        
    return user