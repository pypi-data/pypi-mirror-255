from __future__ import annotations

import json
import pathlib
from dataclasses import make_dataclass
from typing import TYPE_CHECKING, Any, Literal

import h5py
import jijmodeling as jm
import pandas as pd

from minto.consts.default import DEFAULT_RESULT_DIR
from minto.experiment.experiment import Experiment
from minto.table.table import SchemaBasedTable
from minto.typing import ArtifactDataType
from minto.utils.rc_sampleset import (
    EvaluationResult,
    ExprEvaluation,
    Sample,
    SampleSet,
    VariableSparseValue,
)

if TYPE_CHECKING:
    from minto.experiment.experiment import DatabaseSchema


def load(
    experiment_name: str,
    savedir: str | pathlib.Path = DEFAULT_RESULT_DIR,
) -> Experiment:
    """Load and return an artifact, experiment, or table from the given directory.

    Args:
        experiment_name (list[str] | None, optional): List of names of experiments to be loaded, if None, all experiments in `savedir` will be loaded. Defaults to None.
        savedir (str | pathlib.Path, optional): Directory of the experiment. Defaults to DEFAULT_RESULT_DIR.
    Raises:
        FileNotFoundError: If `name_or_dir` is not found in the `savedir` directory.
        ValueError: If `return_type` is not one of "Artifact", "Experiment", or "Table".

    Returns:
        Experiment | Artifact | Table: The loaded artifact, experiment, or table.
    """

    savedir = pathlib.Path(savedir)
    if not (savedir / experiment_name).exists():
        raise FileNotFoundError(f"{(savedir / experiment_name)} is not found.")

    exp = Experiment(experiment_name, savedir=savedir)

    database: DatabaseSchema = getattr(exp, "database")

    base_dir = savedir / experiment_name
    with open(base_dir / "dtypes.json", "r") as f:
        dtypes = json.load(f)

    keys: list[Literal["index", "solver", "parameter", "result"]] = [
        "index",
        "solver",
        "parameter",
        "result",
    ]
    for key in keys:
        if key == "index":
            index = pd.read_csv(base_dir / "index.csv").astype(dtypes[key])
            database["index"] = SchemaBasedTable.from_dataframe(index)
        else:
            info = pd.read_csv(base_dir / f"{key}" / "info.csv").astype(
                dtypes[key]["info"]
            )
            database[key]["info"] = SchemaBasedTable.from_dataframe(info)

            obj: ArtifactDataType = {}
            with h5py.File(base_dir / f"{key}" / "content.h5", "r") as f:
                for index in f:
                    obj[int(index)] = {}

                    for name in f[index]:
                        obj[int(index)][name] = json.loads(f[index][name][()])

                content = pd.DataFrame(obj).T

            if key in ("parameter", "result"):
                problems = {}
                for i, file in enumerate(
                    (exp.savedir / exp.name / f"{key}" / "problems").glob("*")
                ):
                    with open(file, "rb") as f:
                        content_id = int(file.name.split(".")[0])
                        problem = jm.from_protobuf(f.read())

                        problems[i] = {f"{key}_id": content_id, "content": problem}
                content = pd.concat([content, pd.DataFrame(problems).T]).reset_index(
                    drop=True
                )

                samplesets = {}
                for i, file in enumerate(
                    (exp.savedir / exp.name / f"{key}" / "samplesets").glob("*")
                ):
                    with open(file, "r") as f:
                        content_id = int(file.name.split(".")[0])
                        sampleset = to_samplset(json.load(f))

                        samplesets[i] = {f"{key}_id": content_id, "content": sampleset}
                content = pd.concat([content, pd.DataFrame(samplesets).T]).reset_index(
                    drop=True
                )

                dc_objs = {}
                for i, file in enumerate(
                    (exp.savedir / exp.name / f"{key}" / "dataclasses").glob("*")
                ):
                    with open(file, "r") as f:
                        content_id = int(file.name.split(".")[0])
                        json_obj = json.load(f)
                        dc_obj = make_dataclass(json_obj["name"], json_obj["type"])(
                            **json_obj["data"]
                        )

                        dc_objs[i] = {f"{key}_id": content_id, "content": dc_obj}
                content = pd.concat([content, pd.DataFrame(dc_objs).T]).reset_index(
                    drop=True
                )

            if content.empty:
                content = pd.DataFrame(columns=dtypes[key]["content"])
            content = content.astype(dtypes[key]["content"])
            content = content[content[f"{key}_id"].isin(info[f"{key}_id"])].sort_values(
                f"{key}_id"
            )
            database[key]["content"] = SchemaBasedTable.from_dataframe(content)
    return exp


def to_samplset(obj: dict[str, Any]) -> SampleSet:
    for sampleset_field_name, sampleset_field in obj.items():
        if sampleset_field_name == "data":
            for i, sample in enumerate(sampleset_field):
                sample_dict = {}
                for sample_field_name, sample_field in sample.items():
                    if sample_field_name == "vars":
                        for var_name, var_dict in sample_field.items():
                            sample_dict.setdefault("vars", {})[
                                var_name
                            ] = VariableSparseValue(
                                **_deserialize_sparse_variable(var_dict)
                            )
                    elif sample_field_name == "evaluation_result":
                        eval_result_dict = {}
                        for (
                            eval_result_field_name,
                            eval_result_field,
                        ) in sample_field.items():
                            if eval_result_field_name == "constraints":
                                if eval_result_field:
                                    for (
                                        constraint_name,
                                        constraint_dict,
                                    ) in eval_result_field.items():
                                        eval_result_dict.setdefault("constraints", {})[
                                            constraint_name
                                        ] = ExprEvaluation(**constraint_dict)
                                else:
                                    eval_result_dict["constraints"] = {}
                            elif eval_result_field_name == "penalties":
                                eval_result_dict["penalties"] = {}
                            else:
                                eval_result_dict[
                                    eval_result_field_name
                                ] = eval_result_field
                        sample_dict["evaluation_result"] = EvaluationResult(
                            **eval_result_dict
                        )
                obj["data"][i] = Sample(**sample_dict)

    return SampleSet(**obj)


def _deserialize_sparse_variable(
    obj: dict[str, Any],
) -> dict[str, Any]:
    for field_name, field in obj.items():
        if field_name == "value":
            obj["value"] = {tuple(i): v for i, v in zip(field[0], field[1])}
    return obj
