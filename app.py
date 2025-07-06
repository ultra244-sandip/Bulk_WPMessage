from flask import Flask, render_template, request
import pandas as pd
import re
from urllib.parse import quote

app = Flask(__name__, static_folder="static")

def normalize_phone(raw, default_cc="91"):
    s = str(raw).strip()
    digits = re.sub(r"\D+", "", s)
    if re.fullmatch(r"[6-9]\d{9}", digits):
        return default_cc + digits
    if re.fullmatch(default_cc + r"[6-9]\d{9}", digits):
        return digits
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    links = []
    error = None

    if request.method == "POST":
        template = request.form.get("template", "").strip()
        file      = request.files.get("datafile")
        filename  = file.filename.lower()

        try:
            if filename.endswith((".xls", ".xlsx")):
                engine = "openpyxl" if filename.endswith("xlsx") else "xlrd"
                df = pd.read_excel(file, dtype=str, engine=engine)
            elif filename.endswith(".csv"):
                df = pd.read_csv(file, dtype=str)
            else:
                raise ValueError("Unsupported filetype")
        except Exception as e:
            error = f"Could not read file: {e}"
            return render_template("index.html", error=error)
        for _, row in df.iterrows():
                name = row.get("Name", "").strip()
                raw  = row.get("Phone", "").strip()
                phone = normalize_phone(raw)

                if phone:
                    msg = template.format(name=name)
                    url = f"https://wa.me/{phone}?text={quote(msg)}"
                    links.append({"name": name, "phone": phone, "url": url})
                else:
                    links.append({"name": name, "phone": raw, "url": None})

    return render_template("index.html", links=links, error=error)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
