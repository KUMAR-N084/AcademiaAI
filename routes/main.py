from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
from services.ai_service import AIService
from services.pdf_service import generate_pdf
from models.history import History
from utils.validators import validate_question
import logging
import io
from urllib.parse import quote_plus

main_bp = Blueprint("main", __name__)
logger = logging.getLogger(__name__)
ai = AIService()


@main_bp.route("/")
@login_required
def index():
    return render_template("index.html", username=current_user.username)


@main_bp.route("/ask", methods=["POST"])
@login_required
def ask():
    try:
        data = request.get_json(silent=True) or {}
        question = data.get("question", "").strip()
        mode = data.get("mode", "explain")

        error = validate_question(question)
        if error:
            return jsonify({"error": error}), 400

        answer = ai.ask(question, mode)
        History.save(current_user.id, question, answer, mode)
        return jsonify({"answer": answer, "mode": mode})
    except RuntimeError as e:
        logger.warning(f"Ask provider error: {e}")
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        logger.exception("Ask error")
        return jsonify({"error": "AI service unavailable. Please try again."}), 500


@main_bp.route("/visualize", methods=["POST"])
@login_required
def visualize():
    try:
        data = request.get_json(silent=True) or {}
        topic = data.get("topic", "").strip()
        error = validate_question(topic)
        if error:
            return jsonify({"error": error}), 400

        graph, chart_b64 = ai.visualize(topic)
        return jsonify({"graph": graph, "chart": chart_b64})
    except RuntimeError as e:
        logger.warning(f"Visualize provider error: {e}")
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        logger.exception("Visualize error")
        return jsonify({"error": "Could not generate visualization."}), 500


@main_bp.route("/video", methods=["POST"])
@login_required
def video():
    data = request.get_json(silent=True) or {}
    topic = data.get("topic", "").strip()
    if not topic:
        return jsonify({"error": "Topic required."}), 400
    embed = f"https://www.youtube.com/embed?listType=search&list={quote_plus(topic)}"
    return jsonify({"embed": embed})


@main_bp.route("/history", methods=["GET"])
@login_required
def history():
    items = History.get_by_user(current_user.id)
    return jsonify({"history": items})


@main_bp.route("/history/<item_id>", methods=["DELETE"])
@login_required
def delete_history(item_id):
    ok = History.delete(current_user.id, item_id)
    status_code = 200 if ok else 404
    return jsonify({"success": ok}), status_code


@main_bp.route("/export/pdf", methods=["POST"])
@login_required
def export_pdf():
    try:
        data = request.get_json(silent=True) or {}
        question = data.get("question", "Question")
        answer = data.get("answer", "")
        if not answer:
            return jsonify({"error": "No content to export."}), 400

        pdf_bytes = generate_pdf(question, answer, current_user.username)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="academic_answer.pdf"
        )
    except Exception as e:
        logger.exception("PDF export error")
        return jsonify({"error": "Could not generate PDF."}), 500
