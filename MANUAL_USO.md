# PredictLab — Manual corto de uso

## 1. ¿Cómo lo corro en Visual Studio Code?

No necesita instalar nada. Tienes 2 opciones:

**Opción A (más fácil, doble clic):**
1. Abre la carpeta `cristian` en VS Code.
2. Clic derecho en `index.html` > `Open with Live Server` (si tienes la extensión Live Server) o solo haz doble clic en el archivo desde el explorador.

**Opción B (con comando, recomendada para que carguen los gráficos):**
1. En VS Code: `Terminal > New Terminal`.
2. Ejecuta:
```powershell
cd "C:\Users\Luna\Documents\cristian"
python -m http.server 5500
```
3. Abre en el navegador: `http://localhost:5500/index.html`

> Usa la Opción B si los puntos del gráfico no aparecen. Con `file://` el navegador bloquea el `fetch` de los CSV.

Para detener el servidor: `Ctrl + C` en la terminal.

## 2. ¿Cómo funciona el programa?

- `index.html`: toda la app (HTML + CSS + JS). Colores morado claro `#D8B4FE` + azul claro `#BAE6FD`.
- `dolar_data.csv`, `energia_data.csv`, `glucosa_data.csv`: datos para dibujar los puntos reales en el gráfico.
- Los modelos ya vienen entrenados en el JS (objeto `MODELS`) por mínimos cuadrados. No se entrena en cada clic, solo se aplica la fórmula → predicción instantánea.
- Si los CSV están junto al `index.html`, el canvas dibuja 300 puntos reales + la recta. Si no, dibuja solo la recta.

## 3. Regresión lineal simple (puntual)

Fórmula: `y = b0 + b1 * x` (una sola X).

- `b1`: cuánto sube `y` por cada unidad de `x`.
- `b0`: intercepto.
- `R²`: 0 a 1. Cerca de 1 = buen ajuste.

Ejemplos en la app:
- Dólar-Dia: `3959.73 + 4.99*Dia, R²=0.995`
- Energía-Temp: `154.64 + 9.84*Temp, R²=0.596`
- Glucosa-Edad: `79.12 + 1.23*Edad, R²=0.624`

**Uso:** Pestaña > modo `Simple` > elige X en el desplegable > mueve el slider > lee la predicción.

## 4. Regresión multilineal (puntual)

Fórmula: `y = b0 + b1*x1 + b2*x2 + ...` (varias X a la vez).

Capta efectos combinados. Normalmente tiene mayor `R²` que la simple.

Modelos en la app:
- Dólar: `3978.98 -338.06*Infl -2.53*Tasa +4.99*Dia, R²=0.995`
- Energía: `101.38 +9.96*Temp +5.01*Hora -3.08*DiaSem, R²=0.900`
- Glucosa: `66.31 +1.23*Edad +0.88*IMC -2.01*Act, R²=0.685`

**Uso:** Pestaña > modo `Múltiple` > mueve los 2-3 sliders > lee la predicción.
En Dólar activa `solo economía` para ver que sin `Dia` el `R²` cae a `0.006` (no predice).

## 5. Lectura rápida de resultados

- `R² > 0.8`: muy bueno (Dólar completo, Energía).
- `R² 0.6-0.8`: aceptable (Glucosa).
- `R² < 0.1`: esa X sola no sirve (Inflación y Tasa solas).
