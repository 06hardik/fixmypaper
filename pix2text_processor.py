"""Helpers for extracting equation content from PDFs via Pix2Text.

This module is intentionally defensive because Pix2Text APIs can vary
between versions. It attempts a few common invocation styles and always
returns a stable result schema.
"""

from __future__ import annotations

import re
import tempfile
from typing import Any, Dict, List, Optional, Tuple

import fitz


MATH_TOKEN_RE = re.compile(r"[=+\-*/^×÷≤≥≈≠∑∫∂∇√π∞α-ωΑ-Ω]")
LATEX_COMMAND_RE = re.compile(
    r"\\(frac|dfrac|tfrac|sum|int|prod|sqrt|left|right|begin|end|mathbf|mathbb|cdot|times|tag|alpha|beta|gamma|delta|theta|lambda|mu|sigma|omega)"
)


def _looks_like_equation(text: str) -> bool:
    if not text:
        return False
    line = text.strip()
    if not line:
        return False
    if MATH_TOKEN_RE.search(line):
        return True
    if LATEX_COMMAND_RE.search(line):
        return True
    return bool(re.search(r"\([0-9]+\)\s*$", line))


def _looks_like_standalone_equation(text: str) -> bool:
    """Conservative filter for display equations from Pix2Text isolated blocks."""
    if not text:
        return False

    raw = text.strip()
    compact = re.sub(r"\s+", "", raw)
    if len(compact) < 3:
        return False

    if re.fullmatch(r"[A-Za-z]", compact):
        return False

    if LATEX_COMMAND_RE.search(raw):
        return True

    if re.search(r"\\tag\{\d+\}", raw):
        return True

    has_math_symbol = bool(re.search(r"[=+\-*/^_<>≤≥≈≠]", raw))
    has_alpha_num_mix = bool(re.search(r"[A-Za-z]", raw) and re.search(r"\d", raw))
    has_parenthesized_number = bool(re.search(r"\([0-9]+\)\s*$", raw))

    return has_math_symbol or has_alpha_num_mix or has_parenthesized_number


def _normalize_bbox(raw_bbox: Any, fallback: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
    if isinstance(raw_bbox, dict):
        keys = {"x0", "y0", "x1", "y1"}
        if keys.issubset(raw_bbox.keys()):
            return (
                float(raw_bbox["x0"]),
                float(raw_bbox["y0"]),
                float(raw_bbox["x1"]),
                float(raw_bbox["y1"]),
            )

    if isinstance(raw_bbox, (list, tuple)) and len(raw_bbox) >= 4:
        return (float(raw_bbox[0]), float(raw_bbox[1]), float(raw_bbox[2]), float(raw_bbox[3]))

    return fallback


def _position_to_bbox(raw_position: Any, fallback: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
    """Normalize Pix2Text position ([[x, y], ...]) into (x0, y0, x1, y1)."""
    if raw_position is None:
        return fallback

    if hasattr(raw_position, "tolist"):
        raw_position = raw_position.tolist()

    if isinstance(raw_position, (list, tuple)) and len(raw_position) >= 4:
        points = []
        for point in raw_position:
            if isinstance(point, (list, tuple)) and len(point) >= 2:
                try:
                    points.append((float(point[0]), float(point[1])))
                except (TypeError, ValueError):
                    continue

        if points:
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            return (min(xs), min(ys), max(xs), max(ys))

    return fallback


def _bbox_overlap_ratio(a: Dict[str, float], b: Dict[str, float]) -> float:
    ax0, ay0, ax1, ay1 = a["x0"], a["y0"], a["x1"], a["y1"]
    bx0, by0, bx1, by1 = b["x0"], b["y0"], b["x1"], b["y1"]

    ix0, iy0 = max(ax0, bx0), max(ay0, by0)
    ix1, iy1 = min(ax1, bx1), min(ay1, by1)
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0

    inter = (ix1 - ix0) * (iy1 - iy0)
    area_a = max(0.0, (ax1 - ax0) * (ay1 - ay0))
    area_b = max(0.0, (bx1 - bx0) * (by1 - by0))
    base = min(area_a, area_b)
    if base <= 0.0:
        return 0.0
    return inter / base


def _normalize_latex_for_dedupe(text: str) -> str:
    return re.sub(r"\s+", "", (text or "")).strip()


def _dedupe_equations(equations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for eq in equations:
        eq_bbox = eq.get("bbox", {})
        eq_page = eq.get("page")
        eq_latex = _normalize_latex_for_dedupe(str(eq.get("latex") or eq.get("text") or ""))

        is_duplicate = False
        for kept in out:
            if kept.get("page") != eq_page:
                continue
            kept_bbox = kept.get("bbox", {})
            overlap = _bbox_overlap_ratio(eq_bbox, kept_bbox)
            kept_latex = _normalize_latex_for_dedupe(str(kept.get("latex") or kept.get("text") or ""))
            if overlap >= 0.85 and (eq_latex == kept_latex or overlap >= 0.95):
                is_duplicate = True
                break

        if not is_duplicate:
            out.append(eq)

    for idx, eq in enumerate(out):
        eq["index"] = idx
    return out


def _extract_entries(raw: Any) -> List[Dict[str, Any]]:
    if raw is None:
        return []
    if isinstance(raw, list):
        out: List[Dict[str, Any]] = []
        for item in raw:
            out.extend(_extract_entries(item))
        return out
    if isinstance(raw, dict):
        nested_keys = ("results", "items", "blocks", "elements", "predictions", "pages")
        for key in nested_keys:
            if key in raw and isinstance(raw[key], (list, dict)):
                nested = _extract_entries(raw[key])
                if nested:
                    return nested
        return [raw]
    if isinstance(raw, str):
        return [{"text": raw}]
    return []


def _to_equation_record(
    item: Dict[str, Any],
    page_num: int,
    default_bbox: Tuple[float, float, float, float],
    index: int,
) -> Optional[Dict[str, Any]]:
    text = str(item.get("text") or item.get("latex") or item.get("content") or "").strip()
    latex = str(item.get("latex") or text).strip()
    kind = str(item.get("type") or item.get("kind") or "").lower()

    if kind and kind not in {"equation", "formula", "math", "isolated", "inline_formula"}:
        if not _looks_like_equation(latex):
            return None
    elif not _looks_like_equation(latex):
        return None

    bbox = _normalize_bbox(item.get("bbox") or item.get("position") or item.get("box"), default_bbox)
    confidence = item.get("confidence", item.get("score"))

    rec: Dict[str, Any] = {
        "index": index,
        "page": int(item.get("page", page_num)),
        "bbox": {"x0": bbox[0], "y0": bbox[1], "x1": bbox[2], "y1": bbox[3]},
        "type": "equation",
        "text": text,
        "latex": latex,
        "mathml": item.get("mathml"),
        "confidence": float(confidence) if isinstance(confidence, (int, float)) else None,
        "source": "pix2text",
    }
    return rec


def _build_text_formula_ocr() -> Any:
    """Build TextFormulaOCR using upstream-recommended config patterns."""
    from pix2text.text_formula_ocr import TextFormulaOCR  # type: ignore

    base_config = {
        "languages": ("en", "ch_sim"),
        "mfd": {
            "model_name": "mfd-1.5",
            "model_backend": "onnx",
        },
        "formula": {
            "model_name": "mfr-1.5",
            "model_backend": "onnx",
            "more_model_configs": {
                "provider": "CPUExecutionProvider",
            },
        },
    }

    for device in ("cpu", None):
        try:
            return TextFormulaOCR.from_config(
                total_configs=base_config,
                enable_formula=True,
                device=device,
            )
        except Exception as exc:
            print(f"[PIX2TEXT] TextFormulaOCR init failed for device={device}: {exc}")
            continue

    raise RuntimeError("Unable to initialize TextFormulaOCR")


def _recognize_page(text_formula_ocr: Any, image_path: str) -> Any:
    try:
        return text_formula_ocr.recognize(
            image_path,
            return_text=False,
            contain_formula=True,
            resized_shape=768,
            auto_line_break=False,
            mfr_batch_size=1,
        )
    except Exception as exc:
        print(f"[PIX2TEXT] recognize failed on {image_path}: {exc}")
        return None


def extract_equations_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """Extract equations from PDF using Pix2Text.

    Returns:
        {
          "equations": [...],
          "status": {
             "enabled": bool,
             "success": bool,
             "message": str,
             "count": int,
          }
        }
    """
    status = {
        "enabled": False,
        "success": False,
        "message": "Pix2Text not initialized",
        "count": 0,
    }

    try:
        from pix2text import Pix2Text  # type: ignore  # noqa: F401
    except Exception as exc:
        status["message"] = f"Pix2Text import failed: {exc}"
        return {"equations": [], "status": status}

    try:
        text_formula_ocr = _build_text_formula_ocr()
        status["enabled"] = True
    except Exception as exc:
        status["message"] = f"Pix2Text init failed: {exc}"
        return {"equations": [], "status": status}

    equations: List[Dict[str, Any]] = []
    next_index = 0

    page_errors = 0
    with fitz.open(pdf_path) as doc, tempfile.TemporaryDirectory() as tmpdir:
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_rect = page.rect
            fallback_bbox = (0.0, 0.0, float(page_rect.width), float(page_rect.height))

            pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0), alpha=False)
            img_path = f"{tmpdir}/page_{page_num}.png"
            pix.save(img_path)

            raw = _recognize_page(text_formula_ocr, img_path)
            if raw is None:
                page_errors += 1
                continue

            if not isinstance(raw, list):
                entries = _extract_entries(raw)
                for item in entries:
                    rec = _to_equation_record(item, page_num=page_num, default_bbox=fallback_bbox, index=next_index)
                    if rec is not None:
                        equations.append(rec)
                        next_index += 1
                continue

            for item in raw:
                if not isinstance(item, dict):
                    continue
                item_type = str(item.get("type") or "").lower()
                text = str(item.get("text") or "").strip()

                # Use Pix2Text's own isolated class as the primary equation signal.
                if item_type != "isolated":
                    continue

                if not _looks_like_standalone_equation(text):
                    continue

                bbox = _position_to_bbox(item.get("position"), fallback_bbox)
                score = item.get("score")
                equations.append(
                    {
                        "index": next_index,
                        "page": page_num,
                        "bbox": {
                            "x0": bbox[0],
                            "y0": bbox[1],
                            "x1": bbox[2],
                            "y1": bbox[3],
                        },
                        "type": "equation",
                        "text": text,
                        "latex": text,
                        "mathml": None,
                        "confidence": float(score) if isinstance(score, (int, float)) else None,
                        "source": "pix2text",
                        "equation_class": "isolated",
                    }
                )
                next_index += 1

    equations = _dedupe_equations(equations)
    status["count"] = len(equations)
    status["success"] = True
    if page_errors:
        status["message"] = f"Pix2Text extraction complete with {page_errors} page-level failures"
    else:
        status["message"] = "Pix2Text extraction complete"
    return {"equations": equations, "status": status}
