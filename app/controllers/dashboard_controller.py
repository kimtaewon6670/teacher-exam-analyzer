from __future__ import annotations

from typing import Any

from app.controllers.analysis_controller import AnalysisController
from app.services.analysis_service import AnalysisService


class DashboardController(AnalysisController):
    """Controller facade for the dashboard screen.

    The dashboard uses the same graded-result statistics as the analysis screen,
    but exposes the intent with a dashboard-specific controller name.
    """

    def __init__(self, view: Any, analysis_service: AnalysisService | None = None) -> None:
        super().__init__(view, analysis_service, attach_dashboard=False)
