"""Evidently custom business metric used beside the built-in drift presets."""
from typing import List, Union

from evidently.base_metric import ColumnName, InputData, Metric, MetricResult
from evidently.model.widget import BaseWidgetInfo
from evidently.renderers.base_renderer import MetricRenderer, default_renderer
from evidently.renderers.html_widgets import CounterData, counter, header_text


class MeanShiftMetricResult(MetricResult):
    class Config:
        type_alias = "week17:metric_result:MeanShiftMetricResult"

    column_name: str
    reference_mean: float
    current_mean: float
    absolute_shift: float
    relative_shift_pct: float


class MeanShiftMetric(Metric[MeanShiftMetricResult]):
    """Difference in a numeric feature's mean between reference and current."""
    class Config:
        type_alias = "week17:metric:MeanShiftMetric"

    column_name: ColumnName

    def __init__(self, column_name: Union[str, ColumnName]):
        self.column_name = ColumnName.from_any(column_name)
        super().__init__()

    def calculate(self, data: InputData) -> MeanShiftMetricResult:
        _, current, reference = data.get_data(self.column_name)
        if reference is None:
            raise ValueError("MeanShiftMetric requires reference data")
        ref_mean, cur_mean = float(reference.mean()), float(current.mean())
        shift = cur_mean - ref_mean
        return MeanShiftMetricResult(
            column_name=self.column_name.display_name,
            reference_mean=ref_mean,
            current_mean=cur_mean,
            absolute_shift=shift,
            relative_shift_pct=100 * shift / ref_mean if ref_mean else 0.0,
        )


@default_renderer(wrap_type=MeanShiftMetric)
class MeanShiftMetricRenderer(MetricRenderer):
    def render_html(self, obj: MeanShiftMetric) -> List[BaseWidgetInfo]:
        result = obj.get_result()
        return [
            header_text(label=f"Custom business metric: mean shift in {result.column_name}"),
            counter(counters=[
                CounterData.float(label="Reference mean", value=result.reference_mean, precision=2),
                CounterData.float(label="Current mean", value=result.current_mean, precision=2),
                CounterData.float(label="Absolute shift", value=result.absolute_shift, precision=2),
                CounterData.float(label="Relative shift (%)", value=result.relative_shift_pct, precision=2),
            ]),
        ]
