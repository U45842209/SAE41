from fastapi import FastAPI, Request, Form, Response, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
from typing import Annotated
import mysql.connector
import webbrowser

mydb = mysql.connector.connect(

    host="localhost",
    user="user_admin",
    password="Password1234*",
    database="SAE410"
)

sql_cursor = mydb.cursor()

print("Ok")

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")



@app.get("/", response_class=HTMLResponse)
async def accueil(request:Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/new_account", response_class=HTMLResponse)
async def create_account(request:Request):
    return templates.TemplateResponse("new_account.html", {"request": request})


@app.post("/new_account")
async def cr_account_post(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    sql = "INSERT INTO users (username,password) VALUES (%s,%s)"
    values = (username,password)
    sql_cursor.execute(sql, values)
    mydb.commit()

    webbrowser.open("http://127.0.0.1:8000/login")


@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def loginpost(username: Annotated[str, Form()], password: Annotated[str, Form()], response: Response):
    sql = "SELECT * FROM users WHERE username = %s"
    val = (username,)
    sql_cursor.execute(sql, val)
    myresult = sql_cursor.fetchall()

    for x in myresult:
        if username in x and password in x:
            print("ok")
            response.set_cookie(key="username", value=username)
            return RedirectResponse(url="/rdv", status_code=303)

        else:
            print("pas ok")


def get_username(request: Request):
    return request.cookies.get("username")


@app.get("/rdv")
async def rdv(request: Request, username: str = Depends(get_username)):
    print(username)
    return templates.TemplateResponse("page_user.html", {"request": request, "username": username})



@app.post("/rdv")
async def rdvpost(objet: Annotated[str, Form()], date: Annotated[str, Form()], usernamelog: str = Depends(get_username)):

    sql = "SELECT id FROM users WHERE username = %s"
    valsql = (usernamelog,)
    sql_cursor.execute(sql,valsql)
    resultsql1 = sql_cursor.fetchone()
    print(resultsql1[0])

    print(date)

    sql2 = "INSERT INTO rdv (name_rdv, date_rdv, user_id) VALUES (%s,%s,%s)"
    val = (objet, date, resultsql1[0])
    sql_cursor.execute(sql2, val)
    mydb.commit()

