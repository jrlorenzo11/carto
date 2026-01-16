

# ✅Módulo 


```text
app/
├── _init_.py
├── main.py
│
├── api/
│   ├── v1/
│   │   ├── _init_.py
│   │   └── endpoints.py
│   ├── _init_.py
│   ├── health.py
│   ├── autocad.py
│   ├── osm.py
│   ├── matcher.py
│   ├── tps_warp.py
│   └── pipeline.py
│
├── core/
│   ├── _init_.py
│   ├── bootstrap.py
│   ├── config.py
│   ├── logger.py
│   └── paths.py
│
├── db/
│   ├── _init_.py
│   ├── models.py
│   └── session.py
│
├── log/
│   └── app.log
│
├── models/
│   ├── _init_.py
│   └── domain.py
│
├── services/
│   ├── _init_.py
│   ├── path_resolver.py
│   ├── autocad_service.py       # script 1
│   ├── osm_service.py           # script 2
│   ├── matcher.py               # script 3
│   ├── tps_warp.py              # script 4
│   └── pipeline.py              # scripts 1 a 4
├── data/
│   ├── entrada/
│   └── salida/
│
├── log/
│
├── .env
│
├── README.md
│
└── requirements.txt
```

## ✅A: Estructura de rutas con APIRouter

El objetivo de este paso es solo uno:

Tener endpoints claros (/health, /osm, /reproyectar)
sin meter todavía lógica GIS pesada

Esto deja la API bien cableada antes de avanzar.

### 1️⃣ Idea central (modelo mental)

FastAPI bien armada funciona así:
```text
Request HTTP
   ↓
Router (api/)
   ↓
Endpoint (función)
   ↓
Service (services/)
   ↓
Resultado
```
En este paso solo armamos hasta Router + Endpoint, con lógica mínima.

### 2️⃣ Estructura final que vamos a lograr

Después de A, tu proyecto queda así:
```text
app/
├─ main.py              👈 crea la app y registra routers
├─ api/
│  ├─ __init__.py
│  ├─ health.py         👈 /health
│  ├─ osm.py            👈 /osm (stub)
│  └─ reproyectar.py    👈 /reproyectar (stub)
├─ services/            (todavía no lo usamos)
├─ core/
└─ db/
```
```bash
python -m uvicorn app.main:app --reload
```
- ✔ Sabemos que imports funcionan
- ✔ Sabemos que routers funcionan
- ✔ Sabemos que uvicorn está bien
- ✔ Sabemos que el proyecto escala
- ✔ No mezclamos lógica GIS con HTTP

- ❌ No usamos services
- ❌ No leemos .env
- ❌ No reproyectamos nada
- ❌ No descargamos OSM

## B) Configuración .env + settings tipados
🎯 Objetivo de este paso

Centralizar configuración (CRS, radios, paths, flags)

Leer .env correctamente

Tener tipos, defaults y validación

Que la config esté disponible en toda la app

📌 Nada de os.getenv() suelto.

### 1️⃣ Librería que vamos a usar

FastAPI + Pydantic v2 → usamos BaseSettings

app/core/config.py

📌 Esto hace tres cosas clave:
- Lee .env
- Aplica tipos
- Falla si hay tipos incorrectos

## C) Crear un endpoint que:

- Reciba un CSV de AutoCAD (salida LISP)

- Ejecute tu Script 1 (manzanas + esquinas + grupos de 4)

- Guarde los GeoJSON igual que ahora

- Devuelva un resumen JSON (counts, paths)

FastAPI NO ejecuta scripts automáticamente.
FastAPI:

expone endpoints

llama funciones / clases

devuelve respuestas

👉 Por eso tus scripts deben transformarse en servicios, no en .py que corren solos.


```text
app/
├── api/
│   └── autocad.py          ← endpoint
├── services/
│   └── autocad_service.py  ← lógica GIS (script 1)
```
- no usa paths hardcodeados

- es reutilizable

- se puede llamar desde FastAPI

Opción	            Sirve con FastAPI	Escala	Debug	Recomendada
Memoria directa	    ❌	                ❌	    ❌	    ❌
Contexto	        ❌	                ❌	    ⚠️	    ❌
Archivos	        ✅	                ✅	    ✅	    🟢🟢🟢
PostGIS	            ✅	                🟢	    🟢	    🟡
Cache	            ⚠️	                ❌	    ❌	    ❌