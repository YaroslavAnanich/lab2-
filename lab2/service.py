from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from model import User, Post, Base
from database import engine, session_local
from schemas import UserAddSchem, UserDbSchem, PostAddSchem, PostDbSchem, UserDelSchem, PostDelSchem, UserLoginSchem, UserVisitSchem


app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/users/add", response_model=UserDbSchem)
async def create_user(user: UserAddSchem, db: Session = Depends(get_db)):
    existing_user = db.query(User).first()
    if existing_user is not None:
        existing_user = db.query(User).filter(User.name == user.name).first()
        if existing_user is not None:
            raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует.")
    db_user = User(name=user.name, password=user.password, role=user.role, visits=0)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/api/posts/add", response_model=PostDbSchem)
async def create_post(post: PostAddSchem, db: Session = Depends(get_db)):
    db_post = Post(title=post.title, body=post.body, addition=post.addition)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.post("/api/users/edit", response_model=UserDbSchem)
async def edit_user(user: UserDbSchem, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user.id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    db_user.name = user.name
    db_user.password = user.password
    db_user.role = user.role
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/api/posts/edit", response_model=PostDbSchem)
async def edit_post(post: PostDbSchem, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post.id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Пост не найден")
    db_post.title = post.title
    db_post.body = post.body
    db_post.addition = post.addition
    db.commit()
    db.refresh(db_post)
    return db_post


@app.delete("/api/users/del", response_model=UserDbSchem)
async def del_user(user: UserDelSchem, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user.id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if db_user.role == "admin":
        raise HTTPException(status_code=404, detail="Невозможно удалить админа")
    db.delete(db_user)
    db.commit()
    db.query(User).filter(User.id > user.id).update({User.id: User.id - 1}, synchronize_session=False)
    db.commit()
    return db_user


@app.delete("/api/posts/del", response_model=PostDbSchem)
async def del_post(post: PostDelSchem, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post.id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Пост не найден")
    db.delete(db_post)
    db.commit()
    db.query(Post).filter(Post.id > post.id).update({Post.id: Post.id - 1}, synchronize_session=False)
    db.commit()
    return db_post


@app.get("/api/posts/get", response_model=list[PostDbSchem])
async def get_post(db: Session = Depends(get_db)):
    db_post = db.query(Post)
    return db_post


@app.post("/api/recommend")
async def find_visits(expected_visits: UserVisitSchem, db: Session = Depends(get_db)):
    existing_user = db.query(User).all()
    total_visits = db.query(func.sum(User.visits)).scalar()
    if existing_user is None:
        raise HTTPException(status_code=404, detail="Пользователи не найдены")
    if expected_visits.visit > total_visits:
        recommendation = "Чаще добавляйте посты!!"
    else:
        recommendation = "Продолжайте в том же духе!!"
    return {"message": recommendation}


@app.post("/api/users/login", response_model=UserDbSchem)
async def login_user(user: UserLoginSchem, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.name == user.name).first()
    if existing_user is None:
        raise HTTPException(status_code=400, detail="Имя введено не верно.")
    if existing_user.password != user.password:
        raise HTTPException(status_code=400, detail="Пароль введен не верно.")
    existing_user.visits += 1
    db.commit()
    db.refresh(existing_user)
    return existing_user


