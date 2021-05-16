import hashlib

from pydantic.typing import NoneType
from requests.sessions import Request
from app.model import PostSchema, UserLoginSchema
from app.auth.auth_handler import signJWT
from fastapi import FastAPI, HTTPException, Body, Depends, Header
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import signJWT, decodeJWT
from app.auth.auth_check import getEncodedPassword
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import *
from typing import Optional
import app.settings


posts = [
    {
        "id": 1,
        "title": "Pancake",
        "content": "Lorem Ipsum ..."
    }
]

users = [
    {
        "email": "ma.vila@alumnos.upm.es",
        "password": "Marcel"
    }
]

origins = ["*"]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome the app."}


def check_user(data: UserLoginSchema):
    id = get_UserAuth(data.email)
    if id != None:
        return (getEncodedPassword(data.password, get_UserHashedSalt(id)) == get_UserHashedPass(id))
    return False


@app.post("/user/login", tags=["user"])
async def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        return signJWT(user.email)
    raise HTTPException(status_code=401, detail="Wrong Login Details")


@app.get("/user/profile", dependencies=[Depends(JWTBearer())], tags=["posts"])
async def alumno(Authorization: Optional[List[str]] = Header(None)) -> dict:
    token = Authorization[0].replace("Bearer ", "")
    email = decodeJWT(token)['user_id']
    if "@upm.es" in email:
        profesorList = get_Professor(email)[0]
        return{
            "name": profesorList[0],
            "email": profesorList[1],
            "departamento": profesorList[2]
        }
    else:
        alumno = get_Alumno(email, bbdd="isst")
        return {
            "name": alumno[1].split(" ")[0],
            "surname": alumno[1].split(" ")[1],
            "email": alumno[2]
        }


@app.get("/subjects", dependencies=[Depends(JWTBearer())], tags=["subject"])
async def subjects(Authorization: Optional[List[str]] = Header(None)) -> dict:
    token = Authorization[0].replace("Bearer ", "")
    email = decodeJWT(token)['user_id']
    if "@upm.es" in email:
        subjects = get_SubjectsProfesor(email, bbdd="isst")
    else:
        subjects = get_Subjects(email, bbdd="isst")
    objectarray = []
    for subject in subjects:
        objectarray.append({
            "id": subject[1],
            "code": subject[1],
            "name": subject[0],
            "group": subject[2],
            "year": subject[3]
        })

    return objectarray


@app.get("/subjects/{acronimo}/professors", dependencies=[Depends(JWTBearer())], tags=["subjects"])
async def getProfesor(acronimo: str) -> dict:
    profesors = get_ProfesorPerSubject(acronimo, bbdd="isst")
    professorsArray = []
    for profesor in profesors:
        professorsArray.append({
            "id": profesor[0],
            "name": profesor[1],
            "email": profesor[2]
        })

    return professorsArray


@app.get("/surveys/{subjectid}/questions", dependencies=[Depends(JWTBearer())], tags=["survey"])
async def getSurveys(subjectid: str) -> dict:
    surveys = get_Surveys(subjectid, bbdd="isst")
    SurveysArray = []
    for survey in surveys:
        SurveysArray.append({
            "id": survey[0],
            "question": survey[1]
        })

    return SurveysArray


@app.get("/surveys/{subjectid}/traits", dependencies=[Depends(JWTBearer())], tags=["survey"])
async def getTraits(subjectid: str) -> dict:
    traits = get_Traits(subjectid, bbdd="isst")
    traitsArray = []
    for trait in traits:
        traitsArray.append({
            "id": trait[0],
            "label": trait[1]
        })

    return traitsArray


@app.post("/surveys", dependencies=[Depends(JWTBearer())], tags=["survey"])
async def postSurvey(respuesta=Body(...), Authorization: Optional[List[str]] = Header(None)):
    token = Authorization[0].replace("Bearer ", "")
    email = decodeJWT(token)['user_id']
    subject = respuesta["subjectId"]
    professor = respuesta["professor"].lstrip('0')
    listAnswers = [(k, v) for k, v in respuesta['answers'].items()]
    listTraits = respuesta['traits']
    commentsText = respuesta['comments']

    try:
        encuestaId = insert_Form(email, subject, professor, bbdd="isst")
        insert_Answers(encuestaId, listAnswers)
        insert_Traits(encuestaId, listTraits)
        if len(commentsText) > 0:
            insert_CommentsText(encuestaId, commentsText)
        return{
            "message": "DB has been updated"
        }
    except:
        raise HTTPException(status_code=500, detail="Insersion with errors")
