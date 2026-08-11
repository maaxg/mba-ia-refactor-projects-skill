"""Report routes. GET /reports/summary is guarded by require_admin (admin overview)."""
from flask import Blueprint

from controllers import report_controller
from middlewares.auth import require_admin

report_bp = Blueprint("reports", __name__)

report_bp.add_url_rule(
    "/reports/summary", "summary_report", require_admin(report_controller.summary_report), methods=["GET"]
)
report_bp.add_url_rule(
    "/reports/user/<int:user_id>", "user_report", report_controller.user_report, methods=["GET"]
)
