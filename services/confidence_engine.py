"""
==========================================================
CONFIDENCE ENGINE
AI Invoice Extractor
Production Version 2.0
==========================================================
"""

from __future__ import annotations

import threading
import time

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict

from logger import logger

from config import (
    CONFIDENCE_WEIGHTS,
    INVOICE_FIELD_WEIGHTS,
    DEFAULT_FIELD_WEIGHT,
    CONFIDENCE_EXCELLENT_THRESHOLD,
    CONFIDENCE_HIGH_THRESHOLD,
    CONFIDENCE_MEDIUM_THRESHOLD,
    OVERALL_EXCELLENT_THRESHOLD,
    OVERALL_HIGH_THRESHOLD,
    AUTO_APPROVE_THRESHOLD,
    REVIEW_THRESHOLD,
    REVIEW_FIELD_THRESHOLD,
    HIGH_PRIORITY_THRESHOLD,
    CRITICAL_FIELDS,
)


# ==========================================================
# SERVICE INFO
# ==========================================================

SERVICE_NAME = "Confidence Engine"
SERVICE_VERSION = "2.0.0"


# ==========================================================
# DEFAULT RESULT
# ==========================================================

DEFAULT_RESULT = {
    "overall_confidence": 0.0,
    "field_confidence": {},
    "decision": "review",
}


# ==========================================================
# METRICS
# ==========================================================

@dataclass
class ConfidenceMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_processing_time: float = 0.0


# ==========================================================
# CONFIDENCE ENGINE
# ==========================================================

class ConfidenceEngine:
    """
    Production Confidence Engine.

    Responsibilities
    ----------------
    - OCR confidence
    - Rule confidence
    - Validation confidence
    - AI confidence
    - Field confidence
    - Overall document confidence
    - Business decision
    - Human-review classification
    - Runtime metrics
    """

    def __init__(self):

        self.lock = threading.Lock()
        self.metrics = ConfidenceMetrics()

        logger.info(
            "%s %s Initialized",
            SERVICE_NAME,
            SERVICE_VERSION,
        )


    # ======================================================
    # RESULT
    # ======================================================

    def empty_result(self) -> Dict[str, Any]:

        return deepcopy(
            DEFAULT_RESULT
        )


    # ======================================================
    # HEALTH
    # ======================================================

    def health(self) -> Dict[str, Any]:

        return {
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "status": "healthy",
            "metrics": self.get_metrics(),
        }


    # ======================================================
    # METRICS
    # ======================================================

    def get_metrics(self) -> Dict[str, Any]:

        average_processing_time = 0.0

        if self.metrics.successful_requests:

            average_processing_time = (
                self.metrics.total_processing_time
                /
                self.metrics.successful_requests
            )

        return {
            "requests": self.metrics.total_requests,
            "success": self.metrics.successful_requests,
            "failed": self.metrics.failed_requests,
            "average_processing_time": round(
                average_processing_time,
                3,
            ),
        }


    def reset_metrics(self):

        self.metrics = ConfidenceMetrics()

        logger.info(
            "Confidence metrics reset."
        )


    # ======================================================
    # SCORE NORMALIZATION
    # ======================================================

    def normalize_score(
        self,
        score,
    ) -> float:

        try:
            score = float(score)

        except (
            TypeError,
            ValueError,
        ):

            return 0.0

        return max(
            0.0,
            min(
                score,
                1.0,
            ),
        )


    # ======================================================
    # WEIGHTED SCORE
    # ======================================================

    def weighted_score(
        self,
        ocr=0.0,
        rule=0.0,
        validation=0.0,
        ai=0.0,
        weights=None,
    ) -> float:

        if weights is None:
            weights = CONFIDENCE_WEIGHTS

        ocr = self.normalize_score(
            ocr
        )

        rule = self.normalize_score(
            rule
        )

        validation = self.normalize_score(
            validation
        )

        ai = self.normalize_score(
            ai
        )

        score = (
            ocr * weights["ocr"]
            +
            rule * weights["rule"]
            +
            validation * weights["validation"]
            +
            ai * weights["ai"]
        )

        return round(
            score,
            3,
        )


    # ======================================================
    # EXPLAIN CONFIDENCE
    # ======================================================

    def explain_confidence(
        self,
        ocr,
        rule,
        validation,
        ai,
    ):

        final = self.weighted_score(
            ocr,
            rule,
            validation,
            ai,
        )

        return {
            "ocr": self.normalize_score(
                ocr
            ),
            "rule": self.normalize_score(
                rule
            ),
            "validation": self.normalize_score(
                validation
            ),
            "ai": self.normalize_score(
                ai
            ),
            "weights": deepcopy(
                CONFIDENCE_WEIGHTS
            ),
            "final": final,
        }


    # ======================================================
    # FIELD CONFIDENCE
    # ======================================================

    def calculate_field_confidence(
        self,
        field_name: str,
        field_value: Any,
        ocr_confidence: float = 0.0,
        rule_confidence: float = 0.0,
        validation_confidence: float = 0.0,
        ai_confidence: float = 0.0,
        weights: Dict[str, float] | None = None,
    ) -> Dict[str, Any]:
        """
        Calculate confidence for one extracted field.
        """

        final_score = self.weighted_score(
            ocr=ocr_confidence,
            rule=rule_confidence,
            validation=validation_confidence,
            ai=ai_confidence,
            weights=weights,
        )

        if (
            final_score
            >= CONFIDENCE_EXCELLENT_THRESHOLD
        ):

            level = "excellent"

        elif (
            final_score
            >= CONFIDENCE_HIGH_THRESHOLD
        ):

            level = "high"

        elif (
            final_score
            >= CONFIDENCE_MEDIUM_THRESHOLD
        ):

            level = "medium"

        else:

            level = "low"

        return {
            "field": field_name,
            "value": field_value,
            "confidence": final_score,
            "level": level,
            "sources": {
                "ocr": self.normalize_score(
                    ocr_confidence
                ),
                "rule": self.normalize_score(
                    rule_confidence
                ),
                "validation": self.normalize_score(
                    validation_confidence
                ),
                "ai": self.normalize_score(
                    ai_confidence
                ),
            },
            "weights": deepcopy(
                weights
                or CONFIDENCE_WEIGHTS
            ),
        }


    # ======================================================
    # MULTIPLE FIELDS
    # ======================================================

    def calculate_fields(
        self,
        invoice: Dict[str, Any],
        ocr_scores: Dict[str, float],
        rule_scores: Dict[str, float],
        validation_scores: Dict[str, float],
        ai_scores: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Calculate confidence for every invoice field.
        """

        results = {}

        for field, value in invoice.items():

            results[field] = (
                self.calculate_field_confidence(
                    field_name=field,
                    field_value=value,
                    ocr_confidence=ocr_scores.get(
                        field,
                        0.0,
                    ),
                    rule_confidence=rule_scores.get(
                        field,
                        0.0,
                    ),
                    validation_confidence=
                        validation_scores.get(
                            field,
                            0.0,
                        ),
                    ai_confidence=ai_scores.get(
                        field,
                        0.0,
                    ),
                )
            )

        return results


    # ======================================================
    # OVERALL CONFIDENCE
    # ======================================================

    def calculate_overall_confidence(
        self,
        field_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Calculate document confidence
        using configurable field weights.
        """

        weighted_sum = 0.0
        total_weight = 0.0
        missing_fields = []

        for field, result in field_results.items():

            if not isinstance(
                result,
                dict,
            ):

                continue

            confidence = result.get(
                "confidence",
                0.0,
            )

            weight = (
                INVOICE_FIELD_WEIGHTS.get(
                    field,
                    DEFAULT_FIELD_WEIGHT,
                )
            )

            if result.get(
                "value",
                "",
            ) == "":

                missing_fields.append(
                    field
                )

            weighted_sum += (
                confidence * weight
            )

            total_weight += weight

        if total_weight == 0:

            overall = 0.0

        else:

            overall = round(
                weighted_sum
                /
                total_weight,
                3,
            )

        if (
            overall
            >= OVERALL_EXCELLENT_THRESHOLD
        ):

            level = "excellent"

        elif (
            overall
            >= OVERALL_HIGH_THRESHOLD
        ):

            level = "high"

        elif overall >= REVIEW_THRESHOLD:

            level = "medium"

        else:

            level = "low"

        return {
            "overall_confidence": overall,
            "level": level,
            "missing_fields": missing_fields,
            "field_count": len(
                field_results
            ),
            "evaluated_fields": (
                len(field_results)
                -
                len(missing_fields)
            ),
        }


    # ======================================================
    # DECISION ENGINE
    # ======================================================

    def make_decision(
        self,
        field_results: Dict[str, Any],
        overall_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Enterprise Decision Engine.

        Decisions:
        - AUTO_APPROVE
        - HUMAN_REVIEW
        - REJECT
        """

        overall = overall_result.get(
            "overall_confidence",
            0.0,
        )

        reasons = []

        critical_ok = True

        for field in CRITICAL_FIELDS:

            info = field_results.get(
                field,
                {},
            )

            confidence = info.get(
                "confidence",
                0.0,
            )

            value = info.get(
                "value",
                "",
            )

            if (
                value == ""
                or
                confidence
                < REVIEW_FIELD_THRESHOLD
            ):

                critical_ok = False

                reasons.append(
                    f"{field} confidence too low."
                )

        if (
            overall
            >= AUTO_APPROVE_THRESHOLD
            and
            critical_ok
        ):

            decision = "AUTO_APPROVE"

        elif overall >= REVIEW_THRESHOLD:

            decision = "HUMAN_REVIEW"

        else:

            decision = "REJECT"

        return {
            "decision": decision,
            "overall_confidence": overall,
            "critical_fields_ok": critical_ok,
            "reasons": reasons,
        }


    # ======================================================
    # HUMAN REVIEW
    # ======================================================

    def generate_review(
        self,
        field_results: Dict[str, Any],
        decision_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate a human-friendly review report.
        """

        review_fields = []
        summary = []
        highest_risk = "LOW"

        for field, result in field_results.items():

            confidence = result.get(
                "confidence",
                0.0,
            )

            if (
                confidence
                >= REVIEW_FIELD_THRESHOLD
            ):

                continue

            priority = (
                "HIGH"
                if (
                    confidence
                    < HIGH_PRIORITY_THRESHOLD
                )
                else "MEDIUM"
            )

            if priority == "HIGH":

                highest_risk = "HIGH"

            elif (
                priority == "MEDIUM"
                and
                highest_risk != "HIGH"
            ):

                highest_risk = "MEDIUM"

            review_fields.append({
                "field": field,
                "value": result.get(
                    "value",
                    "",
                ),
                "confidence": confidence,
                "level": result.get(
                    "level",
                    "low",
                ),
                "priority": priority,
                "sources": result.get(
                    "sources",
                    {},
                ),
            })

            summary.append(
                f"{field} requires verification."
            )

        review_fields.sort(
            key=lambda item:
                item["confidence"]
        )

        return {
            "decision": decision_result.get(
                "decision",
                "HUMAN_REVIEW",
            ),
            "risk_level": highest_risk,
            "review_required": (
                len(review_fields) > 0
            ),
            "review_count": len(
                review_fields
            ),
            "review_fields": review_fields,
            "summary": summary,
        }


    # ======================================================
    # MASTER CONFIDENCE PIPELINE
    # ======================================================

    def evaluate(
        self,
        invoice: Dict[str, Any],
        ocr_scores: Dict[str, float],
        rule_scores: Dict[str, float],
        validation_scores: Dict[str, float],
        ai_scores: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Complete confidence evaluation pipeline.

        Pipeline:
        1. Field Confidence
        2. Overall Confidence
        3. Business Decision
        4. Human Review Report
        """

        start_time = time.perf_counter()

        with self.lock:

            self.metrics.total_requests += 1

        try:

            field_results = (
                self.calculate_fields(
                    invoice=invoice,
                    ocr_scores=ocr_scores,
                    rule_scores=rule_scores,
                    validation_scores=
                        validation_scores,
                    ai_scores=ai_scores,
                )
            )

            overall_result = (
                self.calculate_overall_confidence(
                    field_results
                )
            )

            decision_result = (
                self.make_decision(
                    field_results,
                    overall_result,
                )
            )

            review_result = (
                self.generate_review(
                    field_results,
                    decision_result,
                )
            )

            processing_time = round(
                time.perf_counter()
                -
                start_time,
                3,
            )

            result = {
                "success": True,
                "processing_time":
                    processing_time,
                "fields":
                    field_results,
                "overall":
                    overall_result,
                "decision":
                    decision_result,
                "review":
                    review_result,
            }

            with self.lock:

                self.metrics.successful_requests += 1
                self.metrics.total_processing_time += (
                    processing_time
                )

            return result

        except Exception as exc:

            logger.exception(
                "Confidence pipeline failed: %s",
                exc,
            )

            processing_time = round(
                time.perf_counter()
                -
                start_time,
                3,
            )

            with self.lock:

                self.metrics.failed_requests += 1
                self.metrics.total_processing_time += (
                    processing_time
                )

            result = self.empty_result()

            result.update({
                "success": False,
                "error": str(exc),
                "processing_time":
                    processing_time,
            })

            return result


    # ======================================================
    # SERVICE INFORMATION
    # ======================================================

    def info(self) -> Dict[str, Any]:
        """
        Return service information.
        """

        return {
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "healthy": True,
            "metrics": self.get_metrics(),
            "default_weights": deepcopy(
                CONFIDENCE_WEIGHTS
            ),
            "auto_approve_threshold":
                AUTO_APPROVE_THRESHOLD,
            "review_threshold":
                REVIEW_THRESHOLD,
        }


    # ======================================================
    # SELF TEST
    # ======================================================

    def self_test(self) -> Dict[str, Any]:
        """
        Execute a lightweight self-test.
        """

        try:

            sample_invoice = {
                "invoice_number": "INV-1001",
            }

            sample_scores = {
                "invoice_number": 1.0,
            }

            result = self.evaluate(
                invoice=sample_invoice,
                ocr_scores=sample_scores,
                rule_scores=sample_scores,
                validation_scores=sample_scores,
                ai_scores=sample_scores,
            )

            return {
                "success": result.get(
                    "success",
                    False,
                ),
                "service": SERVICE_NAME,
                "version": SERVICE_VERSION,
            }

        except Exception as exc:

            logger.exception(
                "Confidence self-test failed: %s",
                exc,
            )

            return {
                "success": False,
                "error": str(exc),
            }


    # ======================================================
    # RESET
    # ======================================================

    def reset(self):

        with self.lock:

            self.reset_metrics()

        logger.info(
            "%s reset completed.",
            SERVICE_NAME,
        )


    # ======================================================
    # SHUTDOWN
    # ======================================================

    def shutdown(self):

        logger.info(
            "%s shutting down.",
            SERVICE_NAME,
        )


    # ======================================================
    # CONTEXT MANAGER
    # ======================================================

    def __enter__(self):

        return self


    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):

        self.shutdown()

        return False


# ==========================================================
# SINGLETON
# ==========================================================

confidence_engine = ConfidenceEngine()


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [
    "ConfidenceEngine",
    "confidence_engine",
]