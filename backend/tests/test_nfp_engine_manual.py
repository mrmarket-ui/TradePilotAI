from services.macro_intelligence import (
    NFPInput,
    analyze_nfp,
)


def show_case(
    name: str,
    data: NFPInput,
):
    result = analyze_nfp(data)

    print()
    print("=" * 65)
    print(name)
    print("=" * 65)

    print(
        "Classification:",
        result.classification,
    )

    print(
        "Score:",
        result.score,
    )

    print(
        "Confidence:",
        f"{result.confidence}%",
    )

    print("Summary:", result.summary)

    print("\nComponents:")

    for component in result.components:
        status = (
            "AVAILABLE"
            if component.available
            else "MISSING"
        )

        print(
            f" - {component.name}: "
            f"{component.score:+.1f} "
            f"[{status}]"
        )

        print(
            f"   {component.explanation}"
        )

    if result.contradictions:
        print("\nContradictions:")

        for item in result.contradictions:
            print(" -", item)

    if result.warnings:
        print("\nWarnings:")

        for item in result.warnings:
            print(" -", item)

    return result


strong = show_case(
    "TEST 1 - STRONG NFP",
    NFPInput(
        nfp_actual=275,
        nfp_forecast=190,
        nfp_previous=175,
        nfp_revised_previous=195,
        unemployment_actual=3.9,
        unemployment_forecast=4.0,
        unemployment_previous=4.0,
        wage_mom_actual=0.4,
        wage_mom_forecast=0.3,
        wage_mom_previous=0.3,
        wage_yoy_actual=4.2,
        wage_yoy_forecast=4.0,
        wage_yoy_previous=4.0,
    ),
)

weak = show_case(
    "TEST 2 - WEAK NFP",
    NFPInput(
        nfp_actual=105,
        nfp_forecast=185,
        nfp_previous=175,
        nfp_revised_previous=150,
        unemployment_actual=4.2,
        unemployment_forecast=4.0,
        unemployment_previous=4.0,
        wage_mom_actual=0.2,
        wage_mom_forecast=0.3,
        wage_mom_previous=0.3,
        wage_yoy_actual=3.7,
        wage_yoy_forecast=4.0,
        wage_yoy_previous=4.0,
    ),
)

mixed = show_case(
    "TEST 3 - MIXED NFP",
    NFPInput(
        nfp_actual=225,
        nfp_forecast=180,
        nfp_previous=190,
        nfp_revised_previous=160,
        unemployment_actual=4.2,
        unemployment_forecast=4.0,
        wage_mom_actual=0.2,
        wage_mom_forecast=0.3,
        wage_yoy_actual=4.0,
        wage_yoy_forecast=4.0,
    ),
)


assert strong.classification == "STRONG"
assert weak.classification == "WEAK"
assert mixed.contradictions

print()
print("=" * 65)
print("NFP ENGINE TESTS PASSED")
print("=" * 65)
