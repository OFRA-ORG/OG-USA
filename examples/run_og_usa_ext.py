import multiprocessing
from distributed import Client
import os, argparse
import json
import time
from taxcalc import Calculator
import matplotlib.pyplot as plt
from ogusa.calibrate import Calibration
from ogcore.parameters import Specifications
from ogcore import output_tables as ot
from ogcore import output_plots as op
from ogcore.execute import runner
from ogcore.utils import safe_read_pickle

# Use a custom matplotlib style file for plots
style_file_url = (
    "https://raw.githubusercontent.com/PSLmodels/OG-Core/"
    + "master/ogcore/OGcorePlots.mplstyle"
)
plt.style.use(style_file_url)


def main(rho_G = None, g_y_annual = None):

    example_dir = "TCJA<>rho_G<>" + str(rho_G) + "<>g_y_annual<>" + str(g_y_annual)

    # Define parameters to use for multiprocessing
    num_workers = min(multiprocessing.cpu_count(), 5)
    client = Client(n_workers=num_workers, threads_per_worker=1)
    print("Number of workers = ", num_workers)

    # Directories to save data
    CUR_DIR = os.path.dirname(os.path.realpath(__file__))
    base_dir = os.path.join(CUR_DIR, example_dir, "OUTPUT_BASELINE")
    reform_dir = os.path.join(CUR_DIR, example_dir, "OUTPUT_REFORM")

    """
    ------------------------------------------------------------------------
    Run baseline policy
    ------------------------------------------------------------------------
    """
    # Set up baseline parameterization
    p = Specifications(
        baseline=True,
        num_workers=num_workers,
        baseline_dir=base_dir,
        output_base=base_dir,
    )
    # Update parameters for baseline from default json file
    p.update_specifications(
        json.load(
            open(
                os.path.join(
                    CUR_DIR, "..", "ogusa", "ogusa_default_parameters.json"
                )
            )
        )
    )
    p.tax_func_type = "GS"
    p.age_specific = False
    c = Calibration(p, estimate_tax_functions=True, client=client)
    # close and delete client bc cache is too large
    client.close()
    del client
    client = Client(n_workers=num_workers, threads_per_worker=1)
    d = c.get_dict()
    # # additional parameters to change
    updated_params = {
        "start_year": 2026,
        "etr_params": d["etr_params"],
        "mtrx_params": d["mtrx_params"],
        "mtry_params": d["mtry_params"],
        "mean_income_data": d["mean_income_data"],
        "frac_tax_payroll": d["frac_tax_payroll"],
    }
    if rho_G is not None:
        updated_params["rho_G"] = rho_G
    if g_y_annual is not None:
        updated_params["g_y_annual"] = g_y_annual
    p.update_specifications(updated_params)

    # Run model
    start_time = time.time()
    runner(p, time_path=True, client=client)
    print("run time = ", time.time() - start_time)

    """
    ------------------------------------------------------------------------
    Run reform policy
    ------------------------------------------------------------------------
    """
    # Grab a reform JSON file already in Tax-Calculator
    # In this example the 'reform' is a change to 2017 law (the
    # baseline policy is tax law in 2018)
    reform_url = (
        "github://PSLmodels:Tax-Calculator@master/taxcalc/"
        + "reforms/ext.json"
    )
    ref = Calculator.read_json_param_objects(reform_url, None)
    iit_reform = ref["policy"]

    # create new Specifications object for reform simulation
    p2 = Specifications(
        baseline=False,
        num_workers=num_workers,
        baseline_dir=base_dir,
        output_base=reform_dir,
    )
    # Update parameters for baseline from default json file
    p2.update_specifications(
        json.load(
            open(
                os.path.join(
                    CUR_DIR, "..", "ogusa", "ogusa_default_parameters.json"
                )
            )
        )
    )
    p2.tax_func_type = "GS"
    p2.age_specific = False
    # Use calibration class to estimate reform tax functions from
    # Tax-Calculator, specifying reform for Tax-Calculator in iit_reform
    c2 = Calibration(
        p2, iit_reform=iit_reform, estimate_tax_functions=True, client=client
    )
    # close and delete client bc cache is too large
    client.close()
    del client
    client = Client(n_workers=num_workers, threads_per_worker=1)
    # update tax function parameters in Specifications Object
    d = c2.get_dict()
    # # additional parameters to change
    updated_params = {
        "start_year": 2026,
        "etr_params": d["etr_params"],
        "mtrx_params": d["mtrx_params"],
        "mtry_params": d["mtry_params"],
        "mean_income_data": d["mean_income_data"],
        "frac_tax_payroll": d["frac_tax_payroll"],
    }
    if rho_G is not None:
        updated_params["rho_G"] = rho_G
    if g_y_annual is not None:
        updated_params["g_y_annual"] = g_y_annual
    p2.update_specifications(updated_params)

    # Run model
    start_time = time.time()
    runner(p2, time_path=True, client=client)
    print("run time = ", time.time() - start_time)
    client.close()

    """
    ------------------------------------------------------------------------
    Save some results of simulations
    ------------------------------------------------------------------------
    """
    base_tpi = safe_read_pickle(os.path.join(base_dir, "TPI", "TPI_vars.pkl"))
    base_params = safe_read_pickle(os.path.join(base_dir, "model_params.pkl"))
    reform_tpi = safe_read_pickle(
        os.path.join(reform_dir, "TPI", "TPI_vars.pkl")
    )
    reform_params = safe_read_pickle(
        os.path.join(reform_dir, "model_params.pkl")
    )
    ans = ot.macro_table(
        base_tpi,
        base_params,
        reform_tpi=reform_tpi,
        reform_params=reform_params,
        var_list=["Y", "C", "K", "L", "r", "w"],
        output_type="pct_diff",
        num_years=10,
        start_year=base_params.start_year,
    )

    # create plots of output
    op.plot_all(
        base_dir,
        reform_dir,
        os.path.join(CUR_DIR, example_dir, "plots_and_tables"),
    )
    # Create CSV file with output
    ot.tp_output_dump_table(
        base_params,
        base_tpi,
        reform_params,
        reform_tpi,
        table_format="csv",
        path=os.path.join(
            CUR_DIR, example_dir, "plots_and_tables", "macro_time_series_output.csv",
        ),
    )

    print("Percentage changes in aggregates:", ans)
    # save percentage change output to csv file
    ans.to_csv(
        os.path.join(
            CUR_DIR, example_dir, "plots_and_tables", "ogusa_example_output.csv"
        )
    )


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--rho_G", help="Budget closure rule smoothing parameter")
    parser.add_argument("--g_y_annual", help="Growth rate of labor augmenting technological progress")
    args = parser.parse_args()

    main(args.rho_G, args.g_y_annual)
