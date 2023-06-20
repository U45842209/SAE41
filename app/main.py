from fastapi import FastAPI, Request, Form, Response, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRoute
from typing import Annotated
import mysql.connector
from mysql.connector import errorcode
import webbrowser
from fastapi_login.exceptions import InvalidCredentialsException
from jinja2 import Environment, FileSystemLoader
import hashlib


#Partie qui permet de bloquer des pages si le cookie n'est pas set avec le principe du middleware


adresse_ip = "localhost"
#Ajout du middleware à FastAPI
app = FastAPI()


#Connexion à la BDD

mydb = mysql.connector.connect(

        host=adresse_ip,
        user="user_admin",
        password="Password1234*",
        database="SAE410"
    )
sql_cursor = mydb.cursor()



print("Ok")

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
           response = RedirectResponse(url="/login", status_code=303)
           return response


def get_username(request: Request):
    return request.cookies.get("username")


#Page complète avec le tableau
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
            "date": line[3].strftime("%Y-%m-%d"),
            "time": str(line[4]),
            "lien": str(line[5])
        }
        print(line)
        table_rdv[item_id] = item
        print(item_id)

    return templates.TemplateResponse("page_user.html", {"request": request, "username": username, "table_rdv": table_rdv})


#Partie formulaire de rdv
@app.post("/rdv")
async def rdvpost(objet: Annotated[str, Form()], date: Annotated[str, Form()], usernamelog: str = Depends(get_username), time: str = Form(...)):

    #Partie Creation de RDV
    sql = "SELECT id FROM users WHERE username = %s"
    valsql = (usernamelog,)
    sql_cursor.execute(sql,valsql)
    resultsql1 = sql_cursor.fetchone()
    print(resultsql1[0])

    #Partie création du lien secret en sha1
    hash = hashlib.sha1()
    nom_rdv = objet
    hash.update(nom_rdv.encode())
    lien = f"http://{adresse_ip}/" + hash.hexdigest()

    #Envoie dans la BDD
    print(date)
    sql2 = "INSERT INTO rdv (name_rdv, date_rdv, user_id,heure_rdv,lien_secret) VALUES (%s,%s,%s,%s,%s)"
    val = (objet, date, resultsql1[0], time,lien)
    sql_cursor.execute(sql2, val)
    mydb.commit()



    return RedirectResponse(url="/rdv", status_code=303)

#Bouton de déconnexion
@app.post("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("username")
    return response


#Bouton de suppression de rdv
@app.post("/delete")
async def delete_rdv(response : Response, item_id: int = Form(...)):
    sql = "DELETE FROM rdv WHERE id = %s"
    val = (item_id,)
    sql_cursor.execute(sql, val)
    mydb.commit()

    response = RedirectResponse(url="/rdv", status_code=303)
    return response


