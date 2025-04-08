# User Behavior Pipeline - MercadoPago Challenge

Este proyecto consiste en el desarrollo de un pipeline de datos en Python que procesa eventos de interacción de usuarios en la app de MercadoPago.

El objetivo es construir un dataset enriquecido que sirva como base para entrenar un modelo de machine learning que prediga el orden óptimo de las Propuestas de Valor (Value Props) en el carrusel.

---

## 📊 Pipeline de procesamiento

El pipeline realiza las siguientes etapas:

1. **Carga de datos** desde tres fuentes:
   - `prints.json`: value props mostradas a usuarios
   - `taps.json`: value props clickeadas por usuarios
   - `pays.csv`: pagos realizados por los usuarios

2. **Preprocesamiento**:
   - Conversión de tipos (`fecha`, `int`, `string`)
   - Renombramiento de columnas
   - Eliminación de registros incompletos

3. **Enriquecimiento del dataset**:
   - Se filtran los prints de la última semana
   - Por cada print, se calculan las siguientes métricas en una ventana de 3 semanas anteriores:
     - Si se hizo click o no ese mismo día (`clicked`)
     - Número de veces que se mostró la misma `value_prop`
     - Número de clics en la misma `value_prop`
     - Cantidad de pagos asociados a esa `value_prop`
     - Total gastado en esa `value_prop`

4. **Exportación**:
   - El dataset enriquecido es exportado a `output/data_enrich.csv` listo para su uso en modelado.

---

## 🗃️ Estructura del proyecto

```
.
├── data/                # Archivos de entrada (.json, .csv)
├── logs/                # Logs de ejecución y errores
├── output/              # Dataset enriquecido generado
├── src/
│   ├── main.py          # Punto de entrada del pipeline
│   ├── pipeline.py      # Carga, limpieza y enriquecimiento
│   ├── utils.py         # Funciones auxiliares (logger, IO)
│   ├── config.py        # Configuración de rutas y parámetros
├── requirements.txt     # Dependencias del entorno
├── README.md            # Documentación del proyecto
```

---

## ⚙️ Requisitos

- Python 3.10+
- pandas

Puedes instalar las dependencias ejecutando:

```bash
pip install -r requirements.txt
```

---

## 🚀 Cómo ejecutar el pipeline

Desde la raíz del proyecto:

```bash
python src/main.py
```

Esto ejecutará todo el pipeline de carga, procesamiento, enriquecimiento y exportación de datos.

---

## 🧠 Decisiones técnicas

- Se utilizó `pandas` para un manejo eficiente de datos tabulares.
- Se evitó el uso de `apply` fila a fila en favor de `groupby` y `merge` para mejorar rendimiento.
- Se separó la lógica por etapas (`carga`, `preprocesamiento`, `enriquecimiento`, `exportación`).
- Se implementó `logging` profesional para seguimiento y debug.
- Todas las rutas y parámetros clave están centralizados en `config.py`.

---

## ✅ Estado

✔ Completado y probado localmente  
✔ Listo para ingestión por modelos de ML  
✔ Preparado para escalar o integrarse a pipelines mayores

---

## 📩 Autor

**Alexander Ladino**  
_Este proyecto fue desarrollado como parte de una prueba técnica._