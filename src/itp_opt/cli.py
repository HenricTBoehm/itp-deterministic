from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from .analysis import summarize
from .constraints import REPORT_CONSTRAINTS
from .enumeration import enumerate_with_status, generate
from .evaluators import EnergyPlusEvaluator, ObservedDataEvaluator
from .models import Catalog, EvaluationResult, Status
from .optimization import exhaustive_search
from .reporting import audit, write_json, write_results_csv
from .reconciliation import constraint_forensics, source_reconciliation, write_source_csv
from .validation import load_combined_observations, validate_data_directory


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="itp-opt", description="Deterministic ITP building optimization")
    result.add_argument("--data-dir", type=Path, default=Path("data/original"))
    result.add_argument("--results-dir", type=Path, default=Path("results"))
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    commands.add_parser("analyze")
    commands.add_parser("enumerate")
    commands.add_parser("reconcile")
    optimize = commands.add_parser("optimize")
    optimize.add_argument("--backend", choices=("observed", "energyplus"), default="observed")
    optimize.add_argument("--objective", default="energy_demand")
    optimize.add_argument("--config", type=Path)
    verify = commands.add_parser("verify")
    verify.add_argument("--config", type=Path, required=True)
    return result


def _read_config(path: Path | None) -> dict:
    if path is None:
        return {}
    try:
        # JSON is a YAML 1.2 subset and avoids an undeclared runtime dependency.
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Config must be readable JSON (also valid YAML 1.2): {exc}") from exc


def _energyplus(config: dict) -> EnergyPlusEvaluator:
    return EnergyPlusEvaluator(
        Path(config["model"]) if config.get("model") else None,
        Path(config["weather"]) if config.get("weather") else None,
        config.get("executable", "energyplus"),
        Path(config.get("output_dir", "results/energyplus")),
    )


def _write_candidates(path: Path) -> dict[str, int]:
    path.parent.mkdir(parents=True, exist_ok=True)
    counts = {status.value: 0 for status in Status}
    fields = ["floor_slab", "ceiling", "exterior_wall", "interior_wall", "window",
              "main_door", "secondary_door", "x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8",
              "admissibility_status", "energy_evaluation_status", "reason"]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for configuration, status, reason in enumerate_with_status(
                Catalog.documented_shape(), list(REPORT_CONSTRAINTS)):
            counts[status.value] += 1
            writer.writerow({**configuration.as_dict(), "admissibility_status": status.value,
                             "energy_evaluation_status": Status.NON_EVALUABLE.value, "reason": reason})
    return counts


def run(args: argparse.Namespace) -> int:
    results_dir: Path = args.results_dir
    audit_path = results_dir / "audit_log.jsonl"
    if args.command == "validate":
        report = validate_data_directory(args.data_dir)
        write_json(results_dir / "validation_report.json", report)
        audit(audit_path, "validate", {"data_dir": str(args.data_dir), "valid": report["valid"],
                                       "files": {name: item.get("sha256") for name, item in report["files"].items()}})
        print(f"Validation report: {results_dir / 'validation_report.json'}")
        return 0 if report["valid"] else 2

    if args.command == "analyze":
        observations = load_combined_observations(args.data_dir)
        write_results_csv(results_dir / "observed_results.csv", observations)
        if not observations:
            audit(audit_path, "analyze", {"status": "NON_EVALUABLE", "reason": "No verified combined observations"})
            print("No verified combined input/output observations are available.", file=sys.stderr)
            return 2
        summary = summarize(observations)
        write_json(results_dir / "observed_summary.json", summary)
        validation = validate_data_directory(args.data_dir)
        audit(audit_path, "analyze", {"status": "complete", "observations": len(observations),
                                       "mapping": validation["input_output_mapping"],
                                       "files": {name: item.get("sha256") for name, item in validation["files"].items()}})
        print(f"Analyzed {len(observations)} observed simulations.")
        return 0

    if args.command == "enumerate":
        counts = _write_candidates(results_dir / "candidate_configurations.csv")
        summary = {"generated": sum(counts.values()), "status_counts": counts,
                   "energy_evaluation_status": Status.NON_EVALUABLE.value,
                   "energetically_optimized": False,
                   "reason": (
                       "Under the current report formula/unit/catalog transcription, every combination violates "
                       "at least one checkable wall constraint; this is not proof of physical impossibility. "
                       "The total-window-area constraint is additionally non-evaluable. No energy simulation occurred."
                   )}
        write_json(results_dir / "enumeration_summary.json", summary)
        audit(audit_path, "enumerate", summary)
        print(f"Generated {summary['generated']} candidates; none were energetically simulated.")
        return 0

    if args.command == "reconcile":
        constraints = constraint_forensics()
        reference_path = Path(__file__).parents[2] / "data" / "reference" / "report_scenarios.csv"
        sources = source_reconciliation(args.data_dir, reference_path)
        write_json(results_dir / "constraint_reconciliation.json", constraints)
        write_json(results_dir / "source_reconciliation.json", sources)
        write_source_csv(results_dir / "source_reconciliation.csv", sources)
        details = {
            "catalog_size": constraints["catalog_size"],
            "minimal_infeasible_subsets": constraints["minimal_infeasible_constraint_subsets"],
            "source_counts": sources["counts"],
            "reference_conclusion": constraints["reference_solution"]["conclusion"],
        }
        audit(audit_path, "reconcile", details)
        print(
            f"Reconciled constraints and sources: {sources['counts']['DISPUTED']} disputed input rows; "
            f"{len(constraints['minimal_infeasible_constraint_subsets'])} minimal infeasible subset."
        )
        return 0

    config = _read_config(args.config)
    if args.command == "verify":
        evaluator = _energyplus(config)
        missing = evaluator.prerequisites()
        details = {"status": "NON_EVALUABLE" if missing else "PREREQUISITES_PRESENT", "missing": missing,
                   "model_mapping_verified": False}
        write_json(results_dir / "verification_summary.json", details)
        audit(audit_path, "verify", details)
        if missing:
            print("Missing prerequisites: " + ", ".join(missing), file=sys.stderr)
            return 3
        print("EnergyPlus prerequisites exist, but model-field mapping is not yet verified.", file=sys.stderr)
        return 4

    observations = load_combined_observations(args.data_dir)
    if args.backend == "observed":
        evaluator = ObservedDataEvaluator(observations)
        configurations = [item.configuration for item in observations]
    else:
        evaluator = _energyplus(config)
        missing = evaluator.prerequisites()
        if missing:
            print("Missing prerequisites: " + ", ".join(missing), file=sys.stderr)
            audit(audit_path, "optimize", {"backend": "energyplus", "missing": missing})
            return 3
        configurations = list(generate(Catalog.documented_shape()))
    best, evaluated = exhaustive_search(configurations, evaluator, args.objective)
    write_results_csv(results_dir / "optimization_results.csv", evaluated)
    summary = {
        "backend": args.backend, "objective": args.objective, "evaluated": len(evaluated),
        "evaluable": sum(item.status is Status.ADMISSIBLE for item in evaluated),
        "best": None if best is None else {"value": best.objectives[args.objective],
                                            "configuration": best.configuration.as_dict()},
        "global_optimum_claim": False,
        "claim_scope": "minimum among exactly matched, verified-admissible observed configurations" if best else "none",
    }
    write_json(results_dir / "optimization_summary.json", summary)
    audit(audit_path, "optimize", summary)
    if best is None:
        print("No evaluable configuration for the requested objective.", file=sys.stderr)
        return 4
    print(f"Best observed {args.objective}: {best.objectives[args.objective]}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return run(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
