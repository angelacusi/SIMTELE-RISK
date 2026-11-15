import json
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from simtele_risk.numerical import run_linear_comparison
from simtele_risk.database import initialize, save_experiment, list_experiments, load_experiment, CASE_NAMES

st.set_page_config(page_title="SIMTELE-RISK", page_icon="🚡", layout="wide")
initialize()

st.title("🚡 SIMTELE-RISK")
st.caption("Simulador académico de métodos numéricos aplicados a infraestructura boliviana")
st.info("Proyecto educativo con datos sintéticos. No está conectado a equipos reales ni representa diagnósticos de Mi Teleférico, operadores de agua o represas.")

MODULES = {
    CASE_NAMES[0]: {
        "tag": "MÓDULO 1",
        "question": "¿Cómo varían el tiempo y la distancia de detención frente a cambios de velocidad, reacción y frenado?",
        "model": "dx/dt = v(t)     |     dv/dt = -a",
        "description": "Modelo de movimiento longitudinal de una cabina. Para desaceleración constante: t_det = v₀/a y d_frenado = v₀²/(2a).",
        "variables": "x: posición [m] · v: velocidad [m/s] · a: desaceleración [m/s²] · t: tiempo [s].",
        "methods": "Semana 2: RK2, RK4, trapecio, Simpson 1/3, Romberg, bisección, Newton-Raphson y secante.",
    },
    CASE_NAMES[1]: {
        "tag": "MÓDULO 2",
        "question": "¿Cuándo una bomba de agua potable alcanzaría un umbral hipotético de deterioro que justifique inspección?",
        "model": "D(t) = D₀ + αt + βt²     |     D(t) - D_umbral = 0",
        "description": "Indicador sintético de pérdida de eficiencia o desgaste de una bomba. Los coeficientes pueden estimarse mediante un sistema lineal.",
        "variables": "D: indicador de deterioro [%] · t: tiempo [meses] · α: tasa lineal [%/mes] · β: aceleración [%/mes²].",
        "methods": "Semana 1: Jacobi, Gauss-Seidel, LU y gradiente conjugado para calibración. Semana 2: bisección, Newton-Raphson y secante.",
    },
    CASE_NAMES[2]: {
        "tag": "MÓDULO 3",
        "question": "¿Cómo cambia la oscilación lateral de una cabina ante variaciones de fuerza del viento y amortiguamiento?",
        "model": "m x'' + c x' + kx = F_viento(t)",
        "description": "Oscilador forzado amortiguado que aproxima el desplazamiento lateral de una cabina mediante parámetros equivalentes.",
        "variables": "m: masa equivalente [kg] · c: amortiguamiento [N·s/m] · k: rigidez equivalente [N/m] · F: fuerza [N] · x: desplazamiento [m].",
        "methods": "Semana 2: RK2, RK4, trapecio, Simpson 1/3 y Romberg.",
    },
    CASE_NAMES[3]: {
        "tag": "MÓDULO 4",
        "question": "¿Cómo reconstruir registros faltantes de nivel de agua y medir la distorsión causada por ruido?",
        "model": "y_ref(t) = sin(t)  o  y_ref(t) = exp(-t)",
        "description": "Se generan mediciones sintéticas de nivel, se ocultan puntos de prueba y se compara la reconstrucción con la señal conocida.",
        "variables": "t: tiempo [h] · y: nivel de agua [m] (escala sintética). Los valores reales de una represa no se presuponen.",
        "methods": "Semana 2: Lagrange, Newton por diferencias divididas y splines cúbicos.",
    },
}

scenario = st.sidebar.selectbox("Escenario experimental", ["NORMAL", "ESTRES", "MAL_CONDICIONADO"],
                                format_func=lambda x: {"NORMAL":"NORMAL","ESTRES":"ESTRÉS","MAL_CONDICIONADO":"MAL CONDICIONADO"}[x])
page = st.sidebar.radio("Navegación", ["Inicio"] + list(MODULES.keys()) + ["Historial"])
st.sidebar.markdown("---")
st.sidebar.caption("Avance de desarrollo: Semana 1")

def show_module(name, info):
    st.header(f"{info['tag']} · {name}")
    st.write("**Pregunta de estudio:** " + info["question"])
    st.subheader("Modelo matemático")
    st.code(info["model"])
    st.write(info["description"])
    st.caption(info["variables"])
    st.markdown("**Métodos previstos**")
    st.write(info["methods"])
    st.markdown(f"**Escenario seleccionado:** {scenario.replace('_',' ')}")
    st.warning("En esta entrega se documenta el modelo y la definición experimental. La implementación completa de los métodos específicos de este módulo corresponde a las siguientes etapas, salvo la prueba de sistemas lineales del módulo 2.")
    if name == CASE_NAMES[0]:
        st.markdown("**Parámetros ilustrativos (editables en próximas iteraciones)**")
        c1,c2,c3 = st.columns(3)
        v0 = c1.number_input("Velocidad inicial [m/s]", min_value=0.1, value=5.0, step=0.5)
        reaction = c2.number_input("Tiempo de reacción [s]", min_value=0.0, value=2.0, step=0.5)
        a = c3.number_input("Desaceleración [m/s²]", min_value=0.1, value=1.0, step=0.1)
        tdet = v0/a
        df = v0**2/(2*a)
        st.metric("Tiempo de frenado", f"{tdet:.3f} s")
        st.metric("Distancia total estimada (reacción + frenado)", f"{v0*reaction+df:.3f} m")
        st.caption("Cálculo analítico ilustrativo con desaceleración constante; no es una especificación operacional.")
    elif name == CASE_NAMES[1]:
        c1,c2,c3 = st.columns(3)
        d0 = c1.number_input("Deterioro inicial D₀ [%]", min_value=0.0, value=5.0)
        alpha = c2.number_input("Tasa α [%/mes]", min_value=0.0, value=0.8)
        beta = c3.number_input("Coeficiente β [%/mes²]", min_value=0.0, value=0.03, format="%.3f")
        threshold = st.number_input("Umbral hipotético [%]", min_value=0.1, value=40.0)
        roots = np.roots([beta, alpha, d0-threshold]) if beta > 0 else np.array([(threshold-d0)/alpha]) if alpha > 0 else []
        valid = [float(r.real) for r in roots if abs(getattr(r,"imag",0)) < 1e-9 and float(r.real) >= 0]
        if valid:
            st.metric("Tiempo estimado hasta umbral", f"{min(valid):.2f} meses")
        else:
            st.write("No se encontró un tiempo real no negativo con estos parámetros.")
        st.caption("Estimación analítica preliminar. El ajuste/calibración con sistemas lineales se demuestra en la sección de comparación.")
    elif name == CASE_NAMES[2]:
        st.write("Escenarios sugeridos: variar la fuerza externa del viento, el amortiguamiento y la masa equivalente. La condición mal condicionada debe construirse como experimento numérico de calibración, no confundirse con peligro físico.")
    else:
        st.write("Señal de prueba sugerida: y(t)=sin(t) o y(t)=exp(-t). En las siguientes semanas se ocultarán nodos conocidos para medir el error real de reconstrucción.")

if page == "Inicio":
    st.subheader("Panel de casos de estudio")
    st.write("Selecciona uno de los cuatro módulos. Los escenarios son hipótesis académicas con parámetros sintéticos.")
    cols = st.columns(2)
    for i, (name, info) in enumerate(MODULES.items()):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"### {info['tag']}")
                st.markdown(f"**{name}**")
                st.write(info["question"])
                st.caption("Para abrirlo, selecciona este caso en la navegación lateral.")
    st.markdown("---")
    st.subheader("Alcance de la semana 1")
    st.write("Formulación de los cuatro casos, teoría de errores transversal, comparación de sistemas lineales 4×4, escenarios y estructura inicial de persistencia.")
    st.caption("Los métodos de interpolación, raíces, integración y EDO se incorporarán progresivamente en la semana 2.")

elif page in MODULES:
    show_module(page, MODULES[page])

elif page == "Historial":
    st.header("Historial de experimentos")
    records = list_experiments()
    if not records:
        st.info("Todavía no hay simulaciones guardadas. Ejecuta la comparación del módulo de sistemas lineales y guarda sus resultados.")
    else:
        df = pd.DataFrame(records, columns=["ID","Caso","Escenario","Fecha","Estado"])
        st.dataframe(df, use_container_width=True, hide_index=True)
        selected_id = st.selectbox("Seleccionar simulación", [r[0] for r in records])
        if st.button("Recuperar experimento"):
            item = load_experiment(selected_id)
            st.json({
                "simulacion": item["header"],
                "ejecuciones": [
                    {"metodo": e[1], "tolerancia": e[2], "convergio": bool(e[3]),
                     "tiempo_ms": e[4], "resultado": json.loads(e[5]) if e[5] else None,
                     "interpretacion": e[6]} for e in item["executions"]
                ]
            })

st.markdown("---")
st.header("Prueba de sistemas lineales · Semana 1")
st.write("Sistema de calibración sintético A·x=b, con A simétrica definida positiva (SPD) y solución de referencia conocida.")
if st.button("Ejecutar comparación de Jacobi, Gauss-Seidel, LU y gradiente conjugado", type="primary"):
    try:
        result = run_linear_comparison(scenario)
        st.session_state["linear_result"] = result
        st.session_state["linear_scenario"] = scenario
    except Exception as exc:
        st.error(f"No se pudo ejecutar: {exc}")

if "linear_result" in st.session_state:
    result = st.session_state["linear_result"]
    st.subheader(f"Resultados · {st.session_state['linear_scenario'].replace('_',' ')}")
    st.write(result["descripcion"])
    c1,c2,c3 = st.columns(3)
    c1.metric("Número de condición κ₂(A)", f"{result['condicion_2']:.3g}")
    c2.metric("Tolerancia", f"{result['tolerancia']:.1e}")
    c3.metric("Máx. iteraciones", result["max_iter"])
    st.markdown("**Matriz A**")
    st.dataframe(pd.DataFrame(result["A"]), hide_index=True)
    st.write("**Vector b:**", np.array2string(result["b"], precision=7))
    st.write("**Solución de referencia:**", np.array2string(result["referencia"], precision=7))
    rows = []
    for method, r in result["resultados"].items():
        rows.append({
            "Método": method, "Iteraciones": r["iteraciones"],
            "Residuo ∞": r["residuo_inf"], "Error absoluto ∞": r["error_absoluto_inf"],
            "Error relativo ∞": r["error_relativo_inf"],
            "Convergió": "Sí" if r["convergio"] else "No (límite/criterio)",
            "Tiempo [ms]": r["tiempo_ms"]
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    fig, ax = plt.subplots()
    for method, r in result["resultados"].items():
        hist = r["historial"]
        if hist:
            ax.semilogy([h["iteracion"] for h in hist],
                        [max(h["residuo"], 1e-18) for h in hist], label=method)
    ax.set_xlabel("Iteración")
    ax.set_ylabel("Residuo infinito")
    ax.set_title("Convergencia del residuo")
    ax.grid(True, alpha=.25)
    ax.legend()
    st.pyplot(fig)
    st.caption("La condición mal condicionada puede hacer que los métodos iterativos no alcancen la tolerancia dentro del máximo de iteraciones. Eso no equivale por sí solo a demostrar que el algoritmo sea incorrecto.")
    if st.button("Guardar esta comparación en el historial"):
        params = {"tolerancia": result["tolerancia"], "max_iter": result["max_iter"],
                  "condicion_2": result["condicion_2"], "referencia": result["referencia"].tolist(),
                  "matriz_A": result["A"].tolist(), "vector_b": result["b"].tolist()}
        saved = save_experiment(CASE_NAMES[1], scenario, params, result["resultados"],
                                "Prueba sintética de calibración lineal para el módulo de deterioro de bombas de agua.")
        st.success(f"Experimento guardado con ID {saved}. Puedes recuperarlo desde Historial.")

st.markdown("---")
with st.expander("Teoría de errores transversal"):
    st.latex(r"E_a=|x_{ref}-x_{aprox}|")
    st.latex(r"E_r=\frac{|x_{ref}-x_{aprox}|}{|x_{ref}|},\quad x_{ref}\ne 0")
    st.latex(r"E_p=100E_r")
    st.latex(r"r=b-Ax_{aprox},\quad \|r\|_\infty=\max_i |r_i|")
    st.latex(r"\kappa(A)=\|A\|\,\|A^{-1}\|")
    st.caption("Si la referencia es cero, el error relativo no se calcula; debe informarse como no definido y evitar división por cero.")
