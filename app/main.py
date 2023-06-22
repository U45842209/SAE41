from fastapi import FastAPI, Request, Form, Response, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRoute
from typing import Annotated
import mysql.connector
import webbrowser
from fastapi_login.exceptions import InvalidCredentialsException
import hashlib
from starlette.exceptions import HTTPException as StarletteHTTPException
import os


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

@app.get("/new_account", response_class=HTMLResponse)
async def create_account(request:Request):
    return templates.TemplateResponse("new_account.html", {"request": request})


@app.post("/new_account")
async def cr_account_post(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    sql = "INSERT INTO users (username,password) VALUES (%s,%s)"
    values = (username,password)
    sql_cursor.execute(sql, values)
    mydb.commit()

    return RedirectResponse(url="/", status_code=303)


@app.get("/")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/")
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
           response = RedirectResponse(url="/", status_code=303)
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
async def rdvpost(request: Request,
                  objet: str = Form(default=None),
                  date: str = Form(default=None),
                  usernamelog: str = Depends(get_username),
                  time: str = Form(default=None),
                  lien_rdv : str = Form(default=None),
                  action : str = Form(...)
                  ):
    if action == "Envoyer":

        #On récupère l'id de l'utilisateur connecté
        sql = "SELECT id FROM users WHERE username = %s"
        valsql = (usernamelog,)
        sql_cursor.execute(sql,valsql)
        resultsql1 = sql_cursor.fetchone()
        print(resultsql1[0])

        #Partie création du lien secret en sha1
        hash = hashlib.sha1()
        nom_rdv = objet
        hash.update(nom_rdv.encode())
        lien = hash.hexdigest()


        #Partie création de la page html du RDV:
        page_type_html = f"""
 <!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Titre de la page</title>
</head>
<body>
    <h1> Vous etes arrives sur la page du rendez vous : {objet}</h1>
</body>
</html>
        """
        with open (f"templates/reu/{hash.hexdigest()}.html", "x") as f:
            f.write(page_type_html)
            f.close()


        #On envoie les différentes informations du rdv dans la BDD
        print(date)
        sql2 = "INSERT INTO rdv (name_rdv, date_rdv, user_id,heure_rdv,lien_secret) VALUES (%s,%s,%s,%s,%s)"
        val = (objet, date, resultsql1[0], time,lien)
        sql_cursor.execute(sql2, val)
        mydb.commit()

        #Creation de la BDD du rdv pour les réponses
        rdv_name = hash.hexdigest()
        sql = f"CREATE TABLE {rdv_name} (user_id INT PRIMARY KEY NOT NULL, reponses INT)"
        sql_cursor.execute(sql)
        mydb.commit()

        return RedirectResponse(url="/rdv", status_code=303)

    #Si on clique sur le bouton "Rejoindre", cela nous envoie sur la page du rdv
    if action =="Rejoindre":
        return RedirectResponse(url=f"/{lien_rdv}", status_code=303)


#Bouton de déconnexion
@app.post("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("username")
    return response


#Bouton de suppression de rdv
@app.post("/delete")
async def delete_rdv(response : Response, item_id: int = Form(...), lien : str = Form(...)):
    sql = "DELETE FROM rdv WHERE id = %s"
    val = (item_id,)
    sql_cursor.execute(sql, val)
    mydb.commit()
    response = RedirectResponse(url="/rdv", status_code=303)

    sqlDel_Table = f"DROP TABLE {lien}"
    sql_cursor.execute(sqlDel_Table)
    mydb.commit()

    os.remove(f"templates/reu/{lien}.html")
    return response



@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    if request.url.path in ["/", "/new_account","/rdv"]:
        # Renvoyer la réponse par défaut sans effectuer d'autres traitements
        return exc

    sql = "SELECT lien_secret FROM rdv WHERE lien_secret LIKE %s"
    url = str(request.url)
    print(url)
    url_split = url.split("/")
    url_end = url_split[-1]
    val = (url_end,)
    sql_cursor.execute(sql, val)
    result = sql_cursor.fetchone() #Ici je récupère dans un tableau tous mes liens secret


    print(type(result))
    print(url_end)

    if url_end in result:
        print("ici")
        return templates.TemplateResponse(f"/reu/{url_end}.html", {"request": request})
    else:
        return templates.TemplateResponse("404.html", {"request": request})