"""Evaluation endpoints for Ninja API v1."""

# pylint: disable=duplicate-code

import logging
from typing import Optional

from django.core.paginator import EmptyPage, Paginator
from django.db import IntegrityError, transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from ninja import Query, Router
from ninja.errors import HttpError

from src.api.v1.pagination import build_page_link
from src.api.v1.schemas.evaluation import (
    CriterionScoreIn,
    EvaluationCriterionIn,
    EvaluationCriterionPatchIn,
    SupplierEvaluationIn,
    SupplierEvaluationPatchIn,
    serialize_evaluation_criterion,
    serialize_evaluation_history,
    serialize_evaluation_summary,
    serialize_supplier_evaluation,
    serialize_supplier_evaluation_detail,
)
from src.supplier.models.evaluation import (
    CriterionScore,
    EvaluationCriterion,
    SupplierEvaluation,
)

logger = logging.getLogger(__name__)

router = Router(tags=["evaluation"])


def _normalize_evaluation_data(data: dict) -> dict:
    normalized = data.copy()
    if "supplier" in normalized:
        normalized["supplier_id"] = normalized.pop("supplier")
    if "period" in normalized:
        normalized["period_id"] = normalized.pop("period")
    return normalized


def _normalize_score_data(score_data: list[dict]) -> list[dict]:
    normalized = []
    for item in score_data:
        score_item = item.copy()
        if "criterion" in score_item:
            score_item["criterion_id"] = score_item.pop("criterion")
        normalized.append(score_item)
    return normalized


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
    criterion = EvaluationCriterion.objects.create(**payload.model_dump(by_alias=False))
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
    period: Optional[int] = None,
    year: Optional[int] = None,
):
    """List supplier evaluations with filters and pagination."""
    queryset = SupplierEvaluation.objects.select_related("supplier", "period").all()
    if supplier is not None:
        queryset = queryset.filter(supplier_id=supplier)
    if period is not None:
        queryset = queryset.filter(period_id=period)
    if year is not None:
        queryset = queryset.filter(period__year=year)
    queryset = queryset.order_by("-evaluation_date", "-id")
    return _paginate(request, queryset, page, size, serialize_supplier_evaluation)


@router.post("/evaluations/", url_name="evaluation-create-v1")
def create_evaluation(request, payload: SupplierEvaluationIn):
    """Create a supplier evaluation and optional criterion scores."""
    data = _normalize_evaluation_data(
        payload.model_dump(by_alias=False, exclude_none=True)
    )
    scores = _normalize_score_data(data.pop("criterion_scores", None) or [])
    try:
        with transaction.atomic():
            evaluation = SupplierEvaluation.objects.create(**data)
            CriterionScore.objects.bulk_create(
                [CriterionScore(evaluation=evaluation, **score) for score in scores]
            )
            evaluation.save()
    except IntegrityError as exc:
        logger.exception("Falha ao criar avaliacao de fornecedor")
        raise HttpError(400, {"detail": "Dados de avaliacao invalidos."}) from exc
    return JsonResponse(serialize_supplier_evaluation(evaluation), status=201)


@router.get("/evaluations/{pk}/", url_name="evaluation-detail-v1")
def get_evaluation(request, pk: int):
    """Retrieve one supplier evaluation with details."""
    evaluation = get_object_or_404(
        SupplierEvaluation.objects.select_related("supplier", "period"), pk=pk
    )
    return serialize_supplier_evaluation_detail(evaluation)


@router.put("/evaluations/{pk}/", url_name="evaluation-update-v1")
def put_evaluation(request, pk: int, payload: SupplierEvaluationIn):
    """Update a supplier evaluation."""
    evaluation = get_object_or_404(SupplierEvaluation, pk=pk)
    data = _normalize_evaluation_data(
        payload.model_dump(by_alias=False, exclude_none=True)
    )
    scores = data.pop("criterion_scores", None)
    for key, value in data.items():
        setattr(evaluation, key, value)
    if scores is not None:
        scores = _normalize_score_data(scores)
        evaluation.criterion_scores.all().delete()
        CriterionScore.objects.bulk_create(
            [CriterionScore(evaluation=evaluation, **score) for score in scores]
        )
    evaluation.save()
    return serialize_supplier_evaluation(evaluation)


@router.patch("/evaluations/{pk}/", url_name="evaluation-partial-v1")
def patch_evaluation(request, pk: int, payload: SupplierEvaluationPatchIn):
    """Partially update a supplier evaluation."""
    evaluation = get_object_or_404(SupplierEvaluation, pk=pk)
    data = _normalize_evaluation_data(
        payload.model_dump(by_alias=False, exclude_unset=True)
    )
    scores = data.pop("criterion_scores", None)
    for key, value in data.items():
        setattr(evaluation, key, value)
    if scores is not None:
        scores = _normalize_score_data(scores)
        evaluation.criterion_scores.all().delete()
        CriterionScore.objects.bulk_create(
            [CriterionScore(evaluation=evaluation, **score) for score in scores]
        )
    evaluation.save()
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
    queryset = SupplierEvaluation.objects.select_related("supplier", "period").all()
    return [serialize_evaluation_summary(item) for item in queryset]


@router.get("/supplier-history/", url_name="evaluation-supplier-history-v1")
def supplier_history(request, supplier: Optional[int] = None):
    """Return evaluation history for a supplier."""
    if not supplier:
        raise HttpError(400, {"message": "É necessário fornecer um ID de fornecedor."})
    queryset = (
        SupplierEvaluation.objects.select_related("period")
        .filter(supplier_id=supplier)
        .order_by("-evaluation_date")
    )
    return [serialize_evaluation_history(item) for item in queryset]


@router.post(
    "/evaluations/{evaluation_id}/scores/", url_name="evaluation-add-scores-v1"
)
def add_criterion_scores(request, evaluation_id: int, payload: list[CriterionScoreIn]):
    """Append criterion scores to an existing evaluation."""
    evaluation = get_object_or_404(SupplierEvaluation, pk=evaluation_id)
    for score in payload:
        score_data = _normalize_score_data([score.model_dump(by_alias=False)])[0]
        CriterionScore.objects.create(
            evaluation=evaluation,
            **score_data,
        )
    evaluation.save()
    return JsonResponse(serialize_supplier_evaluation_detail(evaluation), status=201)
