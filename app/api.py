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
import collections
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


@app.get("/stats/{subjectid}", dependencies=[Depends(JWTBearer())], tags=["subject"])
async def getDataProfessor(subjectid: str, Authorization: Optional[List[str]] = Header(None)) -> dict:
    token = Authorization[0].replace("Bearer ", "")
    email = decodeJWT(token)['user_id']
    questions = []
    traits = []
    uniqueAnswers = []
    answersList = []
    traitList = []
    commentsList = []
    try:
        listAnsweredSurveys = get_AnsweredSurveyList(
            email, subjectid, "isst")
        subjectIdNum = listAnsweredSurveys[0][2]
        profesorId = listAnsweredSurveys[0][3]
        for answeredSurvey in listAnsweredSurveys:
            for value in get_AnswersbyId(answeredSurvey[0]):
                uniqueAnswers.append(value[1])
                answersList.append(value)
            for value in get_TraitsbyId(answeredSurvey[0]):
                traitList.append(value)
            try:
                commentsList.append(get_CommentsbyId(answeredSurvey[0])[0][0])
            except:
                pass
        # questions
        uniqueAnswers = list(set(uniqueAnswers))
        for code in uniqueAnswers:
            sum0 = 0
            sum1 = 0
            sum2 = 0
            sum3 = 0
            sum4 = 0
            sum5 = 0
            for answer in answersList:
                if answer[1] == code:
                    qtext = answer[2]
                    if answer[0] == '0':
                        sum0 += 1
                    if answer[0] == '1':
                        sum1 += 1
                    if answer[0] == '2':
                        sum2 += 1
                    if answer[0] == '3':
                        sum3 += 1
                    if answer[0] == '4':
                        sum4 += 1
                    if answer[0] == '5':
                        sum5 += 1
            else:
                infoquestion = {
                    "questionId": code,
                    "cuestionText": qtext,
                    "dataset": [[0, sum0], [1, sum1], [2, sum2], [3, sum3], [4, sum4], [5, sum5]]
                }
                questions.append(infoquestion)

        # traits
        traitListunique = list(set(traitList))
        for trait in traitListunique:
            infotrait = {
                "traitId": trait[0],
                "traitLabel": trait[1],
                "count": traitList.count(trait)
            }
            traits.append(infotrait)

        returnItem = {
            "subjectId": subjectid,
            "professorId": profesorId,
            "questions": questions,
            "traits": infotrait,
            "comments": commentsList
        }
        return returnItem
    except:
        raise HTTPException(status_code=404, detail="Info Not Found")
