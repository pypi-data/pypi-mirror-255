from __future__ import annotations

import dataclasses
import enum
import typing as typ
import uuid
from typing import Any

import jijmodeling as jm
import numpy as np


@dataclasses.dataclass
class SolvingTime:
    compiling_time: float = 0.0
    transpiling_time: float = 0.0
    preprocess: float = 0.0
    solving_time: float = 0.0
    decoding_time: float = 0.0
    postprocess: float = 0.0

    def total(self) -> float:
        total_time = sum(dataclasses.asdict(self).values())
        return total_time


@dataclasses.dataclass
class SystemTime:
    posting_time: typ.Optional[float] = None
    request_queuing_time: typ.Optional[float] = None
    fetching_problem_time: typ.Optional[float] = None
    fetching_result_time: typ.Optional[float] = None
    deserialize_time: typ.Optional[float] = None


@dataclasses.dataclass
class MeasuringTime:
    solving_time: SolvingTime = SolvingTime()
    system_time: SystemTime = SystemTime()

    def total(self) -> float:
        total_time = self.solving_time.total()
        for value in dataclasses.asdict(self.system_time).values():
            if value is not None:
                total_time += value
        return total_time


Serializable = typ.Union[str, int, float, dict, list]


class VarType(enum.IntEnum):
    CONTINUOUS = 0
    INTEGER = 1
    BINARY = 2


@dataclasses.dataclass(frozen=True)
class VariableSparseValue:
    name: str
    value: dict[tuple[int, ...], float]
    shape: tuple[int, ...]
    vartype: VarType

    def to_dense(self) -> np.ndarray:
        dense_value = np.zeros(self.shape, dtype=np.float64)
        for key, value in self.value.items():
            dense_value[key] = value
        return dense_value

    @classmethod
    def from_array(
        cls, name: str, array: np.ndarray, vartype: VarType = VarType.CONTINUOUS
    ) -> "VariableSparseValue":
        # Check array is scalar or not
        if array.ndim == 0:
            nnz_value = np.array([array])
            subscripts = [[]]
        else:
            nnz_indices = np.nonzero(array)
            subscripts = np.array(list(nnz_indices)).T
            nnz_value = array[nnz_indices]
        return cls(
            name=name,
            value={tuple(key): value for key, value in zip(subscripts, nnz_value)},
            shape=array.shape,
            vartype=vartype,
        )


@dataclasses.dataclass
class ExprEvaluation:
    name: str
    total_violation: float
    expr_values: dict[tuple[int, ...], float]


@dataclasses.dataclass
class EvaluationResult:
    energy: float
    objective: float
    constraints: dict[str, ExprEvaluation]
    penalties: dict[str, ExprEvaluation]


@dataclasses.dataclass
class Sample:
    """The Sample class is designed to store the result of mathematical optimization.

    In the following, we explain the attributes of the Sample class in detail.
    `.vars` is stored only non-zero elements of the decision variables.
    For example, if the values are x = `[[0, 1, 2], [1, 0, 0]]`, it is stored as `{(0, 1): 1, (0, 2): 2, (1, 0): 1}`.
    If you want to get the dense array of the decision variables, use `.to_dense()` method.

    `.run_id` is a unique identifier for the run in which the solution was found. Note that this is not a unique identifier for the sample.
    The same sample can have same run_id if the same sample is obtained in the same run.
    For example, if you run heuristic solver 10 times, you can get 10 samples with the same run_id; You have to set the same run_id manually.
    However, if you run heuristic solver 10 times with different parameters, you can get 10 samples with different run_id.

    Attribuites:
        vars (dict[str, VariableSparseValue]): Stores the optimal values of decision variables in a sparse matrix format. Only non-zero elements are stored.
        evaluation_result (EvaluationResult): Stores the evaluation result of the objective function's value and constraints.
        num_occurrences (int): The number of occurrences of the sample.
        run_id (str): Identifier for the run in which the solution was found. Note that this is not a unique identifier for the sample.
        meta_info (dict[str, Serializable]): Stores the meta information of the sample.
    """

    vars: dict[str, VariableSparseValue]
    evaluation_result: EvaluationResult
    num_occurrences: int = 1
    run_id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))
    meta_info: dict[str, Serializable] = dataclasses.field(default_factory=dict)

    def is_feasible(self, epsilon=1e-10) -> bool:
        total_violation = sum(
            [v.total_violation for v in self.evaluation_result.constraints.values()]
        )
        return total_violation < epsilon

    def to_dense(self) -> dict[str, np.ndarray]:
        dense_vars = {}
        for name, var in self.vars.items():
            dense_vars[name] = var.to_dense()
        return dense_vars

    @classmethod
    def from_array(
        cls,
        array: dict[str, np.ndarray],
        num_occurances: int = 1,
        vartype: typ.Optional[dict[str, VarType]] = None,
        run_id: typ.Optional[str] = None,
        meta_info: typ.Optional[dict] = None,
    ) -> Sample:
        if vartype is None:
            vartype = {name: VarType.CONTINUOUS for name in array.keys()}
        if run_id is None:
            run_id = str(uuid.uuid4())
        if meta_info is None:
            meta_info = {}
        sparse_vars = {}
        for name, value in array.items():
            _vartype = vartype.get(name, VarType.CONTINUOUS)
            sparse_vars[name] = VariableSparseValue.from_array(name, value, _vartype)
        return cls(
            vars=sparse_vars,
            evaluation_result=EvaluationResult(0.0, 0.0, {}, {}),
            num_occurrences=num_occurances,
            run_id=run_id,
            meta_info=meta_info,
        )


@dataclasses.dataclass
class SampleSet:
    """SampleSet is a set of samples

    The SampleSet class is designed to store a collection of Sample instances.

    It behaves similar to a list of Samples with additional features and capabilities.
    - Stores metadata for each SampleSet. During concatenation of multiple SampleSets using the concat method, it maintains the metadata of each SampleSet.
    - Uses the run_id of each Sample as a key in a dictionary to store and retain the metadata of each SampleSet in run_info.
    - Provides an interface to perform searches on the set of Samples, such as retrieving the set of executable solutions, the solution with the minimum objective function value, or the solution with the minimum constraint violation.
    - Implements __len__, __getitem__, and __iter__ to behave like a regular list of Samples.

    Attributes:
        data (list[Sample]): List of samples
        set_id (str): ID of the sample set
        set_info (dict[str, Serializable]): Information of the sample set
        run_info (dict[str, Serializable]): Information of the run
        measuring_time (MeasuringTime): Measuring time of the sample set
        run_times (dict[str, MeasuringTime]): Measuring time of each run

    """

    data: list[Sample]
    set_id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))
    set_info: dict[str, Serializable] = dataclasses.field(default_factory=dict)
    run_info: dict[str, Serializable] = dataclasses.field(default_factory=dict)
    measuring_time: MeasuringTime = dataclasses.field(default_factory=MeasuringTime)
    run_times: dict[str, MeasuringTime] = dataclasses.field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Sample:
        return self.data[idx]

    def __iter__(self) -> typ.Iterator[Sample]:
        return iter(self.data)

    def feasibles(self, epsilon=1e-8) -> SampleSet:
        """Return a sampleset with only feasible samples

        Args:
            epsilon (float, optional): Tolerance for constraint violation. Defaults to 1e-8.

        Returns:
            SampleSet: A sampleset with only feasible samples
        """
        sampleset = SampleSet(
            [sample for sample in self.data if sample.is_feasible(epsilon)]
        )
        sampleset.set_info = self.set_info
        sampleset.run_info = self.run_info
        return sampleset

    def separate(self) -> dict[str, SampleSet]:
        """Separate the sampleset into different samplesets based on the run_id"""
        separated: dict[str, SampleSet] = {}
        for sample in self.data:
            if sample.run_id not in separated:
                separated[sample.run_id] = SampleSet([])
            separated[sample.run_id].data.append(sample)

        for run_id in separated.keys():
            separated[run_id].set_info = self.set_info
            separated[run_id].measuring_time = self.measuring_time
            if run_id in self.run_info:
                separated[run_id].run_info[run_id] = self.run_info[run_id]
            if run_id in self.run_times:
                separated[run_id].measuring_time = self.run_times[run_id]

        return separated

    @classmethod
    def concat(cls, family: list[SampleSet]) -> SampleSet:
        """Concatenate a list of samplesets into one

        Args:
            family (list[SampleSet]): A list of samplesets

        Returns:
            SampleSet: A sampleset that contains all samples from the input samplesets
        """
        data: list[Sample] = []
        run_info: dict[str, Serializable] = {}
        run_times: dict[str, MeasuringTime] = {}
        for sampleset in family:
            for _sampleset in sampleset.separate().values():
                data.extend(_sampleset.data)
                run_info.update(_sampleset.run_info)
                run_times.update(_sampleset.run_times)
        return cls(data, set_info={}, run_info=run_info)

    @classmethod
    def from_array(
        cls, samples: list[dict[str, typ.Union[np.ndarray, list]]]
    ) -> "SampleSet":
        data: list[Sample] = []
        run_id = str(uuid.uuid4())
        for sample in samples:
            _sample = {name: np.array(value) for name, value in sample.items()}
            data.append(Sample.from_array(_sample, run_id=run_id))
        return cls(data=data)


def serialize_sampleset(samplset: SampleSet) -> dict[str, Any]:
    obj = dataclasses.asdict(samplset)

    for sampleset_field_name, sampleset_field in obj.items():
        if sampleset_field_name == "data":
            for i, sample in enumerate(sampleset_field):
                for sample_field_name, sample_field in sample.items():
                    if sample_field_name == "vars":
                        for var_name, deci_var in sample_field.items():
                            for deci_var_field_name, deci_var_field in deci_var.items():
                                if deci_var_field_name == "value":
                                    index_list = []
                                    value_list = []
                                    for index, value in deci_var_field.items():
                                        index_list.append(
                                            list([np.array(i).tolist() for i in index])
                                        )
                                        value_list.append(np.array(value).tolist())
                                    obj["data"][i]["vars"][var_name]["value"] = [
                                        index_list,
                                        value_list,
                                    ]
    return obj


def from_old_sampleset(sampleset: typ.Union[SampleSet, jm.SampleSet]) -> SampleSet:
    if isinstance(sampleset, SampleSet):
        return sampleset

    solutions: list[dict[str, VariableSparseValue]] = []
    for label, _solutions in sampleset.record.solution.items():
        for i, sol in enumerate(_solutions):
            if len(solutions) <= i:
                solutions.append({})

            if isinstance(sol, np.ndarray):
                # If solution is dense type data format
                solutions[i][label] = VariableSparseValue.from_array(label, sol)

            else:
                # If solution is sparse type data format
                nnz_indices = sol[0]
                nnz_values = sol[1]
                shape = sol[2]

                if len(shape) == 0:
                    # sol is scalar
                    if len(nnz_values):
                        solutions[i][label] = VariableSparseValue.from_array(
                            label, np.array(nnz_values)[0]
                        )
                    else:
                        solutions[i][label] = VariableSparseValue.from_array(
                            label, np.array([])
                        )
                else:
                    # sol is array
                    nnz_inv_indices = np.array(list(nnz_indices)).T
                    solutions[i][label] = VariableSparseValue(
                        name=label,
                        value={
                            tuple(idx): value
                            for idx, value in zip(nnz_inv_indices, nnz_values)
                        },
                        shape=shape,
                        vartype=VarType.CONTINUOUS,
                    )

    data: list[Sample] = []
    # add same run_id for all samples
    run_id = str(uuid.uuid4())
    for i, sol in enumerate(solutions):
        energy: list[float] | None = sampleset.evaluation.energy
        objective: list[float] | None = sampleset.evaluation.objective
        const_violation = sampleset.evaluation.constraint_violations
        if energy is None:
            energy = []
        if objective is None:
            objective = []
        constraint: dict[str, ExprEvaluation] = {}
        if const_violation is not None:
            for label, const in const_violation.items():
                constraint[label] = ExprEvaluation(
                    name=label, total_violation=const[i], expr_values={}
                )
        data.append(
            Sample(
                vars=sol,
                evaluation_result=EvaluationResult(
                    energy=energy[i] if len(energy) else 0.0,
                    objective=objective[i] if len(objective) else 0.0,
                    constraints=constraint,
                    penalties={},
                ),
                # TODO: 1 -> sampleset.record.num_occurrences[i]
                num_occurrences=1,
                meta_info={},
                run_id=run_id,
            )
        )

    return SampleSet(
        data=data,
        set_info=sampleset.metadata,
        run_info={},
    )
