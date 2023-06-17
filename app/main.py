from fastapi import FastAPI, Request, Form, Response, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.routing import APIRoute
from typing import Annotated
import mysql.connector
from mysql.connector import errorcode
import webbrowser


#Partie qui permet de bloquer des pages si le cookie n'est pas set avec le principe du middleware



#Ajout du middleware à FastAPI
app = FastAPI()


#Connexion à la BDD
mydb = mysql.connector.connect(
	host="172.20.0.10",
	port="3306",
	user="root",
	password="password",
	database="SAE410"
)
sql_cursor = mydb.cursor()

#Initialisation des templates pour jinja
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


#Le code du site :


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

    return RedirectResponse(url="/login", status_code=303)


@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def loginpost(response: Response, username: str = Form(...), password: str = Form(...)):
    mydb = mysql.connector.connect(
        host="172.20.0.10",
        port="3306",
        user="root",
        password="password",
        database="SAE410"
    )
    sql_cursor = mydb.cursor()

    sql = "SELECT * FROM users WHERE username = %s"
    val = (username,)
    sql_cursor.execute(sql, val)
    myresult = sql_cursor.fetchall()

    for x in myresult:
        if username in x and password in x:
            print("ok")
            response = RedirectResponse(url="/rdv", status_code=303)
            response.set_cookie(key="username", value=username)
            return response

        else:
            print("pas ok")


def get_username(request: Request):
    return request.cookies.get("username")



@app.get("/rdv")
async def rdv(request: Request, usernamelog: str = Depends(get_username)):
    username = request.cookies.get("username")
    print(username)

    # Partie tableau de RDV
    table_rdv = {}
    #On récupère l'id utilisateur
    sql = "SELECT id FROM users WHERE username = %s"
    valsql = (usernamelog,)
    sql_cursor.execute(sql, valsql)
    resultsql1 = sql_cursor.fetchone()

    #On récupère les rdv de l'utilisateur
    sqlTable = "SELECT * FROM rdv WHERE user_id = %s"
    valtable = (resultsql1[0],)
    sql_cursor.execute(sqlTable, valtable)
    resultsqlTable = sql_cursor.fetchall()
    print(resultsqlTable)

    for line in resultsqlTable:
        item_id = str(line[0])
        item = {
            "objet": line[2],
            "date": line[3].strftime("%Y-%m-%d")
        }
        print(line)
        table_rdv[item_id] = item

    return templates.TemplateResponse("page_user.html", {"request": request, "username": username, "table_rdv": table_rdv})



@app.post("/rdv")
async def rdvpost(objet: Annotated[str, Form()], date: Annotated[str, Form()], usernamelog: str = Depends(get_username)):

    #Partie Creation de RDV
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



    return RedirectResponse(url="/rdv", status_code=303)


@app.post("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("username")
    return response
