# SIMTELE-RISK — Semana 1

Proyecto académico de Métodos Numéricos, Universidad Mayor de San Andrés.

## Contexto y alcance

Aplicación educativa con datos sintéticos. No se conecta a equipos reales ni diagnostica infraestructura de Mi Teleférico, sistemas de agua potable o represas.

Los cuatro casos definidos para esta versión son:

1. Detención de emergencia de cabinas — Mi Teleférico, La Paz.
2. Deterioro mecánico y mantenimiento — bombas de agua potable.
3. Oscilaciones por viento — cabinas de Mi Teleférico.
4. Reconstrucción de señales de sensores — niveles de agua en represas.

## Incluido en esta entrega (Semana 1)

- Interfaz web inicial con cuatro casos.
- Formulación y variables de los cuatro modelos.
- Escenarios NORMAL, ESTRÉS y MAL CONDICIONADO.
- Teoría de errores: absoluto, relativo, porcentual, residual y número de condición.
- Comparación de Jacobi, Gauss-Seidel, LU y gradiente conjugado en sistemas SPD 4x4.
- Persistencia SQLite con las seis entidades del DER.
- Guardado y recuperación de las pruebas de sistemas lineales.

## Requisitos

- Python 3.10 o superior.

## Instalación local

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar:

```bash
streamlit run app.py
```

La base `simtele_risk.db` se crea automáticamente al iniciar.

## Estructura

```text
simtele-risk/
├── app.py
├── requirements.txt
├── README.md
├── simtele_risk/
│   ├── numerical.py
│   └── database.py
└── database/
    └── schema.sql
```

## Uso rápido

1. Abrir la aplicación en el navegador.
2. Seleccionar un escenario en la barra lateral.
3. Entrar a cualquiera de los cuatro módulos.
4. En la sección inferior, ejecutar la comparación de sistemas lineales.
5. Revisar matriz, condición, errores, residuos y gráfico.
6. Guardar la comparación y recuperarla desde Historial.

## Advertencias metodológicas

- Todos los valores iniciales son sintéticos y deben justificarse en el informe.
- El gradiente conjugado estándar se aplica únicamente a matrices simétricas definidas positivas.
- Un escenario de mal condicionamiento no es sinónimo de riesgo físico.
- No converger dentro del máximo de iteraciones no demuestra automáticamente que el método sea incorrecto.
- El prototipo no sustituye validación con datos de operadores o entidades públicas.
- Los algoritmos de interpolación, raíces, integración y EDO quedan para la implementación de la semana 2, de acuerdo con el cronograma de la consigna.

## Próximos pasos

- Semana 2: completar interpolación, raíces, integración y EDO; incorporar tablas y gráficos por módulo.
- Semana 3: validar 3 escenarios × 4 módulos, completar persistencia de todas las ejecuciones, conclusiones, pruebas y defensa.
