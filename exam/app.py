import os
import uuid
import threading
import time

from flask import Flask, request, render_template, send_file, jsonify

from extractor import extract_page
from pdf_builder import build_pdf

app = Flask(__name__)
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

MAX_PAGES = 5


def _cleanup_loop():
    while True:
        time.sleep(300)
        now = time.time()
        for fname in os.listdir(RESULTS_DIR):
            path = os.path.join(RESULTS_DIR, fname)
            try:
                if os.path.isfile(path) and now - os.path.getmtime(path) > 1800:
                    os.remove(path)
            except OSError:
                pass


threading.Thread(target=_cleanup_loop, daemon=True).start()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    api_key = request.form.get("api_key", "").strip()
    if not api_key:
        return jsonify({"error": "API 키를 입력해 주세요."}), 400

    files = [f for f in request.files.getlist("images[]") if f.filename]

    if not files:
        return jsonify({"error": "이미지를 업로드해 주세요."}), 400
    if len(files) > MAX_PAGES:
        return jsonify({"error": f"최대 {MAX_PAGES}장까지 가능합니다."}), 400

    pages_data = []
    for idx, f in enumerate(files):
        img_bytes = f.read()
        if not img_bytes:
            return jsonify({"error": f"{idx + 1}번째 파일이 비어 있습니다."}), 400
        try:
            pages_data.append(extract_page(img_bytes, api_key))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:
            app.logger.exception("Extract failed page %d", idx + 1)
            return jsonify({"error": f"[{idx + 1}번째 이미지] {exc}"}), 500

    try:
        pdf_bytes = build_pdf(pages_data)
    except Exception as exc:
        app.logger.exception("PDF build failed")
        return jsonify({"error": f"PDF 생성 오류: {exc}"}), 500

    pdf_id = str(uuid.uuid4())
    with open(os.path.join(RESULTS_DIR, f"{pdf_id}.pdf"), "wb") as fp:
        fp.write(pdf_bytes)

    return jsonify({"download_id": pdf_id, "pages": len(pages_data)})


@app.route("/download/<pdf_id>")
def download(pdf_id):
    try:
        uuid.UUID(pdf_id)
    except ValueError:
        return "잘못된 요청", 400

    path = os.path.join(RESULTS_DIR, f"{pdf_id}.pdf")
    if not os.path.isfile(path):
        return "파일이 없거나 만료되었습니다.", 404

    return send_file(
        path,
        as_attachment=True,
        download_name="exam_original.pdf",
        mimetype="application/pdf",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5002)
