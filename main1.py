from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from databases import Database
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker, relationship
from starlette.applications import Starlette
from starlette.authentication import AuthCredentials, AuthenticationBackend, SimpleUser, requires
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.authentication import UnauthenticatedUser
from starlette.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
Base = declarative_base()

#DATABASE_URL = ("postgresql+asyncpg://task_olse_user:gI8FDezk9tO6y540ne8l91gnJ46Hyc8K@dpg-cqfm355ds78s73c0taog-a.frankfurt-postgres.render.com/task_olse")
DATABASE_URL = DATABASE_URL = ("postgresql+asyncpg://postgres:owIbyag820022013@localhost:3306/task_manager")
database = Database(DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
 
#шаблоны
templates = Jinja2Templates(directory="templates")

SECRET_KEY = "POLLYMANAGERTASKED"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Task(Base):
    __tablename__ = "task"

    task_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(DateTime)
    important = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)
    heading = Column(Text)
    task_text = Column(Text)
    data_stop = Column(DateTime)
    prize = Column(Text)
    user = relationship("User")

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    login = Column(String)
    password = Column(String)
    tasks = relationship("Task")

# Сверияем введенный пароль с хешированным
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

#получаем хэш пароль
def get_password_hash(password):
    return pwd_context.hash(password)

#токен
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=1000)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#извлекаем инф из токена досутпа
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

class JWTAuthenticationBackend(AuthenticationBackend):
    async def authenticate(self, request: Request):
        # Извлекаем токен из cookies
        token = request.cookies.get("access_token")
        
        if not token:
            return AuthCredentials(), UnauthenticatedUser()

        # Проверяем токен
        try:
            payload = decode_access_token(token)
        except Exception as e:
            print(f"Ошибка декодирования токена: {e}")
            return AuthCredentials(), UnauthenticatedUser()

        if payload is None:
            return AuthCredentials(), UnauthenticatedUser()

         
        return AuthCredentials(["authenticated"]), SimpleUser(payload["sub"])

async def homepage(request):
    return templates.TemplateResponse("index.html", {"request": request})

 



async def registration_html(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})
#регистрация нового пользователя
async def registration(request):
    data = await request.json()
    async with SessionLocal() as session:
        async with session.begin():
            try:
                user = User(
                    login=data["login"], password=get_password_hash(data["password"])
                )
                session.add(user)
                await session.commit()
                return JSONResponse({"message": "Регистрация прошла успешно."})
            except Exception as e:
                await session.rollback()
                return JSONResponse({"error": str(e)}, status_code=400)

 
#авторизациы пользователя
async def auth(request):
    data = await request.json()
    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(User).filter(User.login == data["login"])
            )
            user = result.scalar_one_or_none()
    if user and verify_password(data["password"], user.password):
        token = create_access_token(data={"sub": user.user_id})
        return JSONResponse({"access_token": token}, status_code=200)
    return JSONResponse({"error": "Неправильные данные"}, status_code=401)

#удаление задачи 
@requires("authenticated")
async def delete_task(request):
    task_id = int(request.path_params["task_id"]) 
    user_id = request.user.username 

    async with SessionLocal() as session:
        async with session.begin():
            #точно ли задача текущего пользователя?
            result = await session.execute(
                select(Task).filter(Task.task_id == task_id, Task.user_id == user_id)
            )
            task = result.scalar_one_or_none()
            
            if task is None:
                return JSONResponse({"error": "Задача не найдена"}, status_code=404)

            # Удаляем задачу
            await session.delete(task)
            await session.commit()

    return JSONResponse({"message": f"Задача с айди={task_id} была удалена"})

#получаем все задачи определенного пользователя
@requires("authenticated")
async def get_tasks_all(request: Request):
    category = request.path_params.get('category')
    user_id = request.user.username
     
    async with SessionLocal() as session:
        async with session.begin():
            if category == "Важные":#ВАЖНЫЕ
                results = await session.execute(
                    select(Task).filter(Task.user_id == user_id, Task.important == True)
                )
                tasks = results.scalars().all()
            elif category == "Завершенные":
                results = await session.execute(
                    select(Task).filter(Task.user_id == user_id, Task.completed == True)
                )
                tasks = results.scalars().all()
            elif category == "Сегодня":
                twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
                results = await session.execute( select(Task).filter(Task.user_id == user_id, Task.created_at >= twenty_four_hours_ago,Task.completed == False)
                )
                tasks = results.scalars().all()
            else:
                results = await session.execute(
                    select(Task).filter(Task.user_id == user_id)
                )
                tasks = results.scalars().all()
                
    
    return templates.TemplateResponse("storage.html", {"request": request, "tasks": tasks, "category": category.capitalize()})

#получаем все задачи определенного пользователя
@requires("authenticated")
async def get_tasks(request):
    user_id = request.user.username
    async with SessionLocal() as session:
        async with session.begin():
            results = await session.execute(
                select(Task).filter(Task.user_id == user_id)
            )
            tasks = results.scalars().all()
    
    return templates.TemplateResponse("storage.html", {"request": request, "tasks": tasks, "category": "Все задачи"})

@requires("authenticated")
async def create_or_edit_task(request):
    if request.method == "POST":
        data = await request.json()
        user_id = request.user.username
        task_id = data.get("task_id")
        heading = data.get("heading")
        task_text = data.get("task_text")
        prize = data.get("prize")
        important = data.get("important", False)
        completed = data.get("completed", False)
        data_stop = data.get("data_stop")

        try:
            data_stop = datetime.strptime(data_stop, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            data_stop = None

        async with SessionLocal() as session:
            async with session.begin():
                if task_id:
                    task = await session.get(Task, task_id)
                    if task:
                        # Обновляем задачу
                        task.heading = heading
                        task.task_text = task_text
                        task.prize = prize
                        task.important = important
                        task.completed = completed
                        task.data_stop = data_stop
                        await session.commit()
                        return HTMLResponse(f'<script>window.location.href = "/storage.html";</script>', status_code=200)
                else:
                    # Создаем новую задачу
                    task = Task(
                        user_id=user_id,
                        heading=heading,
                        task_text=task_text,
                        prize=prize,
                        important=important,
                        completed=completed,
                        data_stop=data_stop,
                        created_at=datetime.now(),
                    )
                    session.add(task)
                    await session.commit()
                    return HTMLResponse(f'<script>window.location.href = "/storage.html";</script>', status_code=200)

        return JSONResponse({"error": "Task not found or no changes made"}, status_code=404)
    
    elif request.method == "GET":
        task_id = request.query_params.get("task_id")
        task = None
        if task_id:
            async with SessionLocal() as session:
                task = await session.get(Task, int(task_id))

        context = {"request": request, "task": task}
        return templates.TemplateResponse("task_dob.html", context)

# получение задачи по ID
@requires("authenticated")
async def get_task_by_id(request):
    print("все плохо")
    task_id = int(request.path_params["task_id"])
    user_id = request.user.username
   
    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(Task).filter(Task.task_id == task_id, Task.user_id == user_id)
            )
            task = result.scalar_one_or_none()

    if task:
        task_dict = {
            "task_id": task.task_id,
            "user_id": task.user_id,
            "created_at": task.created_at.isoformat(),
            "important": task.important,
            "completed": task.completed,
            "heading": task.heading,
            "task_text": task.task_text,
            "data_stop": task.data_stop.isoformat() if task.data_stop else None,
            "prize": task.prize,
        }
        return JSONResponse(task_dict)
    else:
        return JSONResponse({"error": "Task not found"}, status_code=404)
    
 #маршруты
routes = [
    Route("/storage.html", get_tasks, methods=["GET"]),
    Route("/tasks/{category}", get_tasks_all, methods=["GET"]),
    Route("/task_dob.html", create_or_edit_task, methods=["GET", "POST"]), 
    Route("/registration", registration, methods=["POST"]),
    Route("/auth", auth, methods=["POST"]),
    Route("/", homepage),
    Route("/registration.html", registration_html),
    Mount("/static_css", StaticFiles(directory="static_css"), name="static_css"),
    Mount("/images", StaticFiles(directory="images"), name="images"),
    Mount("/js", StaticFiles(directory="js"), name="js"),
    Route("/tasks/{task_id:int}", get_task_by_id, methods=["GET"]),
    Route("/tasks/{task_id}", endpoint=delete_task, methods=["DELETE"]),
]

app = Starlette(debug=True, routes=routes)
app.add_middleware(SessionMiddleware, secret_key='your-secret-key')  #ключ для сессии
app.add_middleware(AuthenticationMiddleware, backend=JWTAuthenticationBackend())