from enum import Enum

from pydantic import Field

from ribasim.input_base import ChildModel, NodeModel, TableModel

# These schemas are autogenerated
from ribasim.schemas import (  # type: ignore
    BasinProfileSchema,
    BasinStateSchema,
    BasinStaticSchema,
    BasinSubgridSchema,
    BasinTimeSchema,
    DiscreteControlConditionSchema,
    DiscreteControlLogicSchema,
    FlowBoundaryStaticSchema,
    FlowBoundaryTimeSchema,
    FractionalFlowStaticSchema,
    LevelBoundaryStaticSchema,
    LevelBoundaryTimeSchema,
    LinearResistanceStaticSchema,
    ManningResistanceStaticSchema,
    OutletStaticSchema,
    PidControlStaticSchema,
    PidControlTimeSchema,
    PumpStaticSchema,
    TabulatedRatingCurveStaticSchema,
    TabulatedRatingCurveTimeSchema,
    TerminalStaticSchema,
    UserStaticSchema,
    UserTimeSchema,
)


class Allocation(ChildModel):
    timestep: float | None = None
    use_allocation: bool = False
    objective_type: str = "quadratic_relative"


class Compression(str, Enum):
    zstd = "zstd"
    lz4 = "lz4"


class Results(ChildModel):
    outstate: str | None = None
    compression: Compression = Compression.zstd
    compression_level: int = 6
    subgrid: bool = False


class Solver(ChildModel):
    algorithm: str = "QNDF"
    saveat: float | list[float] = []
    adaptive: bool = True
    dt: float | None = None
    dtmin: float | None = None
    dtmax: float | None = None
    force_dtmin: bool = False
    abstol: float = 1e-06
    reltol: float = 1e-05
    maxiters: int = 1000000000
    sparse: bool = True
    autodiff: bool = True


class Verbosity(str, Enum):
    debug = "debug"
    info = "info"
    warn = "warn"
    error = "error"


class Logging(ChildModel):
    verbosity: Verbosity = Verbosity.info
    timing: bool = False


class Terminal(NodeModel):
    static: TableModel[TerminalStaticSchema] = Field(
        default_factory=TableModel[TerminalStaticSchema],
        json_schema_extra={"sort_keys": ["node_id"]},
    )


class PidControl(NodeModel):
    static: TableModel[PidControlStaticSchema] = Field(
        default_factory=TableModel[PidControlStaticSchema],
        json_schema_extra={"sort_keys": ["node_id", "control_state"]},
    )
    time: TableModel[PidControlTimeSchema] = Field(
        default_factory=TableModel[PidControlTimeSchema],
        json_schema_extra={"sort_keys": ["node_id", "time"]},
    )


class LevelBoundary(NodeModel):
    static: TableModel[LevelBoundaryStaticSchema] = Field(
        default_factory=TableModel[LevelBoundaryStaticSchema],
        json_schema_extra={"sort_keys": ["node_id"]},
    )
    time: TableModel[LevelBoundaryTimeSchema] = Field(
        default_factory=TableModel[LevelBoundaryTimeSchema],
        json_schema_extra={"sort_keys": ["node_id", "time"]},
    )


class Pump(NodeModel):
    static: TableModel[PumpStaticSchema] = Field(
        default_factory=TableModel[PumpStaticSchema],
        json_schema_extra={"sort_keys": ["node_id", "control_state"]},
    )


class TabulatedRatingCurve(NodeModel):
    static: TableModel[TabulatedRatingCurveStaticSchema] = Field(
        default_factory=TableModel[TabulatedRatingCurveStaticSchema],
        json_schema_extra={"sort_keys": ["node_id", "control_state", "level"]},
    )
    time: TableModel[TabulatedRatingCurveTimeSchema] = Field(
        default_factory=TableModel[TabulatedRatingCurveTimeSchema],
        json_schema_extra={"sort_keys": ["node_id", "time", "level"]},
    )


class User(NodeModel):
    static: TableModel[UserStaticSchema] = Field(
        default_factory=TableModel[UserStaticSchema],
        json_schema_extra={"sort_keys": ["node_id", "priority"]},
    )
    time: TableModel[UserTimeSchema] = Field(
        default_factory=TableModel[UserTimeSchema],
        json_schema_extra={"sort_keys": ["node_id", "priority", "time"]},
    )


class FlowBoundary(NodeModel):
    static: TableModel[FlowBoundaryStaticSchema] = Field(
        default_factory=TableModel[FlowBoundaryStaticSchema],
        json_schema_extra={"sort_keys": ["node_id"]},
    )
    time: TableModel[FlowBoundaryTimeSchema] = Field(
        default_factory=TableModel[FlowBoundaryTimeSchema],
        json_schema_extra={"sort_keys": ["node_id", "time"]},
    )


class Basin(NodeModel):
    profile: TableModel[BasinProfileSchema] = Field(
        default_factory=TableModel[BasinProfileSchema],
        json_schema_extra={"sort_keys": ["node_id", "level"]},
    )
    state: TableModel[BasinStateSchema] = Field(
        default_factory=TableModel[BasinStateSchema],
        json_schema_extra={"sort_keys": ["node_id"]},
    )
    static: TableModel[BasinStaticSchema] = Field(
        default_factory=TableModel[BasinStaticSchema],
        json_schema_extra={"sort_keys": ["node_id"]},
    )
    time: TableModel[BasinTimeSchema] = Field(
        default_factory=TableModel[BasinTimeSchema],
        json_schema_extra={"sort_keys": ["node_id", "time"]},
    )
    subgrid: TableModel[BasinSubgridSchema] = Field(
        default_factory=TableModel[BasinSubgridSchema],
        json_schema_extra={"sort_keys": ["subgrid_id", "basin_level"]},
    )


class ManningResistance(NodeModel):
    static: TableModel[ManningResistanceStaticSchema] = Field(
        default_factory=TableModel[ManningResistanceStaticSchema],
        json_schema_extra={"sort_keys": ["node_id", "control_state"]},
    )


class DiscreteControl(NodeModel):
    condition: TableModel[DiscreteControlConditionSchema] = Field(
        default_factory=TableModel[DiscreteControlConditionSchema],
        json_schema_extra={
            "sort_keys": ["node_id", "listen_feature_id", "variable", "greater_than"]
        },
    )
    logic: TableModel[DiscreteControlLogicSchema] = Field(
        default_factory=TableModel[DiscreteControlLogicSchema],
        json_schema_extra={"sort_keys": ["node_id", "truth_state"]},
    )


class Outlet(NodeModel):
    static: TableModel[OutletStaticSchema] = Field(
        default_factory=TableModel[OutletStaticSchema],
        json_schema_extra={"sort_keys": ["node_id", "control_state"]},
    )


class LinearResistance(NodeModel):
    static: TableModel[LinearResistanceStaticSchema] = Field(
        default_factory=TableModel[LinearResistanceStaticSchema],
        json_schema_extra={"sort_keys": ["node_id", "control_state"]},
    )


class FractionalFlow(NodeModel):
    static: TableModel[FractionalFlowStaticSchema] = Field(
        default_factory=TableModel[FractionalFlowStaticSchema],
        json_schema_extra={"sort_keys": ["node_id", "control_state"]},
    )
