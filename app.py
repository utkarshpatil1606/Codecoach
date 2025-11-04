from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from analyzer import analyze_code, format_findings
import openai

app = Flask(__name__)
app.secret_key = "replace-this-with-a-secure-random-string"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_KEY:
    openai.api_key = OPENAI_KEY

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    uploaded = request.files.get("codefile")
    raw_code = request.form.get("raw_code")
    language = request.form.get("language") or "python"

    if not uploaded and not raw_code:
        flash("Upload a file or paste code into the editor.", "warning")
        return redirect(url_for("index"))

    if uploaded:
        filename = secure_filename(uploaded.filename)
        if filename == "":
            flash("Invalid filename.", "danger")
            return redirect(url_for("index"))
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded.save(save_path)
        with open(save_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
    else:
        code = raw_code

    local_findings = analyze_code(code, language=language)

    ai_analysis = None
    if OPENAI_KEY:
        try:
            prompt = (
                "You are a helpful code reviewer for students. Given the code below, "
                "provide summary, three suggestions, and one possible bug.\nCode:\n```" + code + "```"
            )
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role":"user", "content": prompt}],
                max_tokens=450,
                temperature=0.2,
            )
            ai_analysis = resp["choices"][0]["message"]["content"].strip()
        except Exception as e:
            ai_analysis = f"AI review failed: {e}"

    findings_text = format_findings(local_findings)

    return render_template("result.html",
                           code=code,
                           findings=findings_text,
                           ai_analysis=ai_analysis,
                           language=language)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
