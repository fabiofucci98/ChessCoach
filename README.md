## 🛠️ Tech Stack

### **Frontend**
* **Framework:** Next.js (TypeScript)
* **Styling:** Tailwind CSS

### **Backend & API**
* **Framework:** FastAPI (Python 3.11)
* **ORM:** SQLAlchemy 2.0 (Async)
* **Validation:** Pydantic v2

### **Database & Caching**
* **Database:** PostgreSQL 16
* **Cache & Message Broker:** Redis

### **Asynchronous Tasks & Engine**
* **Task Queue:** Celery
* **Chess Engine:** Stockfish Engine

### **DevOps & Containerization**
* **Orchestration:** Docker & Docker Compose

---

## 🚀 Guida Rapida con Docker (Consigliata)

Avvia l'intero ecosistema dell'applicazione con un solo comando.

### 1. Avvio dei Container

```bash
# Sviluppa e avvia tutti i servizi in modalità detached
docker compose up -d --build

# Visualizza i log in tempo reale di tutti i servizi
docker compose logs -f
```

### 2. Mappa dei Servizi ed Endpoints

| Servizio | Porta / URL | Descrizione |
| :--- | :--- | :--- |
| **Frontend (Next.js)** | `http://localhost:3000` | Web Dashboard per l'utente |
| **Backend API (FastAPI)** | `http://localhost:8000` | REST API |
| **Documentazione API (Swagger)** | `http://localhost:8000/docs` | Interfaccia Swagger UI per testare le API |
| **PostgreSQL** | `localhost:5432` | Database principale |
| **Redis** | `localhost:6379` | Cache / Broker dei messaggi Celery |

### 3. Gestione Migrazioni Database (Alembic)

Le migrazioni vengono eseguite automaticamente all'avvio del container API. Se hai la necessità di gestirle manualmente:

```bash
# Genera una nuova migrazione dopo aver aggiornato i modelli SQLAlchemy
docker compose exec api alembic revision --autogenerate -m 

# Applica le migrazioni pendenti
docker compose exec api alembic upgrade head
```

### 4. Arresto dei Container

```bash
# Ferma i container (mantiene sicuri i dati del database nei volumi)
docker compose down

# Ferma e cancella i volumi del database (ripartenza pulita)
docker compose down -v
```

---

## 💻 Configurazione Sviluppo Locale (VS Code)

Configurare gli ambienti locali permette di sfruttare l'autocompletamento dell'IDE, il controllo dei tipi ed evitare segnalazioni d'errore (red squigglies) in VS Code.

### 1. Setup Backend (Python Virtual Environment)

```powershell
# Spostati nella cartella principale del progetto
cd C:\Users\fabio\Desktop\chesscoach

# Crea l'ambiente virtuale
python -m venv backend\.venv

# Attiva l'ambiente virtuale (Windows PowerShell)
.\backend\.venv\Scripts\Activate.ps1

# Aggiorna pip e installa le dipendenze
python -m pip install --upgrade pip
pip install -r backend/requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

```

> **Selezionare l'interprete in VS Code:**
> Premere `Ctrl + Shift + P` $\rightarrow$ *Python: Select Interpreter* $\rightarrow$ Selezionare `backend/.venv/Scripts/python.exe`.

### 2. Setup Frontend (Node.js / Next.js)

```powershell
# Entra nella cartella frontend
cd frontend

# Installa le dipendenze locali Node.js
npm install

# Avvia il server di sviluppo Next.js
npm run dev
```


---

## 📂 Struttura del Progetto

```plaintext
chesscoach/
├── .vscode/                 # Impostazioni workspace VS Code (PYTHONPATH)
├── backend/                 # Applicazione FastAPI
│   ├── app/
│   │   ├── core/            # Configurazioni, connessione DB, setup Celery
│   │   ├── migrations/      # Script di migrazione Alembic
│   │   ├── models/          # Modelli DB SQLAlchemy
│   │   ├── routes/          # Endpoints API REST
│   │   └── tasks/           # Task asincroni Celery (Stockfish)
│   ├── Dockerfile
│   ├── alembic.ini
│   └── requirements.txt
├── frontend/                # Applicazione Next.js
│   ├── app/                 # Next.js App Router
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml       # Orchestratore multi-container
└── README.md                # Documentazione del progetto
```

---

## ⚡ Cheat Sheet dei Comandi Principali

| Operazione | Comando |
| :--- | :--- |
| **Avviare tutto** | `docker compose up -d` |
| **Ricostruire dopo cambio dipendenze** | `docker compose build` |
| **Controllare i log di un servizio** | `docker compose logs -f api` *(o `worker`, `web`)* |
| **Creare una migrazione DB** | `docker compose exec api alembic revision --autogenerate -m "msg"` |
| **Applicare migrazioni DB** | `docker compose exec api alembic upgrade head` |