from __future__ import annotations

import re
from typing import Literal

import jijmodeling as jm
import pandas as pd
from jijzept.response import JijModelingResponse

from minto.records.records import Record
from minto.table.table import SchemaBasedTable
from minto.utils.rc_sampleset import (
    EvaluationResult,
    ExprEvaluation,
    SampleSet,
    VariableSparseValue,
    VarType,
    from_old_sampleset,
)


class SampleSetRecord(Record):
    sample_run_id: str
    num_occurrences: int
    energy: float
    objective: float
    is_feasible: bool
    sample_id: int
    deci_var_value: dict[str, VariableSparseValue]
    eval_result: EvaluationResult


def expand_sampleset(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    sampleset_df = dataframe[
        dataframe["content"].apply(
            lambda x: isinstance(x, (SampleSet, jm.SampleSet, JijModelingResponse))
        )
    ]
    df_list = []
    for _, record in sampleset_df.iterrows():
        table = convert_sampleset_to_table(
            record["content"], content_id=record["result_id"], key="result"
        )
        df_list.append(table.dataframe())

    if len(df_list) == 0:
        return pd.DataFrame()
    else:
        return pd.concat(df_list)


def to_valid_name(name: str) -> str:
    return re.sub(r"\W|^(?=\d)", "_", name)


def convert_sampleset_to_table(
    sampleset: SampleSet | JijModelingResponse,
    content_id: int,
    key: Literal["parameter", "result"],
) -> SchemaBasedTable:
    if isinstance(sampleset, JijModelingResponse):
        sampleset = from_old_sampleset(sampleset.sample_set)
    elif isinstance(sampleset, jm.SampleSet):
        sampleset = from_old_sampleset(sampleset)

    schema = SampleSetRecord.dtypes
    schema[f"{key}_id"] = int
    # add constraint violation columns to schema
    if len(sampleset) > 0:
        for constraint_name in sampleset[0].evaluation_result.constraints.keys():
            constraint_name = to_valid_name(constraint_name)
            schema[constraint_name + "_total_violation"] = float

    sampleset_table = SchemaBasedTable(schema=schema)
    sampleset_table._validator.model_rebuild(
        _types_namespace={"VarType": VarType, "ExprEvaluation": ExprEvaluation}
    )

    for sample_id, sample in enumerate(sampleset):
        record = {
            f"{key}_id": content_id,
            "sample_run_id": sample.run_id,
            "num_occurrences": int(sample.num_occurrences),
            "energy": float(sample.evaluation_result.energy),
            "objective": float(sample.evaluation_result.objective),
            "is_feasible": bool(sample.is_feasible()),
            "sample_id": sample_id,
            "deci_var_value": sample.vars,
            "eval_result": sample.evaluation_result,
        }
        # extract constraint total violation
        total_violations: dict[str, float] = {}
        for constraint_name, constraint in sample.evaluation_result.constraints.items():
            constraint_name = to_valid_name(constraint_name)
            total_violations[
                constraint_name + "_total_violation"
            ] = constraint.total_violation
        record.update(total_violations)
        sampleset_table.insert(record)
    return sampleset_table
