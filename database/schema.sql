PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS caso_estudio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    modelo_version TEXT NOT NULL DEFAULT '1.0'
);

CREATE TABLE IF NOT EXISTS escenario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caso_id INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('NORMAL','ESTRES','MAL_CONDICIONADO')),
    parametros_json TEXT NOT NULL,
    fuente_datos TEXT NOT NULL DEFAULT 'Datos sintéticos académicos',
    FOREIGN KEY(caso_id) REFERENCES caso_estudio(id)
);

CREATE TABLE IF NOT EXISTS simulacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    escenario_id INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    equipo_usuario TEXT,
    estado TEXT NOT NULL DEFAULT 'completada',
    FOREIGN KEY(escenario_id) REFERENCES escenario(id)
);

CREATE TABLE IF NOT EXISTS ejecucion_metodo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    simulacion_id INTEGER NOT NULL,
    metodo TEXT NOT NULL,
    tolerancia REAL,
    paso REAL,
    max_iter INTEGER,
    convergio INTEGER NOT NULL,
    tiempo_ms REAL,
    FOREIGN KEY(simulacion_id) REFERENCES simulacion(id)
);

CREATE TABLE IF NOT EXISTS iteracion_resultado (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ejecucion_id INTEGER NOT NULL,
    numero INTEGER NOT NULL,
    aproximacion_json TEXT NOT NULL,
    residual REAL,
    error_abs REAL,
    error_rel REAL,
    FOREIGN KEY(ejecucion_id) REFERENCES ejecucion_metodo(id)
);

CREATE TABLE IF NOT EXISTS resultado_resumen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ejecucion_id INTEGER NOT NULL,
    referencia TEXT,
    valor_json TEXT NOT NULL,
    metrica_error_json TEXT,
    interpretacion TEXT,
    FOREIGN KEY(ejecucion_id) REFERENCES ejecucion_metodo(id)
);
