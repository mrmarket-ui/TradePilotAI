from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from models.user import User

from dependencies.subscription import (
    require_premium_plan,
)

from schemas.macro_intelligence import (
    DirectionalBiasResponse,
    MacroScoreComponentResponse,
    MarketDirectionalBiasResponse,
    NFPMultimodalAnalysisResponse,
    NFPAnalysisRequest,
    NFPAnalysisResponse,
    NFPExtractedEvidenceResponse,
    NFPTextAnalysisRequest,
    NFPTextAnalysisResponse,
    GeneralMacroAnalysisResponse,
)

from services.macro_intelligence import (
    NFPInput,
    analyze_directional_bias,
    analyze_nfp,
)

from services.macro_intelligence.nfp_extractor import (
    extract_nfp_from_evidence,
    extract_nfp_from_sources,
    extract_general_macro_from_sources,
    extract_nfp_from_text,
)


router = APIRouter(
    prefix="/macro",
    tags=["Macro Intelligence"],
)


@router.post(
    "/analyze/nfp",
    response_model=NFPAnalysisResponse,
)
def analyze_nfp_release(
    payload: NFPAnalysisRequest,
    current_user: User = Depends(
        require_premium_plan,
    ),
) -> NFPAnalysisResponse:
    """
    Analyse a US Non-Farm Payrolls release.

    Premium access is enforced server-side.

    The endpoint interprets the economic release
    itself. It does not predict asset direction.
    """

    # Dependency is intentionally retained even
    # though the user object is not otherwise needed.
    # It guarantees Premium access server-side.
    _ = current_user

    analysis = analyze_nfp(
        NFPInput(
            nfp_actual=payload.nfp_actual,
            nfp_forecast=payload.nfp_forecast,
            nfp_previous=payload.nfp_previous,
            nfp_revised_previous=(
                payload.nfp_revised_previous
            ),
            unemployment_actual=(
                payload.unemployment_actual
            ),
            unemployment_forecast=(
                payload.unemployment_forecast
            ),
            unemployment_previous=(
                payload.unemployment_previous
            ),
            wage_mom_actual=(
                payload.wage_mom_actual
            ),
            wage_mom_forecast=(
                payload.wage_mom_forecast
            ),
            wage_mom_previous=(
                payload.wage_mom_previous
            ),
            wage_yoy_actual=(
                payload.wage_yoy_actual
            ),
            wage_yoy_forecast=(
                payload.wage_yoy_forecast
            ),
            wage_yoy_previous=(
                payload.wage_yoy_previous
            ),
        )
    )

    return NFPAnalysisResponse(
        event=analysis.event,
        classification=analysis.classification,
        score=analysis.score,
        confidence=analysis.confidence,
        components=[
            MacroScoreComponentResponse(
                name=component.name,
                score=component.score,
                weight=component.weight,
                explanation=(
                    component.explanation
                ),
                available=component.available,
            )
            for component in analysis.components
        ],
        strong_factors=analysis.strong_factors,
        weak_factors=analysis.weak_factors,
        contradictions=analysis.contradictions,
        warnings=analysis.warnings,
        summary=analysis.summary,
    )



@router.post(
    "/analyze/nfp/evidence",
    response_model=(
        NFPMultimodalAnalysisResponse
    ),
)
async def analyze_nfp_multimodal_evidence(
    current_user: User = Depends(
        require_premium_plan,
    ),
    evidence: str = Form(default=""),
    images: list[UploadFile] = File(
        default=[],
    ),
) -> NFPMultimodalAnalysisResponse:
    """
    Analyse NFP text and up to five screenshots.

    Gemini extracts factual evidence only.

    The existing deterministic NFP engine
    performs the economic classification.

    A separate deterministic layer converts
    that validated result into macro directional
    biases. It does not produce trade calls.
    """

    _ = current_user

    clean_evidence = evidence.strip()

    if len(images) > 5:
        raise HTTPException(
            status_code=422,
            detail=(
                "A maximum of five screenshots "
                "may be analysed at once."
            ),
        )

    allowed_types = {
        "image/png",
        "image/jpeg",
        "image/webp",
    }

    extracted_images: list[
        tuple[bytes, str, str]
    ] = []

    evidence_sources: list[str] = []

    if clean_evidence:
        evidence_sources.append(
            "Text evidence"
        )

    for (
        index,
        image,
    ) in enumerate(
        images,
        start=1,
    ):
        mime_type = (
            image.content_type or ""
        ).lower()

        if mime_type not in allowed_types:
            await image.close()

            raise HTTPException(
                status_code=415,
                detail=(
                    "Only PNG, JPEG and WEBP "
                    "screenshots are supported."
                ),
            )

        image_bytes = await image.read(
            10 * 1024 * 1024 + 1
        )

        await image.close()

        if len(image_bytes) > (
            10 * 1024 * 1024
        ):
            raise HTTPException(
                status_code=413,
                detail=(
                    "Each screenshot must be "
                    "10 MB or smaller."
                ),
            )

        if not image_bytes:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Screenshot {index} "
                    "is empty."
                ),
            )

        source_label = (
            f"Screenshot {index}"
        )

        extracted_images.append(
            (
                image_bytes,
                mime_type,
                source_label,
            )
        )

        evidence_sources.append(
            source_label
        )

    if (
        not clean_evidence
        and not extracted_images
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "Supply text evidence, "
                "one or more screenshots, "
                "or both."
            ),
        )

    try:
        extracted = (
            extract_nfp_from_sources(
                text=clean_evidence,
                images=extracted_images,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "AI evidence extraction "
                "is temporarily unavailable."
            ),
        ) from exc

    structured = NFPInput(
        nfp_actual=extracted[
            "nfp_actual"
        ],
        nfp_forecast=extracted[
            "nfp_forecast"
        ],
        nfp_previous=extracted[
            "nfp_previous"
        ],
        nfp_revised_previous=extracted[
            "nfp_revised_previous"
        ],
        unemployment_actual=extracted[
            "unemployment_actual"
        ],
        unemployment_forecast=extracted[
            "unemployment_forecast"
        ],
        unemployment_previous=extracted[
            "unemployment_previous"
        ],
        wage_mom_actual=extracted[
            "wage_mom_actual"
        ],
        wage_mom_forecast=extracted[
            "wage_mom_forecast"
        ],
        wage_mom_previous=extracted[
            "wage_mom_previous"
        ],
        wage_yoy_actual=extracted[
            "wage_yoy_actual"
        ],
        wage_yoy_forecast=extracted[
            "wage_yoy_forecast"
        ],
        wage_yoy_previous=extracted[
            "wage_yoy_previous"
        ],

        adp_actual=extracted[
            "adp_actual"
        ],
        adp_forecast=extracted[
            "adp_forecast"
        ],
        adp_previous=extracted[
            "adp_previous"
        ],

        jolts_actual=extracted[
            "jolts_actual"
        ],
        jolts_forecast=extracted[
            "jolts_forecast"
        ],
        jolts_previous=extracted[
            "jolts_previous"
        ],

        claims_actual=extracted[
            "claims_actual"
        ],
        claims_forecast=extracted[
            "claims_forecast"
        ],
        claims_previous=extracted[
            "claims_previous"
        ],
    )

    analysis = analyze_nfp(
        structured
    )

    directional = (
        analyze_directional_bias(
            analysis
        )
    )

    return NFPMultimodalAnalysisResponse(
        event=analysis.event,
        classification=(
            analysis.classification
        ),
        score=analysis.score,
        confidence=analysis.confidence,
        components=[
            MacroScoreComponentResponse(
                name=component.name,
                score=component.score,
                weight=component.weight,
                explanation=(
                    component.explanation
                ),
                available=component.available,
            )
            for component
            in analysis.components
        ],
        strong_factors=(
            analysis.strong_factors
        ),
        weak_factors=(
            analysis.weak_factors
        ),
        contradictions=(
            analysis.contradictions
        ),
        warnings=analysis.warnings,
        summary=analysis.summary,
        extracted_evidence=(
            NFPExtractedEvidenceResponse(
                **extracted
            )
        ),
        directional_bias=(
            DirectionalBiasResponse(
                overall_context=(
                    directional.overall_context
                ),
                markets=[
                    MarketDirectionalBiasResponse(
                        market=item.market,
                        bias=item.bias,
                        confidence=(
                            item.confidence
                        ),
                        explanation=(
                            item.explanation
                        ),
                    )
                    for item
                    in directional.markets
                ],
                disclaimer=(
                    directional.disclaimer
                ),
            )
        ),
        evidence_sources=(
            evidence_sources
        ),
    )


@router.post(
    "/analyze/nfp/text",
    response_model=NFPTextAnalysisResponse,
)
def analyze_nfp_text_evidence(
    payload: NFPTextAnalysisRequest,
    current_user: User = Depends(
        require_premium_plan,
    ),
) -> NFPTextAnalysisResponse:
    """
    Extract and analyse raw NFP text evidence.

    Gemini performs evidence extraction only.
    The deterministic NFP engine performs the
    strong, weak or inconclusive classification.

    This endpoint does not predict asset direction
    and does not generate trade calls.
    """

    _ = current_user

    extracted = extract_nfp_from_text(
        payload.evidence
    )

    analysis = analyze_nfp(
        NFPInput(
            nfp_actual=extracted[
                "nfp_actual"
            ],
            nfp_forecast=extracted[
                "nfp_forecast"
            ],
            nfp_previous=extracted[
                "nfp_previous"
            ],
            nfp_revised_previous=extracted[
                "nfp_revised_previous"
            ],
            unemployment_actual=extracted[
                "unemployment_actual"
            ],
            unemployment_forecast=extracted[
                "unemployment_forecast"
            ],
            unemployment_previous=extracted[
                "unemployment_previous"
            ],
            wage_mom_actual=extracted[
                "wage_mom_actual"
            ],
            wage_mom_forecast=extracted[
                "wage_mom_forecast"
            ],
            wage_mom_previous=extracted[
                "wage_mom_previous"
            ],
            wage_yoy_actual=extracted[
                "wage_yoy_actual"
            ],
            wage_yoy_forecast=extracted[
                "wage_yoy_forecast"
            ],
            wage_yoy_previous=extracted[
                "wage_yoy_previous"
            ],
        )
    )

    return NFPTextAnalysisResponse(
        event=analysis.event,
        classification=(
            analysis.classification
        ),
        score=analysis.score,
        confidence=analysis.confidence,
        components=[
            MacroScoreComponentResponse(
                name=component.name,
                score=component.score,
                weight=component.weight,
                explanation=(
                    component.explanation
                ),
                available=component.available,
            )
            for component
            in analysis.components
        ],
        strong_factors=(
            analysis.strong_factors
        ),
        weak_factors=(
            analysis.weak_factors
        ),
        contradictions=(
            analysis.contradictions
        ),
        warnings=analysis.warnings,
        summary=analysis.summary,
        extracted_evidence=(
            NFPExtractedEvidenceResponse(
                **extracted
            )
        ),
    )


@router.post(
    "/analyze/general",
    response_model=GeneralMacroAnalysisResponse,
)
async def analyze_general_macro(
    current_user: User = Depends(
        require_premium_plan,
    ),
    evidence: str = Form(default=""),
    images: list[UploadFile] = File(default=[]),
) -> GeneralMacroAnalysisResponse:
    """
    General-purpose Macro AI Analyst.

    Accepts free-form economic evidence and screenshots.
    Gemini reads and reasons over the complete submission.
    No predefined NFP fields are required.
    """

    _ = current_user

    clean_evidence = evidence.strip()

    if len(images) > 5:
        raise HTTPException(
            status_code=422,
            detail=(
                "A maximum of five screenshots "
                "may be analysed at once."
            ),
        )

    allowed_types = {
        "image/png",
        "image/jpeg",
        "image/webp",
    }

    extracted_images = []
    evidence_sources = []

    if clean_evidence:
        evidence_sources.append("Text evidence")

    for index, image in enumerate(
        images,
        start=1,
    ):
        mime_type = (
            image.content_type or ""
        ).lower()

        if mime_type not in allowed_types:
            await image.close()
            raise HTTPException(
                status_code=415,
                detail=(
                    "Only PNG, JPEG and WEBP "
                    "screenshots are supported."
                ),
            )

        image_bytes = await image.read(
            10 * 1024 * 1024 + 1
        )

        await image.close()

        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=(
                    "Each screenshot must be "
                    "10 MB or smaller."
                ),
            )

        if not image_bytes:
            raise HTTPException(
                status_code=422,
                detail=f"Screenshot {index} is empty.",
            )

        source_label = f"Screenshot {index}"

        extracted_images.append(
            (
                image_bytes,
                mime_type,
                source_label,
            )
        )

        evidence_sources.append(source_label)

    if (
        not clean_evidence
        and not extracted_images
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "Supply economic evidence as text, "
                "screenshots, or both."
            ),
        )

    try:
        result = extract_general_macro_from_sources(
            text=clean_evidence,
            images=extracted_images,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    result["evidence_sources"] = evidence_sources

    return GeneralMacroAnalysisResponse(
        **result
    )
