import psycopg2
from psycopg2.extras import RealDictCursor
from .model import QuizResponse

connection = psycopg2.connect(
    database="nextStepDB",
    user="postgres",
    password="password",
    host="localhost",
    port=5432
)

def addQuizResponse(data: QuizResponse):
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    SQLcheck = "SELECT EXISTS(SELECT 1 FROM answers WHERE user_id = %s AND q_id = %s);"
    cursor.execute(SQLcheck, (data.userID, data.domanda))
    esiste = cursor.fetchone()['exists']

    if esiste:
        SQLupdate = "UPDATE answers SET risp_id = %s WHERE user_id = %s AND q_id = %s;"
        cursor.execute(SQLupdate, (data.risposta, data.userID, data.domanda))
    else:
        SQLinsert = "INSERT INTO answers (user_id, q_id, risp_id) VALUES (%s, %s, %s);"
        cursor.execute(SQLinsert, (data.userID, data.domanda, data.risposta))

    connection.commit()
    cursor.close()
    return

def getQuizQuestions(q_ID: int):
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    SQLquery = "SELECT * FROM questions WHERE q_id = %s;"
    cursor.execute(SQLquery, (q_ID,))
    
    q_ans = cursor.fetchone()
    cursor.close()
    return q_ans

def getSchoolPositions(provincia: str):
    if provincia == "XX":
        return getSchoolPositionsNoProv()
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    SQLquery = "SELECT DISTINCT denominazione_sede_direttivo, coory, coorx FROM scuole WHERE provincia = %s;"
    cursor.execute(SQLquery, (provincia,))
    ris = cursor.fetchall()
    cursor.close()
    return ris

def getSchoolPositionsNoProv():
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    SQLquery = "SELECT DISTINCT denominazione_sede_direttivo, coory, coorx FROM scuole"
    cursor.execute(SQLquery)
    ris = cursor.fetchall()
    cursor.close()
    return ris