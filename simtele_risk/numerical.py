"""Métodos numéricos de la primera semana para SIMTELE-RISK."""
import time
import numpy as np
from scipy.linalg import lu_factor, lu_solve

def error_metrics(reference, approximation):
    ref = np.asarray(reference, dtype=float)
    approx = np.asarray(approximation, dtype=float)
    abs_err = np.abs(ref - approx)
    abs_norm = float(np.linalg.norm(abs_err, ord=np.inf))
    ref_norm = float(np.linalg.norm(ref, ord=np.inf))
    rel = abs_norm / ref_norm if ref_norm != 0 else None
    return {
        "error_absoluto_inf": abs_norm,
        "error_relativo_inf": rel,
        "error_porcentual_inf": rel * 100 if rel is not None else None,
    }

def residual_metrics(A, b, x):
    r = np.asarray(b, dtype=float) - np.asarray(A, dtype=float) @ np.asarray(x, dtype=float)
    return r, float(np.linalg.norm(r, ord=np.inf))

def jacobi(A, b, tol=1e-8, max_iter=1000, x0=None, reference=None):
    A, b = np.asarray(A, float), np.asarray(b, float)
    x = np.zeros_like(b) if x0 is None else np.asarray(x0, float).copy()
    if np.any(np.isclose(np.diag(A), 0)):
        raise ValueError("Jacobi requiere elementos diagonales no nulos.")
    D = np.diag(A)
    R = A - np.diagflat(D)
    history = []
    converged = False
    for k in range(1, max_iter + 1):
        xn = (b - R @ x) / D
        _, res = residual_metrics(A, b, xn)
        err = error_metrics(reference, xn)["error_absoluto_inf"] if reference is not None else None
        history.append({"iteracion": k, "x": xn.tolist(), "residuo": res, "error_abs": err})
        if np.linalg.norm(xn - x, ord=np.inf) <= tol and res <= max(tol, 1e-14):
            x, converged = xn, True
            break
        x = xn
    return x, history, converged

def gauss_seidel(A, b, tol=1e-8, max_iter=1000, x0=None, reference=None):
    A, b = np.asarray(A, float), np.asarray(b, float)
    n = len(b)
    x = np.zeros_like(b) if x0 is None else np.asarray(x0, float).copy()
    if np.any(np.isclose(np.diag(A), 0)):
        raise ValueError("Gauss-Seidel requiere elementos diagonales no nulos.")
    history, converged = [], False
    for k in range(1, max_iter + 1):
        old = x.copy()
        for i in range(n):
            x[i] = (b[i] - np.dot(A[i, :i], x[:i]) - np.dot(A[i, i+1:], old[i+1:])) / A[i, i]
        _, res = residual_metrics(A, b, x)
        err = error_metrics(reference, x)["error_absoluto_inf"] if reference is not None else None
        history.append({"iteracion": k, "x": x.tolist(), "residuo": res, "error_abs": err})
        if np.linalg.norm(x - old, ord=np.inf) <= tol and res <= max(tol, 1e-14):
            converged = True
            break
    return x, history, converged

def solve_lu(A, b, reference=None):
    start = time.perf_counter()
    lu, piv = lu_factor(np.asarray(A, float))
    x = lu_solve((lu, piv), np.asarray(b, float))
    elapsed = (time.perf_counter() - start) * 1000
    _, res = residual_metrics(A, b, x)
    err = error_metrics(reference, x)["error_absoluto_inf"] if reference is not None else None
    history = [{"iteracion": 1, "x": x.tolist(), "residuo": res, "error_abs": err}]
    return x, history, True, elapsed

def conjugate_gradient(A, b, tol=1e-8, max_iter=1000, x0=None, reference=None):
    A, b = np.asarray(A, float), np.asarray(b, float)
    if not np.allclose(A, A.T, atol=1e-12):
        raise ValueError("Gradiente conjugado estándar requiere matriz simétrica.")
    if np.min(np.linalg.eigvalsh(A)) <= 0:
        raise ValueError("Gradiente conjugado estándar requiere matriz definida positiva.")
    x = np.zeros_like(b) if x0 is None else np.asarray(x0, float).copy()
    r = b - A @ x
    p = r.copy()
    rsold = float(r @ r)
    history, converged = [], False
    for k in range(1, max_iter + 1):
        Ap = A @ p
        denom = float(p @ Ap)
        if abs(denom) < 1e-30:
            break
        alpha = rsold / denom
        x = x + alpha * p
        r = r - alpha * Ap
        rsnew = float(r @ r)
        _, res = residual_metrics(A, b, x)
        err = error_metrics(reference, x)["error_absoluto_inf"] if reference is not None else None
        history.append({"iteracion": k, "x": x.tolist(), "residuo": res, "error_abs": err})
        if np.sqrt(rsnew) <= tol and res <= max(tol, 1e-14):
            converged = True
            break
        p = r + (rsnew / rsold) * p
        rsold = rsnew
    return x, history, converged

def system_for_scenario(scenario):
    """Matriz SPD y solución conocida para los tres experimentos."""
    x_star = np.array([1.0, 2.0, -1.0, 2.0])
    if scenario == "NORMAL":
        A = np.array([[10., -1., 2., 0.],
                      [-1., 11., -1., 3.],
                      [2., -1., 10., -1.],
                      [0., 3., -1., 8.]])
        tol, max_iter = 1e-5, 2000
        description = "Matriz SPD de referencia, bien condicionada."
    elif scenario == "ESTRES":
        A = np.array([[10., -1., 2., 0.],
                      [-1., 11., -1., 3.],
                      [2., -1., 10., -1.],
                      [0., 3., -1., 8.]])
        tol, max_iter = 1e-9, 5000
        description = "Mayor exigencia de precisión: tolerancia más estricta y perturbación controlada en b."
    else:
        rho = 0.9999
        A = np.array([[1., rho, 0., 0.],
                      [rho, 1., 0., 0.],
                      [0., 0., 1., rho],
                      [0., 0., rho, 1.]])
        tol, max_iter = 1e-7, 2500
        description = "Matriz SPD casi singular por bloques; se espera alta sensibilidad y posible límite de iteraciones."
    b = A @ x_star
    if scenario == "ESTRES":
        b = b + np.array([1e-4, -1e-4, 2e-4, -2e-4])
        x_star = np.linalg.solve(A, b)  # referencia exacta del sistema perturbado
    return A, b, x_star, tol, max_iter, description

def run_linear_comparison(scenario):
    A, b, reference, tol, max_iter, description = system_for_scenario(scenario)
    results = {}
    for name, fn in [("Jacobi", jacobi), ("Gauss-Seidel", gauss_seidel)]:
        start = time.perf_counter()
        x, hist, conv = fn(A, b, tol=tol, max_iter=max_iter, reference=reference)
        elapsed = (time.perf_counter() - start) * 1000
        results[name] = pack_result(A, b, reference, x, hist, conv, elapsed)
    x, hist, conv, elapsed = solve_lu(A, b, reference)
    results["LU"] = pack_result(A, b, reference, x, hist, conv, elapsed)
    start = time.perf_counter()
    x, hist, conv = conjugate_gradient(A, b, tol=tol, max_iter=max_iter, reference=reference)
    elapsed = (time.perf_counter() - start) * 1000
    results["Gradiente conjugado"] = pack_result(A, b, reference, x, hist, conv, elapsed)
    return {
        "A": A, "b": b, "referencia": reference,
        "condicion_2": float(np.linalg.cond(A, 2)),
        "descripcion": description, "tolerancia": tol,
        "max_iter": max_iter, "resultados": results
    }

def pack_result(A, b, reference, x, history, converged, elapsed):
    _, res = residual_metrics(A, b, x)
    metrics = error_metrics(reference, x)
    return {
        "x": np.asarray(x).tolist(),
        "iteraciones": len(history),
        "residuo_inf": res,
        **metrics,
        "convergio": bool(converged),
        "tiempo_ms": float(elapsed),
        "historial": history
    }
