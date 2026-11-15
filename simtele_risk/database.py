import sqlite3, json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "simtele_risk.db"
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "database" / "schema.sql"

CASE_NAMES = [
    "Detención de emergencia de cabinas",
    "Deterioro mecánico de bombas de agua potable",
    "Oscilaciones por viento en Mi Teleférico",
    "Reconstrucción de sensores de niveles de agua",
]

def connect():
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    return con

def initialize():
    with connect() as con:
        con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        for name in CASE_NAMES:
            con.execute("INSERT OR IGNORE INTO caso_estudio(nombre) VALUES (?)", (name,))

def save_experiment(case_name, scenario, params, method_results, interpretation):
    with connect() as con:
        row = con.execute("SELECT id FROM caso_estudio WHERE nombre=?", (case_name,)).fetchone()
        case_id = row[0]
        cur = con.execute(
            "INSERT INTO escenario(caso_id,tipo,parametros_json,fuente_datos) VALUES (?,?,?,?)",
            (case_id, scenario, json.dumps(params, ensure_ascii=False), "Datos sintéticos académicos")
        )
        scenario_id = cur.lastrowid
        cur = con.execute(
            "INSERT INTO simulacion(escenario_id,fecha,equipo_usuario,estado) VALUES (?,?,?,?)",
            (scenario_id, datetime.now().isoformat(timespec="seconds"), "Equipo SIMTELE-RISK", "completada")
        )
        sim_id = cur.lastrowid
        for method, result in method_results.items():
            cur = con.execute(
                """INSERT INTO ejecucion_metodo
                (simulacion_id,metodo,tolerancia,paso,max_iter,convergio,tiempo_ms)
                VALUES (?,?,?,?,?,?,?)""",
                (sim_id, method, params.get("tolerancia"), params.get("paso"),
                 params.get("max_iter"), int(result.get("convergio", True)),
                 result.get("tiempo_ms"))
            )
            execution_id = cur.lastrowid
            hist = result.get("historial", [])
            if not hist:
                hist = [{"iteracion": 1, "x": result.get("valor"), "residuo": result.get("residuo_inf"),
                         "error_abs": result.get("error_absoluto_inf")}]
            for item in hist:
                con.execute(
                    """INSERT INTO iteracion_resultado
                    (ejecucion_id,numero,aproximacion_json,residual,error_abs,error_rel)
                    VALUES (?,?,?,?,?,?)""",
                    (execution_id, item["iteracion"], json.dumps(item.get("x"), ensure_ascii=False),
                     item.get("residuo"), item.get("error_abs"), result.get("error_relativo_inf"))
                )
            summary = {k:v for k,v in result.items() if k != "historial"}
            con.execute(
                """INSERT INTO resultado_resumen
                (ejecucion_id,referencia,valor_json,metrica_error_json,interpretacion)
                VALUES (?,?,?,?,?)""",
                (execution_id, json.dumps(params.get("referencia"), ensure_ascii=False),
                 json.dumps(summary, ensure_ascii=False),
                 json.dumps({k: result.get(k) for k in ("error_absoluto_inf","error_relativo_inf","error_porcentual_inf","residuo_inf")}, ensure_ascii=False),
                 interpretation)
            )
    return sim_id

def list_experiments(limit=100):
    with connect() as con:
        return con.execute("""
            SELECT s.id, c.nombre, e.tipo, s.fecha, s.estado
            FROM simulacion s
            JOIN escenario e ON e.id=s.escenario_id
            JOIN caso_estudio c ON c.id=e.caso_id
            ORDER BY s.id DESC LIMIT ?
        """, (limit,)).fetchall()

def load_experiment(sim_id):
    with connect() as con:
        head = con.execute("""
            SELECT s.id,c.nombre,e.tipo,e.parametros_json,s.fecha
            FROM simulacion s JOIN escenario e ON e.id=s.escenario_id
            JOIN caso_estudio c ON c.id=e.caso_id WHERE s.id=?
        """, (sim_id,)).fetchone()
        if not head:
            return None
        executions = con.execute("""
            SELECT em.id,em.metodo,em.tolerancia,em.convergio,em.tiempo_ms,
                   rr.valor_json,rr.interpretacion
            FROM ejecucion_metodo em LEFT JOIN resultado_resumen rr ON rr.ejecucion_id=em.id
            WHERE em.simulacion_id=?
        """, (sim_id,)).fetchall()
        return {"header": head, "executions": executions}
