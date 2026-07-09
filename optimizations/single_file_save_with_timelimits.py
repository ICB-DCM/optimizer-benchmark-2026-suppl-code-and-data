#!/usr/bin/env python3

import mpi4py
import pypesto
import re
import amici
import pypesto.petab
import pypesto.optimize
import petab
import pypesto.logging
import logging
import argparse
import numpy as np
from datetime import date, datetime
import fides
import nlopt
import sys
import os
import mpi4py
import time
from mpi4py import MPI
from pypesto.engine.mpi_pool import MPIPoolEngine

import cyipopt


def check_versions():
    """Check for required versions"""
    if (
        amici.__version__ != "0.2.18"
        or petab.__version__ != "0.5.0"
        or fides.__version__ != "0.7.8"
    ):
        print("Version mismatch... Aborting execution.")
        return False
    return True


def preprocess_problem(problem, model) -> None:
    """
    Preprocess benchmark models
    Parameters
    ----------
    :problem:
        PEtab model problem
    :model:
        name of model
    """
    if re.match("Weber", model):
        # don't estimate certain standard deviation parameters for Weber model
        problem.parameter_df.loc[
            ["std_yPKDt", "std_yPI4K3Bt", "std_yCERTt"], petab.ESTIMATE
        ] = 0

    if model in [
        "Brannmark_JBC2010",
        "Fiedler_BMCSystBiol2016",
        "Borghans_BiophysChem1997",
    ]:
        # timepoint specific overrides are needed to be overriden for some models
        petab.flatten_timepoint_specific_output_overrides(problem)


def run_optimization(
    importer,
    optimizer,
    output_folder,
    yaml_file,
    algorithm_name,
    num_starts,
    name_run,
    asa_or_fsa,
    precompile,
    output_file,
    walltime,
):
    """Run optimization"""
    pypesto.logging.log_to_console(logging.INFO)
    objective = importer.create_objective(guess_steadystate=False)

    # default is FSA unless specified as ASA
    objective.amici_solver.setSensitivityMethod(amici.SensitivityMethod_forward)
    objective.amici_solver.setSensitivityMethodPreequilibration(
        amici.SensitivityMethod_forward
    )
    objective.amici_model.setSteadyStateSensitivityMode(
        amici.SteadyStateSensitivityMode.integrationOnly
    )
    objective.amici_model.setSteadyStateComputationMode(
        amici.SteadyStateSensitivityMode.integrationOnly
    )

    # for dogleg trust-ncg and trust-krylov only FSA
    # or request ASA
    if asa_or_fsa == "ASA":
        objective.amici_solver.setSensitivityMethod(amici.SensitivityMethod_adjoint)
        objective.amici_solver.setSensitivityMethodPreequilibration(
            amici.SensitivityMethod_adjoint
        )
        objective.amici_model.setSteadyStateSensitivityMode(
            amici.SteadyStateSensitivityMode.integrationOnly
        )
        objective.amici_model.setSteadyStateComputationMode(
            amici.SteadyStateSensitivityMode.integrationOnly
        )

    # print(objective.amici_solver.getAbsoluteToleranceFSA())
    # print(objective.amici_solver.getAbsoluteToleranceASA())
    # print(objective.amici_solver.getRelativeTolerance())

    print(f"MPI_COMM_WORLD: {mpi4py.MPI.COMM_WORLD.Get_size()}")
    option = pypesto.optimize.OptimizeOptions(
        allow_failed_starts=True
    )  # used only for dogleg trust-ncg trust-krylov
    # history_name = f"/lustre/mlnvme/data/sgrein_hpc-benchmark_test/parallel_test3/{yaml_file}/{algorithm_name}/{name_run}_id={{id}}.h5"
    import os

    # print(f"Is directory: {os.path.isdir('app/data/parallel_test3/')}")
    # folders = next(os.walk('/'))[1]
    # print("folders:")
    # print(folders)
    # print(f"Is directory: {os.path.isdir('/workspace/')}")
    # folders = next(os.walk('/workspace/'))[1]
    # import glob
    # print("folders:")
    # print(glob.glob("/workspace/*"))
    # print(glob.glob("/workspace/Brannmark_JBC2010/*"))

    # for apptainer runs exchange history file definition
    history_name = f"/workspace/{yaml_file}/{algorithm_name}/{name_run}_id={{id}}.h5"

    # history_name = "/lustre/mlnvme/data/sgrein_hpc-benchmark_test/debug_Boehm/Boehm_JProteomeRes2014/BFGS/run_test_id={{id}}.h5"
    hist_options = pypesto.HistoryOptions(
        trace_record=True,
        trace_record_grad=True,
        trace_record_hess=False,
        trace_record_res=False,
        trace_record_sres=False,
        storage_file=None,
    )

    # for test without apptainer
    # engine = pypesto.engine.mpi_pool.MPIPoolEngine()

    # create problem anew (once)
    problem = importer.create_problem(objective, force_compile=precompile)

    if precompile:
        sys.exit(0)

    # minimize with new method saving the history of each multi start to a .h5 file
    # This uses the branch reduce_storage from stephanmg/pyPESTO on Github to reduce memory storage and disallow idling of CPUs in parallel multi starts
    # for apptainer with minimize_new
    print("here, starting optimization")
    result = pypesto.optimize.minimize_new(
        problem=problem,
        n_starts=num_starts,
        optimizer=optimizer,
        options=option,
        history_options=hist_options,
        filename=f"/workspace/{yaml_file}/{algorithm_name}/{output_file}",
        interval=1,
        wall_time_limit=walltime,
    )
    print("done?")
    return problem, result


def get_optimizer(optimizer_name):
    """Return pyPESTO optimizer"""
    if optimizer_name.startswith("nlopt"):
        method = int(optimizer_name.split("_")[1])
        optimizer_name = optimizer_name.split("_")[0]
    else:
        print(f"Optimizer not found with name: {optimizer_name}")
        method = None

    opt_all = {
        "L-BFGS-B": pypesto.optimize.ScipyOptimizer(
            method="L-BFGS-B", options={"disp": False}
        ),
        "SLSQP": pypesto.optimize.ScipyOptimizer(
            method="SLSQP", options={"disp": False}
        ),
        "fides": pypesto.optimize.FidesOptimizer(
            options={}, hessian_update=fides.BFGS()
        ),
        "nlopt": pypesto.optimize.NLoptOptimizer(method=method),
        "tnc": pypesto.optimize.ScipyOptimizer(method="TNC", options={"disp": False}),
        "newton-cg": pypesto.optimize.ScipyOptimizer(
            method="Newton-CG", options={"disp": False}
        ),
        "cg": pypesto.optimize.ScipyOptimizer(method="cg", options={"disp": False}),
        "BFGS": pypesto.optimize.ScipyOptimizer(method="BFGS", options={"disp": False}),
        "trust-krylov": pypesto.optimize.ScipyOptimizer(
            method="trust-krylov", options={"disp": False}
        ),
        "trust-ncg": pypesto.optimize.ScipyOptimizer(
            method="trust-ncg", options={"disp": False}
        ),
        "dogleg": pypesto.optimize.ScipyOptimizer(
            method="dogleg", options={"disp": False}
        ),
        "Powell": pypesto.optimize.ScipyOptimizer(
            method="Powell", options={"disp": False}
        ),
        "COBYLA": pypesto.optimize.ScipyOptimizer(
            method="COBYLA", options={"disp": False}
        ),
        "Nelder-Mead": pypesto.optimize.ScipyOptimizer(
            method="Nelder-Mead", options={"disp": False}
        ),
        "least_squares": pypesto.optimize.ScipyOptimizer(
            method="least_squares", options={"disp": False}
        ),
        "pyswarm": pypesto.optimize.PyswarmOptimizer(options={}),
        "cmaes": pypesto.optimize.CmaOptimizer(options={}),
        "ipopt": pypesto.optimize.IpoptOptimizer(options={"print_level": 12}),
        "ls_trf": pypesto.optimize.ScipyOptimizer(
            method="ls_trf", options={"disp": False}
        ),
    }

    return opt_all[optimizer_name]


def parse_cli_args():
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(description="Run pyPESTO optimization")

    parser.add_argument("-z", dest="output_file")

    parser.add_argument(
        "-d", "--petab-dir", dest="petab_dir", help="Directory of the PEtab model"
    )

    parser.add_argument(
        "-y",
        "--yaml-file",
        dest="yaml_file",
        required=True,
        help="Name of the yaml model",
    )

    parser.add_argument(
        "-a",
        "--algorithm",
        dest="algorithm_name",
        required=True,
        help="Algorithm used for optimization",
    )

    parser.add_argument(
        "-s",
        "--num-starts",
        dest="num_starts",
        required=True,
        help="Number of multistarts",
    )

    parser.add_argument(
        "-o",
        "--output-folder-model",
        dest="output_folder",
        required=True,
        help="Folder to write compiled AMICI models",
    )

    parser.add_argument(
        "-x",
        "--output-folder-data",
        dest="output_folder_data",  # was -m
        required=False,
        help="Folder to write optimization results",
    )

    parser.add_argument(
        "-n",
        "--name-run",
        dest="name_run",
        required=False,
        default=False,
        help="Name run",
    )

    parser.add_argument("--asa-or-fsa", dest="asa_or_fsa", required=True)

    parser.add_argument("--precompile", dest="precompile", required=False)

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    print("versions:")
    print(pypesto.__version__)
    print(amici.__version__)
    # sys.exit(0)
    # if not check_versions():
    #    sys.exit(0)

    args = parse_cli_args()

    petab_problem = petab.Problem.from_yaml(f"{args.petab_dir}/{args.yaml_file}.yaml")
    preprocess_problem(petab_problem, args.yaml_file)
    importer = pypesto.petab.PetabImporter(
        petab_problem, output_folder=f"{args.output_folder}/{args.yaml_file}"
    )

    # get optimizer
    optimizer = get_optimizer(args.algorithm_name)

    # set walltime depending on problem class
    hard_problems = [
        "Alkan",
        "Bachmann",
        "Beer",
        "Chen",
        "Fujita",
        "Isensee",
        "Lucarelli",
        "Raimundez",
        "Zheng",
        "Froehlich",
        "Lang",
    ]
    walltime = 3.0 * 60 * 60
    hard_problem = any(hard in args.yaml_file for hard in hard_problems)
    if hard_problem:
        walltime = 9.0 * 60 * 60

    # set walltime for optimizer which support it
    if optimizer.supports_maxtime():
        optimizer.set_maxtime(walltime)

    run_optimization(
        importer,
        optimizer,
        args.output_folder_data,
        args.yaml_file,
        args.algorithm_name,
        int(args.num_starts),
        args.name_run,
        args.asa_or_fsa,
        args.precompile,
        args.output_file,
        walltime,
    )
