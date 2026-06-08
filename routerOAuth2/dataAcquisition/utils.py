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
    try:
        connection.rollback()
        if provincia == "XX":
            return getSchoolPositionsNoProv()
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        SQLquery = """
            SELECT 
                denominazione_sede_direttivo,
                comune_sede_di_direttivo,
                provincia,
                coory,
                coorx,
                indirizzo_sede_di_direttivo,
                cap_sede_dir,
                indirizzo_email_autonomia,
                indirizzo_email_sede_corsi,
                organico_sede,
                tipologia_sede,
                tipologia,
                array_agg(DISTINCT indirizzo_scolastico) 
                    FILTER (WHERE indirizzo_scolastico IS NOT NULL AND indirizzo_scolastico != '') as corsi
            FROM scuole
            WHERE provincia = %s
            GROUP BY 
                denominazione_sede_direttivo,
                comune_sede_di_direttivo,
                provincia,
                coory,
                coorx,
                indirizzo_sede_di_direttivo,
                cap_sede_dir,
                indirizzo_email_autonomia,
                indirizzo_email_sede_corsi,
                organico_sede,
                tipologia_sede,
                tipologia;
        """
        cursor.execute(SQLquery, (provincia,))
        ris = cursor.fetchall()
        cursor.close()
        return ris
    except Exception as e:
        connection.rollback()
        raise e

def getSchoolPositionsNoProv():
    try:
        connection.rollback()
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        SQLquery = SQLquery = """
            SELECT 
                denominazione_sede_direttivo,
                comune_sede_di_direttivo,
                provincia,
                coory,
                coorx,
                indirizzo_sede_di_direttivo,
                cap_sede_dir,
                indirizzo_email_autonomia,
                indirizzo_email_sede_corsi,
                tipologia_sede,
                tipologia,
                array_agg(DISTINCT elem->>'indirizzo_scolastico') 
                    FILTER (WHERE elem->>'indirizzo_scolastico' IS NOT NULL AND elem->>'indirizzo_scolastico' != '') as corsi,
                MAX((elem->>'organico_sede')::integer) as organico_sede
            FROM scuole,
                jsonb_array_elements(indirizzi_scolastici::jsonb) as elem
            GROUP BY 
                denominazione_sede_direttivo,
                comune_sede_di_direttivo,
                provincia,
                coory,
                coorx,
                indirizzo_sede_di_direttivo,
                cap_sede_dir,
                indirizzo_email_autonomia,
                indirizzo_email_sede_corsi,
                tipologia_sede,
                tipologia;
        """
        cursor.execute(SQLquery)
        ris = cursor.fetchall()
        cursor.close()
        return ris
    except Exception as e:
        connection.rollback()
        raise e