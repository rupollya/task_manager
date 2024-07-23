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
from starlette.exceptions import HTTPException
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.authentication import UnauthenticatedUser
Base = declarative_base()

DATABASE_URL = ("postgresql+asyncpg://task_olse_user:gI8FDezk9tO6y540ne8l91gnJ46Hyc8K@dpg-cqfm355ds78s73c0taog-a.frankfurt-postgres.render.com/task_olse")
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


 


class JWTAuthanticationBackend(AuthenticationBackend):
    async def authenticate(self, request):
        if "authorization" not in request.headers:
            return AuthCredentials(), UnauthenticatedUser()

        auth = request.headers["authorization"]
        try:
            scheme, token = auth.split()
        except ValueError:
            return AuthCredentials(), UnauthenticatedUser()

        if scheme.lower() != "bearer":
            return AuthCredentials(), UnauthenticatedUser()

        payload = decode_access_token(token)
        if payload is None:
            return AuthCredentials(), UnauthenticatedUser()

        return AuthCredentials(["authenticated"]), SimpleUser(payload["sub"])


async def homepage(request):
    return templates.TemplateResponse("index.html", {"request": request})


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



# получение задачи по ID
@requires("authenticated")
async def get_task_by_id(request):
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

    tasks_list = []
    for task in tasks:
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
        tasks_list.append(task_dict)

    return JSONResponse(tasks_list)


# отображаем только завершенные задачи
@requires("authenticated")
async def get_completed_tasks(request):

    user_id = request.user.username
    async with SessionLocal() as session:
        async with session.begin():
            results = await session.execute(
                select(Task).filter(Task.user_id == user_id)
            )
            tasks = results.scalars().all()
    query = task.select().where(task.c.completed == True)
    results = await database.fetch_all(query)

    tasks_list = []
    for row in results:
        task = dict(row)
        task["created_at"] = task["created_at"].isoformat()
        task["data_stop"] = task["data_stop"].isoformat()
        tasks_list.append(task)

    return JSONResponse(tasks_list)

#ТОЛЬКО ВАЖНЫЕ
@requires("authenticated")
async def get_important_tasks(request):
    user_id = request.user.username
    async with SessionLocal() as session:
        async with session.begin():
            results = await session.execute(
                select(Task).filter(Task.user_id == user_id, Task.important == True)
            )
            tasks = results.scalars().all()

    tasks_list = []
    for task in tasks:
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
        tasks_list.append(task_dict)

    return JSONResponse(tasks_list)

#только те что были созданы сегодня
@requires("authenticated")
async def get_tasks_today(request):
    user_id = request.user.username
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
    
    async with SessionLocal() as session:
        async with session.begin():
            results = await session.execute(
                select(Task).filter(Task.user_id == user_id, Task.created_at >= twenty_four_hours_ago)
            )
            tasks = results.scalars().all()

    tasks_list = []
    for task in tasks:
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
        tasks_list.append(task_dict)

    return JSONResponse(tasks_list)

#ОТОБРАЖАЕМ ТОЛЬКО ЗАВЕРШЕННЫЕ
@requires("authenticated")
async def get_completed_tasks(request):
    user_id = request.user.username
    async with SessionLocal() as session:
        async with session.begin():
            results = await session.execute(
                select(Task).filter(Task.user_id == user_id, Task.completed == True)
            )
            tasks = results.scalars().all()

    tasks_list = []
    for task in tasks:
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
        tasks_list.append(task_dict)

    return JSONResponse(tasks_list)
#создаем или редактиурем задачу
@requires("authenticated")
async def create_task(request):
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
                    #обновляем задачу если был получен айди
                    task.heading = heading
                    task.task_text = task_text
                    task.prize = prize
                    task.important = important
                    task.completed = completed
                    task.data_stop = data_stop
                    await session.commit()
                    response_data = {
                        "task_id": task.task_id,
                        "user_id": user_id,
                        "heading": heading,
                        "task_text": task_text,
                        "prize": prize,
                        "important": important,
                        "completed": completed,
                        "data_stop": data_stop.isoformat() if data_stop else None,
                        "created_at": task.created_at.isoformat(),
                    }
                    print("Отправляемые данные на клиент:", response_data)
                    return JSONResponse(response_data, status_code=200)
            #иначе создаем новую
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

    response_data = {
        "task_id": task.task_id,
        "user_id": user_id,
        "heading": heading,
        "task_text": task_text,
        "prize": prize,
        "important": important,
        "completed": completed,
        "data_stop": data_stop.isoformat() if data_stop else None,
        "created_at": task.created_at.isoformat(),
    }

    print("Отправляемые данные на клиент:", response_data)
    return JSONResponse(response_data, status_code=201)


 
 #маршруты
routes = [
    Route("/tasks_today", endpoint=get_tasks_today, methods=["GET"]),
    Route("/registration", registration, methods=["POST"]),
    Route("/create_task", create_task, methods=["POST"]),
    Route("/auth", auth, methods=["POST"]),
    Route("/tasks", get_tasks, methods=["GET"]),
    Route("/tasks_completed", endpoint=get_completed_tasks, methods=["GET"]),
    Route("/tasks_important", endpoint=get_important_tasks, methods=["GET"]),
    Route("/", homepage),
    Mount("/static_css", StaticFiles(directory="static_css"), name="static_css"),
    Mount("/html", StaticFiles(directory="templates"), name="html"),
    Mount("/images", StaticFiles(directory="images"), name="images"),
    Mount("/js", StaticFiles(directory="js"), name="js"),
    Route("/tasks/{task_id:int}", get_task_by_id, methods=["GET"]),
    Route("/tasks/{task_id}", endpoint=delete_task, methods=["DELETE"]),
]


app = Starlette(debug=True, routes=routes)
app.add_middleware(AuthenticationMiddleware, backend=JWTAuthanticationBackend())
