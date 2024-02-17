# THIS IS NOT A WORKING EXAMPLE YET

# pylint: disable=duplicate-code,unused-argument


import bencher as bch
import math
import random
import numpy as np
import holoviews as hv

from strenum import StrEnum
from enum import auto


class Function(StrEnum):
    fn_cos = auto()
    fn_sin = auto()
    fn_log = auto()
    fn_arctan = auto()

    def call(self, arg) -> float:
        """Calls the function defined by the name of the enum

        Returns:
            float: The result of calling the function defined by the enum
        """
        return getattr(np, self.removeprefix("fn_"))(arg)


class PlotFunctions(bch.ParametrizedSweep):
    phase = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=5
    )

    freq = bch.FloatSweep(default=1, bounds=[0, math.pi], doc="Input angle", units="rad", samples=5)

    theta = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=10
    )

    compute_fn = bch.EnumSweep(Function)

    fn_output = bch.ResultVar(units="v", doc="sin of theta with some noise")

    out_sum = bch.ResultVar(units="v", doc="The sum")

    hmap = bch.ResultReference()
    hmap1 = bch.ResultHmap()

    def __call__(self, plot=True, **kwargs) -> dict:
        self.update_params_from_kwargs(**kwargs)
        noise = 0.1

        self.fn_output = self.compute_fn.call(self.phase + self.freq * self.theta) + random.uniform(
            0, noise
        )

        self.hmap1 = self.plot_holo(plot)
        self.hmap = bch.ResultReference(self.hmap1)

        return self.get_results_values_as_dict()

    def plot_holo(self, plot=True) -> hv.core.ViewableElement:
        """Plots a generic representation of the object that is not a basic hv datatype. In this case its an image of the values of the object, but it could be any representation of the object, e.g. a screenshot of the object state"""
        if plot:
            pt = hv.Text(0, 0, f"{self.phase}\n{self.freq}\n {self.theta}")
            pt *= hv.Ellipse(0, 0, 1)
            return pt
        return None


def example_holosweep(
    run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
) -> bch.Bench:
    wv = PlotFunctions()

    # run_cfg.use_optuna = True

    bench = bch.Bench("waves", wv, run_cfg=run_cfg, report=report)

    bench.plot_sweep(
        "phase",
        input_vars=[PlotFunctions.param.theta, PlotFunctions.param.freq],
        result_vars=[PlotFunctions.param.fn_output, PlotFunctions.param.hmap],
        # result_vars=[PlotFunctions.param.hmap],
    )

    # print("best", res.get_best_trial_params(True))
    # print(res.hmap_kdims)
    # bench.report.append(res.describe_sweep())
    # bench.report.append(res.to_optuna_plots())
    # bench.report.append(res.get_best_holomap())
    # bench.report.append(res.to_curve(), "Slider view")
    # bench.report.append(res.to_holomap())

    # bench.report.append(res.to_holomap().layout())
    return bench


if __name__ == "__main__":
    bench_run = bch.BenchRunner("bench_runner_test")
    bench_run.add_run(example_holosweep)
    bench_run.run(level=3, show=True, use_cache=False)
