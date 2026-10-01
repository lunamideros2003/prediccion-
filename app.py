from flask import Flask, request, render_template_string
import pickle
import os
BASE = os.path.dirname(os.path.abspath(__file__))
def load(name):
    with open(os.path.join(BASE, name), "rb") as f:
        m = pickle.load(f)
    if hasattr(m, "predict"):
        return {"sk": m}
    return m
try:
    MD = load("modelo_dolar_coef.pkl")
    MG = load("modelo_glucosa_coef.pkl")
    ME = load("modelo_energia_coef.pkl")
except Exception:
    MD = {"intercept": 3978.984617, "coef": [-338.059761, -2.532823, 4.99906]}
    MG = {"intercept": 66.314991, "coef": [1.233681, 0.883236, -2.010386]}
    ME = {"intercept": 101.38299, "coef": [9.965998, 5.01176, -3.08917]}
app = Flask(__name__)
HTML = """
<h2>PredictLab - Dolar / Glucosa / Energia</h2>
<form method="post">
<select name="ej">
<option value="dolar">Dolar</option>
<option value="glucosa">Glucosa</option>
<option value="energia">Energia</option>
</select><br>
X1: <input name="x1" type="number" step="any" required>
X2: <input name="x2" type="number" step="any" required>
X3: <input name="x3" type="number" step="any" required>
<button>Predecir</button>
</form>
{% if pred %}<h3>Prediccion: {{pred}}</h3>{% endif %}
<p>Dolar: Inflacion,Tasa,Dia | Glucosa: Edad,IMC,Act | Energia: Temp,Hora,DiaSem</p>
"""
def calc(d, x):
    return d["intercept"] + sum(c*v for c, v in zip(d["coef"], x))
@app.route("/", methods=["GET", "POST"])
def index():
    pred = None
    if request.method == "POST":
        x = [float(request.form["x1"]), float(request.form["x2"]), float(request.form["x3"])]
        ej = request.form["ej"]
        if ej == "dolar":
            pred = calc(MD, x)
        elif ej == "glucosa":
            pred = calc(MG, x)
        else:
            pred = calc(ME, x)
        pred = round(pred, 2)
    return render_template_string(HTML, pred=pred)
if __name__ == "__main__":
    app.run(debug=True)
