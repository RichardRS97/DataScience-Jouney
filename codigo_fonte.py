from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import psycopg2
import requests
import os
from dotenv import load_dotenv
import uvicorn

# Carregar variáveis de ambiente
load_dotenv()

# Estabelecendo a conexão com o banco de dados
conn = psycopg2.connect(
    dbname="postgres",  # nome do banco de dados
    user="postgres",    # usuário do banco
    password=os.getenv("DB_PASSWORD", "Resenha123"),
    host="localhost",   # host do banco
    port="5432"         # porta do banco de dados
)

# Criar o cursor para realizar operações no banco
cursor = conn.cursor()

# Exemplo de uma consulta simples
cursor.execute("SELECT version();")
db_version = cursor.fetchone()
print(f"Conexão bem-sucedida! Versão do banco: {db_version[0]}")

# Fechar a conexão quando terminar
cursor.close()
conn.close()

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Conexão com o DB foi realizada com sucesso!"}


# Configuração do banco de dados
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

conn = psycopg2.connect(
    dbname=DB_NAME, user=DB_USER, host=DB_HOST, port=DB_PORT
)
cursor = conn.cursor()

# Criar tabelas se não existirem
cursor.execute("""
    CREATE TABLE IF NOT EXISTS doacoes (
        id SERIAL PRIMARY KEY,
        cpf VARCHAR(11),
        hemocentro_id INTEGER,
        data TIMESTAMP,
        volume INTEGER
    );
    CREATE TABLE IF NOT EXISTS pontuacoes (
        cpf VARCHAR(11) PRIMARY KEY,
        pontos INTEGER DEFAULT 0,
        nivel INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS feedback (
        id SERIAL PRIMARY KEY,
        cpf VARCHAR(11),
        avaliacao INTEGER,
        comentario TEXT
    );
""")
conn.commit()


# Modelos Pydantic
class Doacao(BaseModel):
    cpf: str
    hemocentro_id: int
    data: datetime
    volume: int


class Feedback(BaseModel):
    cpf: str
    avaliacao: int
    comentario: str


# Agendador de tarefas
scheduler = BackgroundScheduler()


scheduler.start()


def enviar_notificacao(cpf):
    print(f"\ud83d\udce2 Notificação enviada para o doador com CPF: {cpf}")


def agendar_notificacao(doacao):
    data_notificacao = doacao.data + timedelta(days=7)
    scheduler.add_job(enviar_notificacao, 'date', run_date=data_notificacao,
                      args=[doacao.cpf])


def atualizar_pontos(cpf, pontos):
    cursor.execute("SELECT pontos FROM pontuacoes WHERE cpf = %s", (cpf,))
    resultado = cursor.fetchone()

    if resultado:
        pontos_atual = resultado[0] + pontos
        cursor.execute("UPDATE pontuacoes SET pontos = %s WHERE cpf = %s",
                       (pontos_atual, cpf))
    else:
        cursor.execute("INSERT INTO pontuacoes (cpf, pontos) VALUES (%s, %s)",
                       (cpf, pontos))

    conn.commit()


# Inicialização da API
app = FastAPI()


LOCAL_API_URL = "https://api.exemplo.com/hemocentros"


@app.get("/hemocentro_proximo")
def obter_hemocentro_proximo(latitude: float = Query(...),
                             longitude: float = Query(...)):
    try:
        response = requests.get(f"{LOCAL_API_URL}?latitude={latitude}"
                                "&longitude={longitude}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500,
                            detail=f"Erro ao obter hemocentro: {str(e)}")


@app.post("/registrar_doacao")
def registrar_doacao(doacao: Doacao):
    try:
        cursor.execute(
            "INSERT INTO doacoes"
            "(cpf, hemocentro_id, data, volume) VALUES (%s, %s, %s, %s)",
            (doacao.cpf, doacao.hemocentro_id, doacao.data, doacao.volume)
        )
        conn.commit()

        agendar_notificacao(doacao)
        atualizar_pontos(doacao.cpf, 10)

        return {"mensagem": "Doação registrada com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/enviar_feedback")
def enviar_feedback(feedback: Feedback):
    try:
        cursor.execute(
            "INSERT INTO feedback "
            "(cpf, avaliacao, comentario) VALUES (%s, %s, %s)",
            (feedback.cpf, feedback.avaliacao, feedback.comentario)
        )
        conn.commit()
        return {"mensagem": "Feedback enviado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ver_feedback")
def ver_feedback(cpf: str):
    cursor.execute("SELECT avaliacao, comentario FROM feedback WHERE cpf = %s",
                   (cpf,))
    feedbacks = cursor.fetchall()
    return {"feedbacks": feedbacks}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
