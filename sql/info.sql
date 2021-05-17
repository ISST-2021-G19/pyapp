CREATE TABLE ESCUELA(ID VARCHAR(5) PRIMARY KEY,
    NOMBRE VARCHAR(255) NOT NULL,
    ACRONIMO VARCHAR(8) NOT NULL);

CREATE TABLE ALUMNO(ID VARCHAR(40) PRIMARY KEY,
    NOMBRE VARCHAR(255) NOT NULL,
    EMAIL VARCHAR(255) UNIQUE,
    ESCUELA_ID VARCHAR(5) NOT NULL,
    FOREIGN KEY (ESCUELA_ID) REFERENCES ESCUELA(ID));

CREATE TABLE DEPARTAMENTO(ID VARCHAR(4) PRIMARY KEY,
    NOMBRE VARCHAR(255) UNIQUE,
    ACRONIMO VARCHAR(3) UNIQUE,
    ESCUELA_ID VARCHAR(5) NOT NULL,
    FOREIGN KEY (ESCUELA_ID) REFERENCES ESCUELA(ID));

CREATE TABLE PROFESOR(ID VARCHAR(40) PRIMARY KEY,
    NOMBRE VARCHAR(255) NOT NULL,
    EMAIL VARCHAR(255) UNIQUE,
    DEPARTAMENTO_ID VARCHAR(4) NOT NULL,
    FOREIGN KEY (DEPARTAMENTO_ID) REFERENCES DEPARTAMENTO(ID));

CREATE TABLE SUBJECT(ID VARCHAR(40) PRIMARY KEY,
    NOMBRE VARCHAR(255) NOT NULL,
    ACRONIMO VARCHAR(5) NOT NULL,
    DEPARTAMENTO_ID VARCHAR(4) NOT NULL,
    PROFESOR_ID VARCHAR(40) NOT NULL,
    ALUMNO_ID VARCHAR(40) NOT NULL,
    FOREIGN KEY (DEPARTAMENTO_ID) REFERENCES DEPARTAMENTO(ID),
    FOREIGN KEY (PROFESOR_ID) REFERENCES PROFESOR(ID),
    FOREIGN KEY (ALUMNO_ID) REFERENCES ALUMNO(ID));

CREATE TABLE ENCUESTA(ID VARCHAR(40) PRIMARY KEY,
    FECHA TIMESTAMP NOT NULL,
    SUBJECT_ID VARCHAR(40) NOT NULL,
    PROFESOR_ID VARCHAR(40) NOT NULL,
    ALUMNO_ID VARCHAR(40) NOT NULL,
    FOREIGN KEY (SUBJECT_ID) REFERENCES SUBJECT(ID),
    FOREIGN KEY (PROFESOR_ID) REFERENCES PROFESOR(ID),
    FOREIGN KEY (ALUMNO_ID) REFERENCES ALUMNO(ID));

CREATE TABLE RESPUESTA(ID VARCHAR(40) PRIMARY KEY,
    ENCUESTA_ID VARCHAR(40),
    FOREIGN KEY (ENCUESTA_ID) REFERENCES ENCUESTA(ID));

CREATE TABLE PREGUNTAENCUESTA(ID VARCHAR(40) PRIMARY KEY,
    TEXTO VARCHAR(255),
    TIPO VARCHAR(40));

CREATE TABLE TRAITS(ID VARCHAR(40) PRIMARY KEY,
    LABEL VARCHAR(255))

CREATE TABLE RESPUESTA(ID VARCHAR(40) PRIMARY KEY,
    
    PREGUNTA_ID VARCHAR(40),
    RESPUESTA VARCHAR(40),
    FOREIGN KEY (ENCUESTA_ID) REFERENCES ENCUESTA(ID),
    FOREIGN KEY (PREGUNTA_ID) REFERENCES PREGUNTAENCUESTA(ID));

CREATE TABLE RESPUESTACOMENTARIO(ID VARCHAR(40) PRIMARY KEY,
    RESPUESTA TEXT(),
    FOREIGN KEY (ID) REFERENCES ENCUESTA(ID));

CREATE TABLE RESPUESTATRAITS(ID VARCHAR(40) PRIMARY KEY,
    ENCUESTA_ID VARCHAR(40),
    RESPUESTA VARCHAR(100),
    FOREIGN KEY (ENCUESTA_ID) REFERENCES ENCUESTA(ID));