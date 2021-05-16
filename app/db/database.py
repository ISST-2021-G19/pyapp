from typing import List
from fastapi.param_functions import Query
import psycopg2
from datetime import datetime
from pydantic.typing import NoneType


def _executeRetrieveAll(query, bbdd: str, returnResult=None) -> list:
    conn = psycopg2.connect(
        host="localhost",
        database=bbdd,
        user="postgres",
        password="json")
    cursor = conn.cursor()
    cursor.execute(query)
    returnResult = cursor.fetchall()
    conn.close()

    return returnResult


def _executeRetrieveOne(query, bbdd: str, returnResult=None) -> tuple:
    conn = psycopg2.connect(
        host="localhost",
        database=bbdd,
        user="postgres",
        password="json")
    cursor = conn.cursor()
    cursor.execute(query)
    returnResult = cursor.fetchone()
    conn.close()

    return returnResult


def _executeInserts(query, bbdd: str, returnResult=None) -> list:
    conn = psycopg2.connect(
        host="localhost",
        database=bbdd,
        user="postgres",
        password="json")
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()


def get_Escuela(bbdd="isst") -> tuple:
    return _executeRetrieveOne("SELECT * FROM ESCUELA", bbdd, returnResult=True)


def get_allAlumnos(bbdd="isst") -> list:
    return _executeRetrieveAll("SELECT * FROM ALUMNO", bbdd, returnResult=True)


def get_UserAuth(mail, bbdd="Auth") -> str:
    try:
        user = _executeRetrieveOne("SELECT Id FROM ALUMNO where email = '{}'".format(
            mail), bbdd, returnResult=True)[0]
    except:
        user = None
    return user


def get_UserHashedPass(id, bbdd="Auth") -> str:
    pwd = _executeRetrieveOne("SELECT encodedpwd FROM PWD where user_id = '{}'".format(
        id), bbdd, returnResult=True)[0]
    pwd = pwd.split(" ")[1].replace("'", "")
    return str.encode(pwd)


def get_UserHashedSalt(id, bbdd="Auth") -> bytes:
    salt = _executeRetrieveOne("SELECT encodedpwd FROM PWD where user_id = '{}'".format(
        id), bbdd, returnResult=True)[0]
    salt = salt.split(" ")[0].replace("'", "")
    return str.encode(salt)


def get_Alumno(email, bbdd="isst") -> list:
    return _executeRetrieveOne("SELECT * FROM ALUMNO Where email = '{}'".format(email), bbdd, returnResult=True)


def get_Subjects(email, bbdd="isst") -> list:
    id_alumno = _executeRetrieveOne("SELECT id FROM ALUMNO Where email = '{}'".format(
        email), bbdd, returnResult=True)[0]
    subjects = _executeRetrieveAll("""SELECT DISTINCT SUBJECT.nombre, SUBJECT.acronimo, DEPARTAMENTO.nombre, SUBJECT.curso
                                    FROM SUBJECT 
                                    INNER JOIN DEPARTAMENTO
                                    on SUBJECT.departamento_id = DEPARTAMENTO.id
                                    Where alumno_id = '{}'""".format(id_alumno), bbdd, returnResult=True)
    return subjects


def get_ProfesorPerSubject(acronimo, bbdd="isst") -> list:
    professors = _executeRetrieveAll("""SELECT DISTINCT SUBJECT.profesor_id, PROFESOR.nombre, PROFESOR.email
                                    FROM SUBJECT 
                                    INNER JOIN PROFESOR
                                    on SUBJECT.profesor_id = PROFESOR.id
                                    Where acronimo = '{}'""".format(acronimo), bbdd, returnResult=True)
    return professors


def get_Surveys(subjectId=None, bbdd="isst") -> list:
    surveys = _executeRetrieveAll(
        "SELECT * FROM PREGUNTAENCUESTA", bbdd, returnResult=True)
    return surveys


def get_Traits(subjectId=None, bbdd="isst") -> list:
    surveys = _executeRetrieveAll(
        "SELECT * FROM TRAITS", bbdd, returnResult=True)
    return surveys

# Post


def insert_Form(email: str, subject: str, professor: str, bbdd="isst"):
    userId = _executeRetrieveOne("SELECT Id FROM ALUMNO where email = '{}'".format(
        email), bbdd, returnResult=True)[0]
    subjectId = _executeRetrieveOne("SELECT Id FROM SUBJECT where acronimo = '{}' AND profesor_id = '{}'".format(
        subject, professor), bbdd, returnResult=True)[0]
    stringId = userId + professor + subjectId
    query = """INSERT INTO encuesta (id, fecha, subject_id, profesor_id, alumno_id)VALUES ('{}','{}','{}','{}','{}')""".format(
        stringId, datetime.now(tz=None), subjectId, professor, userId)

    _executeInserts(query, "isst")

    return stringId


def insert_Answers(encuestaId: str, listAnswers: list):
    for answer in listAnswers:
        id = encuestaId + answer[0]
        query = "INSERT INTO respuesta VALUES ('{}','{}','{}','{}')".format(
            id, encuestaId, answer[0], answer[1])
        _executeInserts(query, "isst", returnResult=None)


def insert_Traits(encuestaId: str, listTraits: list):
    for trait in listTraits:
        id = encuestaId + trait
        query = "INSERT INTO respuestatraits VALUES ('{}','{}','{}')".format(
            id, encuestaId, trait)
        _executeInserts(query, "isst", returnResult=None)


def insert_CommentsText(encuestaId: str, listTraits: list):
    id = encuestaId
    query = "INSERT INTO respuestacomentario VALUES ('{}','{}')".format(
        id, listTraits)
    _executeInserts(query, "isst", returnResult=None)
