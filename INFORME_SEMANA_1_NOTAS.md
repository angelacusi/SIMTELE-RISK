# Notas para completar el informe de avance — Semana 1

## Ajuste del contexto

La consigna base presenta un sistema de transporte por cable inspirado en Mi Teleférico. Para contextualizar los casos en Bolivia, el equipo propone:

- Módulo 1: detención de cabinas de Mi Teleférico.
- Módulo 2: deterioro de bombas de agua potable.
- Módulo 3: oscilaciones por viento en cabinas de Mi Teleférico.
- Módulo 4: reconstrucción de sensores de nivel de agua en represas.

**Consultar con la docente** si se autoriza que los módulos 2 y 4 amplíen el contexto sectorial original del transporte por cable. La matemática requerida se conserva, pero cambia el fenómeno aplicado.

## Datos y supuestos

Todos los datos usados en la aplicación son sintéticos. No representan especificaciones de operación ni mediciones verificadas de Mi Teleférico, EPSAS o represas bolivianas.

## Pendientes antes de entregar

- Completar nombres y apellidos de todos los integrantes en la portada.
- Confirmar la fecha oficial de entrega.
- Ejecutar la aplicación en el equipo del grupo y tomar capturas reales.
- Ejecutar los tres escenarios y guardar los resultados.
- Verificar que las tablas del informe coincidan con la salida real del programa.
- Agregar el DER como figura en el PDF.
- Crear el repositorio remoto y subir el código.
- No presentar resultados numéricos de pruebas que no se hayan ejecutado y comprobado.

## Correcciones numéricas detectadas en el borrador recibido

La matriz 4x4 escrita en el informe y el vector de referencia x*=(1,2,-1,2)^T no producen el primer componente b1=10. Al multiplicar A·x*, se obtiene b=(6,28,-12,23)^T. El programa utiliza este vector consistente.

Además, el número de condición 2 de esa matriz es aproximadamente 2.36, no 1.8. Las iteraciones y errores deben tomarse de la ejecución real del programa con la tolerancia declarada; no copiar cifras preliminares que no coincidan con la corrida.
