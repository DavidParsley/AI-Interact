
from fastapi import  Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from models import get_db, Users, RevokedToken
from schemas import CreateUserSchema, LoginUserSchema, UpdateUserSchema
from auth import signJWT, hash_password, verify_password, get_current_user, JWTBearer


router = APIRouter(
    prefix="/user",
    tags=['user']
)

# Sign up
@router.post("/signup", tags=["user"])
def create_user(user: CreateUserSchema, session: Session = Depends(get_db)):
    hashed_pw = hash_password(user.password)
    user_dict = user.model_dump()
    user_dict["password"] = hashed_pw

    check_email = session.query(Users).filter(Users.email == user.email).first()
    if check_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user = Users(**user_dict)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "User created successfully", "user": signJWT(new_user.id)}

# Login
@router.post("/login", tags=["user"])
def user_login(user: LoginUserSchema, session: Session = Depends(get_db)):
    db_user = session.query(Users).filter_by(email=user.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Email not found.")
    
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Incorrect password.")
    
    return signJWT(db_user.id)


# Current User
@router.get("/current_user", tags=["user"])
def read_current_user(current_user: Users = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
    }

# Update User
@router.patch("/update", tags=["user"])
def update_user(updates: UpdateUserSchema, session: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    updated = False

    if updates.email:
        existing_email = session.query(Users).filter(Users.email == updates.email).first()
        if existing_email and existing_email.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = updates.email
        updated = True

    if updates.password:
        current_user.password = hash_password(updates.password)
        updated = True

    if updated:
        session.commit()
        session.refresh(current_user)
        return {
            "message": "User updated successfully",
            "user": {
                "id": current_user.id,
                "email": current_user.email
            }
        }
    else:
        raise HTTPException(status_code=400, detail="No fields to update")
    
# Logout 
@router.delete("/logout", tags=["user"])
def logout(token: str = Depends(JWTBearer()), session: Session = Depends(get_db)):
    revoked_token = RevokedToken(token=token)
    session.add(revoked_token)
    session.commit()
    return {"message": "Successfully logged out"}