"""Evaluation endpoints for Ninja API v1."""

# pylint: disable=duplicate-code

import json
from typing import Optional

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.paginator import EmptyPage, Paginator
from django.db import IntegrityError, transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from loguru import logger
from ninja import Query, Router
from ninja.errors import HttpError
from src.api.v1.pagination import build_page_link
from src.api.v1.schemas.evaluation import (
    CriterionScoreIn, EvaluationCriterionIn, EvaluationCriterionPatchIn,
    SupplierEvaluationIn, SupplierEvaluationPatchIn,
    serialize_evaluation_criterion, serialize_evaluation_history,
    serialize_evaluation_summary, serialize_supplier_evaluation,
    serialize_supplier_evaluation_detail)
from src.supplier.models.evaluation import (MIXED_PERIOD_TYPE_ERROR,
                                            CriterionScore,
                                            EvaluationCriterion,
                                            EvaluationPeriodType,
                                            SupplierEvaluation)

router = Router(tags=["evaluation"])

DUPLICATE_PERIOD_ERROR = (
    "Já existe uma avaliação para este fornecedor no período selecionado."
)
INVALID_PERIOD_ERROR = "Combinação inválida para tipo e número do período."


def _normalize_evaluation_data(data: dict) -> dict:
    normalized = data.copy()
    if "supplier" in normalized:
        normalized["supplier_id"] = normalized.pop("supplier")
    return normalized


def _normalize_score_data(score_data: list[dict]) -> list[dict]:
    normalized = []
    for item in score_data:
        score_item = item.copy()
        if "criterion" in score_item:
            score_item["criterion_id"] = score_item.pop("criterion")
        normalized.append(score_item)
    return normalized


def _validate_period_payload(data: dict) -> None:
    period_type = data.get("period_type")
    period_number = data.get("period_number")

    if period_type is None or period_number is None:
        return

    if (
        period_type == EvaluationPeriodType.QUADRIMESTER
        and period_number in [1, 2, 3]
    ):
        return
    if period_type == EvaluationPeriodType.SEMESTER and period_number in [1, 2]:
        return

    raise HttpError(400, INVALID_PERIOD_ERROR)


def _parse_supplier_evaluation_payload(payload: dict, partial: bool = False):
    schema = SupplierEvaluationPatchIn if partial else SupplierEvaluationIn
    # ValidationError → handler em exceptions.py
    parsed = schema.model_validate(payload)

    parsed_data = parsed.model_dump(
        by_alias=False, exclude_none=not partial, exclude_unset=partial
    )
    _validate_period_payload(parsed_data)
    return parsed


def _extract_json_payload(request) -> dict:
    """Extract JSON body payload from request."""
    raw_body = request.body.decode("utf-8") if request.body else ""
    if not raw_body:
        return {}

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise HttpError(400, "JSON invalido.") from exc

    if not isinstance(payload, dict):
        raise HttpError(400, "Payload deve ser um objeto JSON.")

    return payload


def _serialize_integrity_error(error: IntegrityError) -> str:
    error_text = str(error).lower()
    # PostgreSQL: named constraint in error
    if "supplier_eval_supplier_year_type_number_uniq" in error_text:
        return DUPLICATE_PERIOD_ERROR
    if "supplier_eval_year_cycle_unique" in error_text:
        return str(MIXED_PERIOD_TYPE_ERROR)
    if "supplier_eval_period_type_valid" in error_text:
        return INVALID_PERIOD_ERROR
    if "supplier_eval_period_number_by_type_valid" in error_text:
        return INVALID_PERIOD_ERROR
    # SQLite: column names instead of named constraints
    if (
        "supplier_evaluation.supplier_id" in error_text
        and "supplier_evaluation.period_type" in error_text
        and "supplier_evaluation.period_number" in error_text
    ):
        return DUPLICATE_PERIOD_ERROR
    if "supplier_evaluation_year_cycle" in error_text:
        return str(MIXED_PERIOD_TYPE_ERROR)
    return "Dados de avaliacao invalidos."


def _check_duplicate_evaluation(
    supplier_id: int,
    evaluation_year: int,
    period_type: str,
    period_number: int,
    exclude_pk: Optional[int] = None,
) -> None:
    """Raise HttpError 400 if an evaluation already exists for this supplier/year/period."""
    qs = SupplierEvaluation.objects.filter(
        supplier_id=supplier_id,
        evaluation_year=evaluation_year,
        period_type=period_type,
        period_number=period_number,
    )
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    if qs.exists():
        raise HttpError(400, DUPLICATE_PERIOD_ERROR)


def _paginate(request, queryset, page: int, size: int, serializer_fn):
    paginator = Paginator(queryset, size)
    try:
        current_page = paginator.page(page)
    except EmptyPage:
        current_page = (
            paginator.page(paginator.num_pages) if paginator.num_pages else []
        )

    results = (
        [serializer_fn(item) for item in current_page.object_list]
        if paginator.count
        else []
    )

    return {
        "count": paginator.count,
        "next": (
            build_page_link(
                request,
                current_page.next_page_number() if current_page.has_next() else None,
                size,
            )
            if paginator.count
            else None
        ),
        "previous": (
            build_page_link(
                request,
                (
                    current_page.previous_page_number()
                    if current_page.has_previous()
                    else None
                ),
                size,
            )
            if paginator.count
            else None
        ),
        "results": results,
    }


@router.get("/criteria-list/", url_name="evaluation-criteria-list-v1")
def list_criteria(
    request, page: int = Query(1, ge=1), size: int = Query(12, ge=1, le=100)
):
    """List evaluation criteria with pagination."""
    queryset = EvaluationCriterion.objects.all().order_by("order")
    return _paginate(request, queryset, page, size, serialize_evaluation_criterion)


@router.post("/criteria/", url_name="evaluation-criteria-create-v1")
def create_criterion(request, payload: EvaluationCriterionIn):
    """Create a new evaluation criterion."""
    criterion = EvaluationCriterion.objects.create(
        **payload.model_dump(by_alias=False))
    return JsonResponse(serialize_evaluation_criterion(criterion), status=201)


@router.get("/criteria/{pk}/", url_name="evaluation-criteria-detail-v1")
def get_criterion(request, pk: int):
    """Retrieve one evaluation criterion."""
    criterion = get_object_or_404(EvaluationCriterion, pk=pk)
    return serialize_evaluation_criterion(criterion)


@router.put("/criteria/{pk}/", url_name="evaluation-criteria-update-v1")
def put_criterion(request, pk: int, payload: EvaluationCriterionIn):
    """Update one evaluation criterion."""
    criterion = get_object_or_404(EvaluationCriterion, pk=pk)
    for key, value in payload.model_dump(by_alias=False).items():
        setattr(criterion, key, value)
    criterion.save()
    return serialize_evaluation_criterion(criterion)


@router.patch("/criteria/{pk}/", url_name="evaluation-criteria-partial-v1")
def patch_criterion(request, pk: int, payload: EvaluationCriterionPatchIn):
    """Partially update one evaluation criterion."""
    criterion = get_object_or_404(EvaluationCriterion, pk=pk)
    for key, value in payload.model_dump(by_alias=False, exclude_unset=True).items():
        setattr(criterion, key, value)
    criterion.save()
    return serialize_evaluation_criterion(criterion)


@router.delete("/criteria/{pk}/", url_name="evaluation-criteria-delete-v1")
def delete_criterion(request, pk: int):
    """Delete one evaluation criterion."""
    criterion = get_object_or_404(EvaluationCriterion, pk=pk)
    criterion.delete()
    return HttpResponse(status=204)


@router.get("/evaluations-list/", url_name="evaluation-list-v1")
# pylint: disable=too-many-positional-arguments
def list_evaluations(
    request,
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
    supplier: Optional[int] = None,
    evaluation_year: Optional[int] = Query(None, alias="evaluationYear"),
    period_type: Optional[str] = Query(None, alias="periodType"),
    period_number: Optional[int] = Query(None, alias="periodNumber"),
):
    """List supplier evaluations with filters and pagination."""
    queryset = SupplierEvaluation.objects.select_related("supplier").all()
    if supplier is not None:
        queryset = queryset.filter(supplier_id=supplier)
    if evaluation_year is not None:
        queryset = queryset.filter(evaluation_year=evaluation_year)
    if period_type is not None:
        queryset = queryset.filter(period_type=period_type)
    if period_number is not None:
        queryset = queryset.filter(period_number=period_number)
    queryset = queryset.order_by(
        "-evaluation_year",
        "period_type",
        "-period_number",
        "-evaluation_date",
        "-id",
    )
    return _paginate(request, queryset, page, size, serialize_supplier_evaluation)


@router.post("/evaluations/", url_name="evaluation-create-v1")
def create_evaluation(request):
    """Create a supplier evaluation and optional criterion scores."""
    payload = _extract_json_payload(request)
    validated_payload = _parse_supplier_evaluation_payload(payload)
    data = _normalize_evaluation_data(
        validated_payload.model_dump(by_alias=False, exclude_none=True)
    )
    scores = _normalize_score_data(data.pop("criterion_scores", None) or [])
    _check_duplicate_evaluation(
        supplier_id=data["supplier_id"],
        evaluation_year=data["evaluation_year"],
        period_type=data["period_type"],
        period_number=data["period_number"],
    )
    try:
        with transaction.atomic():
            evaluation = SupplierEvaluation.objects.create(**data)
            CriterionScore.objects.bulk_create(
                [CriterionScore(evaluation=evaluation, **score)
                 for score in scores]
            )
            evaluation.save()
    except (IntegrityError, DjangoValidationError) as exc:
        logger.exception("Falha ao criar avaliacao de fornecedor")
        if isinstance(exc, DjangoValidationError):
            detail = (
                exc.message_dict.get(
                    "period_type", [str(MIXED_PERIOD_TYPE_ERROR)])[0]
                if hasattr(exc, "message_dict")
                else str(exc)
            )
            raise HttpError(400, detail) from exc
        raise HttpError(400, _serialize_integrity_error(exc)) from exc
    return JsonResponse(serialize_supplier_evaluation(evaluation), status=201)


@router.get("/evaluations/{pk}/", url_name="evaluation-detail-v1")
def get_evaluation(request, pk: int):
    """Retrieve one supplier evaluation with details."""
    evaluation = get_object_or_404(
        SupplierEvaluation.objects.select_related("supplier"), pk=pk
    )
    return serialize_supplier_evaluation_detail(evaluation)


@router.put("/evaluations/{pk}/", url_name="evaluation-update-v1")
def put_evaluation(request, pk: int):
    """Update a supplier evaluation."""
    payload = _extract_json_payload(request)
    evaluation = get_object_or_404(SupplierEvaluation, pk=pk)
    validated_payload = _parse_supplier_evaluation_payload(payload)
    data = _normalize_evaluation_data(
        validated_payload.model_dump(by_alias=False, exclude_none=True)
    )
    scores = data.pop("criterion_scores", None)
    _check_duplicate_evaluation(
        supplier_id=data.get("supplier_id", evaluation.supplier_id),
        evaluation_year=data.get(
            "evaluation_year", evaluation.evaluation_year),
        period_type=data.get("period_type", evaluation.period_type),
        period_number=data.get("period_number", evaluation.period_number),
        exclude_pk=pk,
    )
    for key, value in data.items():
        setattr(evaluation, key, value)
    if scores is not None:
        scores = _normalize_score_data(scores)
        evaluation.criterion_scores.all().delete()
        CriterionScore.objects.bulk_create(
            [CriterionScore(evaluation=evaluation, **score)
             for score in scores]
        )
    try:
        evaluation.save()
    except (IntegrityError, DjangoValidationError) as exc:
        if isinstance(exc, DjangoValidationError):
            detail = (
                exc.message_dict.get(
                    "period_type", [str(MIXED_PERIOD_TYPE_ERROR)])[0]
                if hasattr(exc, "message_dict")
                else str(exc)
            )
            raise HttpError(400, detail) from exc
        raise HttpError(400, _serialize_integrity_error(exc)) from exc
    return serialize_supplier_evaluation(evaluation)


@router.patch("/evaluations/{pk}/", url_name="evaluation-partial-v1")
def patch_evaluation(request, pk: int):
    """Partially update a supplier evaluation."""
    payload = _extract_json_payload(request)
    evaluation = get_object_or_404(SupplierEvaluation, pk=pk)
    validated_payload = _parse_supplier_evaluation_payload(
        payload, partial=True)
    data = _normalize_evaluation_data(
        validated_payload.model_dump(by_alias=False, exclude_unset=True)
    )
    scores = data.pop("criterion_scores", None)
    for key, value in data.items():
        setattr(evaluation, key, value)
    _check_duplicate_evaluation(
        supplier_id=evaluation.supplier_id,
        evaluation_year=evaluation.evaluation_year,
        period_type=evaluation.period_type,
        period_number=evaluation.period_number,
        exclude_pk=pk,
    )
    if scores is not None:
        scores = _normalize_score_data(scores)
        evaluation.criterion_scores.all().delete()
        CriterionScore.objects.bulk_create(
            [CriterionScore(evaluation=evaluation, **score)
             for score in scores]
        )
    try:
        evaluation.save()
    except (IntegrityError, DjangoValidationError) as exc:
        if isinstance(exc, DjangoValidationError):
            detail = (
                exc.message_dict.get(
                    "period_type", [str(MIXED_PERIOD_TYPE_ERROR)])[0]
                if hasattr(exc, "message_dict")
                else str(exc)
            )
            raise HttpError(400, detail) from exc
        raise HttpError(400, _serialize_integrity_error(exc)) from exc
    return serialize_supplier_evaluation(evaluation)


@router.delete("/evaluations/{pk}/", url_name="evaluation-delete-v1")
def delete_evaluation(request, pk: int):
    """Delete a supplier evaluation."""
    evaluation = get_object_or_404(SupplierEvaluation, pk=pk)
    evaluation.delete()
    return HttpResponse(status=204)


@router.get("/summary/", url_name="evaluation-summary-v1")
def evaluation_summary(request):
    """Return evaluation summary list."""
    queryset = SupplierEvaluation.objects.select_related("supplier").all()
    return [serialize_evaluation_summary(item) for item in queryset]


@router.get("/supplier-history/", url_name="evaluation-supplier-history-v1")
def supplier_history(request, supplier: Optional[int] = None):
    """Return evaluation history for a supplier."""
    if not supplier:
        raise HttpError(400, "É necessário fornecer um ID de fornecedor.")
    queryset = (
        SupplierEvaluation.objects.select_related("supplier")
        .filter(supplier_id=supplier)
        .order_by(
            "-evaluation_year",
            "period_type",
            "-period_number",
            "-evaluation_date",
            "-id",
        )
    )
    return [serialize_evaluation_history(item) for item in queryset]


@router.post(
    "/evaluations/{evaluation_id}/scores/", url_name="evaluation-add-scores-v1"
)
def add_criterion_scores(request, evaluation_id: int, payload: list[CriterionScoreIn]):
    """Append criterion scores to an existing evaluation."""
    evaluation = get_object_or_404(SupplierEvaluation, pk=evaluation_id)
    for score in payload:
        score_data = _normalize_score_data(
            [score.model_dump(by_alias=False)])[0]
        CriterionScore.objects.create(
            evaluation=evaluation,
            **score_data,
        )
    evaluation.save()
    return JsonResponse(serialize_supplier_evaluation_detail(evaluation), status=201)
