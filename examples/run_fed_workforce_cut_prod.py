import multiprocessing
from distributed import Client
import os, argparse
import json
import time
import importlib.resources
import copy
from taxcalc import Calculator
import matplotlib.pyplot as plt
from ogusa.calibrate import Calibration
from ogcore.parameters import Specifications
from ogcore import output_tables as ot
from ogcore import output_plots as op
from ogcore.execute import runner
from ogcore.utils import safe_read_pickle

def main(num_years, overwrite):
    # Directories to save data
    CUR_DIR = os.path.dirname(os.path.realpath(__file__))

    base_dir = os.path.join(CUR_DIR, "Current_Law", "OUTPUT")
    # need to correct one base policy error
    # base_policy = {
    #     "ALD_DomesticProduction_hc": {"2026": 1.00}
    # }
    # iit_baseline = base_policy

    reform_dir = os.path.join(CUR_DIR, "Prod_Level_Gain_"+str(num_years)+"_yrs", "OUTPUT")

    if os.path.exists(reform_dir) and not overwrite:
        print('Already did ' + reform_dir + '. Skip!')

    else:
        if os.path.exists(reform_dir) and overwrite:
            print('Already did ' + reform_dir + ', but overwriting...')
        else:
            print('Have not done ' + reform_dir + ', and now doing...')
            
        # Define parameters to use for multiprocessing
        num_workers = multiprocessing.cpu_count() - 2
        client = Client(n_workers=num_workers, threads_per_worker=1)
        print("Number of workers = ", num_workers)

        """
        ------------------------------------------------------------------------
        Run reform policy
        ------------------------------------------------------------------------
        """
        # create new Specifications object for reform simulation
        p2 = Specifications(
            baseline=False,
            num_workers=num_workers,
            baseline_dir=base_dir,
            output_base=reform_dir,
        )
        # Update parameters for baseline from default json file
        with importlib.resources.open_text(
            "ogusa", "ogusa_default_parameters.json"
        ) as file:
            defaults = json.load(file)
        p2.update_specifications(defaults)
        p2.tax_func_type = "GS"
        p2.age_specific = False

        # Use calibration class to estimate reform tax functions from
        # Tax-Calculator, specifying reform for Tax-Calculator in iit_reform
        # c2 = Calibration(
        #     p2, iit_baseline=iit_baseline, iit_reform=iit_reform, estimate_tax_functions=True, data='tmd', client=client
        # )
        c2 = Calibration(
            p2, estimate_tax_functions=True, data='tmd', client=client
        )
        # update tax function parameters in Specifications Object
        d = c2.get_dict()
        # additional parameters to change
        updated_params = {
            "start_year": 2025,
            "RC_TPI": 100*1e-4,
            "etr_params": d["etr_params"],
            "mtrx_params": d["mtrx_params"],
            "mtry_params": d["mtry_params"],
            "mean_income_data": d["mean_income_data"],
            "frac_tax_payroll": d["frac_tax_payroll"],
        }

        if int(num_years)==1:
            updated_params["Z"] = [[1.000249791]]
            print("doing 1 years......")
        elif int(num_years)==4:
            updated_params["Z"] = [[1.000249791], [1.000474247], [1.000675969], [1.000857287]]
            print("doing 4 years......")
        else:
            print("NOT CHANGING Z!!!")
        updated_params["baseline_spending"] = True
        p2.update_specifications(updated_params)
        
        # Run model
        start_time = time.time()
        runner(p2, time_path=True, client=client)
        print("run time = ", time.time() - start_time)
        client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_years", help="Number of years federal workforce is cut by 10%, either 1 or 4")
    parser.add_argument("--overwrite", help="Whether to overwrite existing run")
    args = parser.parse_args()
    main(args.num_years, args.overwrite)