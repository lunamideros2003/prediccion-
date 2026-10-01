import csv
import math
import pickle
import os

BASE = os.path.dirname(os.path.abspath(__file__))

def load_csv(path, features, target):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    X = [[float(r[c]) for c in features] for r in rows]
    y = [float(r[target]) for r in rows]
    return X, y

def train_ols(X, y):
    try:
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import mean_squared_error, r2_score
        model = LinearRegression()
        model.fit(X, y)
        yh = model.predict(X)
        mse = float(mean_squared_error(y, yh))
        rmse = float(math.sqrt(mse))
        r2 = float(r2_score(y, yh))
        return {
            "b0": float(model.intercept_),
            "coef": [float(c) for c in model.coef_],
            "mse": mse, "rmse": rmse, "r2": r2,
            "sklearn_model": model
        }
    except ImportError:
        n = len(y)
        p = len(X[0])
        XtX = [[0.0]*(p+1) for _ in range(p+1)]
        Xty = [0.0]*(p+1)
        for i in range(n):
            row = [1.0] + X[i]
            for a in range(p+1):
                Xty[a] += row[a]*y[i]
                for b in range(p+1):
                    XtX[a][b] += row[a]*row[b]
        M = [XtX[i][:]+[Xty[i]] for i in range(p+1)]
        N = p+1
        for i in range(N):
            piv = M[i][i]
            for r in range(i+1, N):
                if abs(M[r][i]) > abs(piv):
                    M[i], M[r] = M[r], M[i]
                    piv = M[i][i]
                    break
            for r in range(N):
                if r == i:
                    continue
                f = M[r][i]/piv
                for c in range(i, N+1):
                    M[r][c] -= f*M[i][c]
        coef_all = [M[i][N]/M[i][i] for i in range(N)]
        b0 = coef_all[0]
        coef = coef_all[1:]
        yh = [b0+sum(c*v for c, v in zip(coef, row)) for row in X]
        mse = sum((a-b)**2 for a, b in zip(y, yh))/n
        rmse = math.sqrt(mse)
        my = sum(y)/n
        ss_tot = sum((a-my)**2 for a in y)
        ss_res = sum((a-b)**2 for a, b in zip(y, yh))
        r2 = 1-ss_res/ss_tot
        return {"b0": b0, "coef": coef, "mse": mse, "rmse": rmse, "r2": r2, "sklearn_model": None}

def save_model(out_path, features, target, res):
    data = {
        "features": features,
        "target": target,
        "intercept": res["b0"],
        "coef": res["coef"],
        "mse": res["mse"],
        "rmse": res["rmse"],
        "r2": res["r2"]
    }
    if res["sklearn_model"] is not None:
        with open(out_path, "wb") as f:
            pickle.dump(res["sklearn_model"], f)
    else:
        with open(out_path, "wb") as f:
            pickle.dump(data, f)
    with open(out_path.replace(".pkl", "_coef.pkl"), "wb") as f:
        pickle.dump(data, f)
    return data

def scatter_png(csv_path, xcol, ycol, out_png, max_pts=400):
    try:
        from PIL import Image, ImageDraw
        with open(csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        step = max(1, len(rows)//max_pts)
        pts = [(float(r[xcol]), float(r[ycol])) for r in rows[::step]]
        W, H = 640, 420
        img = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(img)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        def X(v): return 50 + (v-xmin)/(xmax-xmin+1e-9)*(W-70)
        def Y(v): return H-40 - (v-ymin)/(ymax-ymin+1e-9)*(H-70)
        for x, y in pts:
            d.ellipse([X(x)-2, Y(y)-2, X(x)+2, Y(y)+2], fill=(168, 85, 247))
        d.text((50, 10), f"{xcol} vs {ycol}", fill=(60, 30, 120))
        img.save(out_png)
    except Exception as e:
        print("No se pudo graficar", out_png, e)

TASKS = [
    ("dolar", "dolar_data.csv", ["Inflacion", "Tasa_interes", "Dia"], "Precio_Dolar", "modelo_dolar.pkl"),
    ("glucosa", "glucosa_data.csv", ["Edad", "IMC", "Actividad_Fisica"], "Nivel_Glucosa", "modelo_glucosa.pkl"),
    ("energia", "energia_data.csv", ["Temperatura", "Hora", "Dia_Semana"], "Consumo_Energia", "modelo_energia.pkl"),
]

if __name__ == "__main__":
    for name, csvf, feats, targ, outm in TASKS:
        X, y = load_csv(os.path.join(BASE, csvf), feats, targ)
        res = train_ols(X, y)
        info = save_model(os.path.join(BASE, outm), feats, targ, res)
        print(f"{name}: y = {info['intercept']:.3f} + " + " + ".join(f"{c:.3f}*{f}" for c, f in zip(info['coef'], feats)))
        print(f"  MSE={info['mse']:.2f} RMSE={info['rmse']:.2f} R2={info['r2']:.4f}")
        for xc in feats:
            scatter_png(os.path.join(BASE, csvf), xc, targ, os.path.join(BASE, f"graf_{name}_{xc}.png"))
    print("Modelos exportados .pkl y graficas PNG generadas.")
