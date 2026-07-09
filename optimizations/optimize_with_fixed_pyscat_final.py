#!/usr/bin/env python3

import mpi4py
import uuid
import pypesto
import pathlib
import re
import amici
import pypesto.petab
from pypesto.store import save_to_hdf5
import pypesto.optimize
import petab
import pypesto.logging
import logging
import argparse
import numpy as np
from datetime import date, datetime
import fides
import sys
import os
import mpi4py
import time
from mpi4py import MPI
from pypesto.engine.mpi_pool import MPIPoolEngine
from pypesto.history import Hdf5History
from pyscat import (
    SacessOptions,
    SacessOptimizer,
    get_default_ess_options,
    SacessCmaFactory,
    SacessFidesFactory,
    SacessIpoptFactory,
)


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
    walltime,
    nworkers,
    precompile,
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
        amici.SteadyStateComputationMode.integrationOnly
    )

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
            amici.SteadyStateComputationMode.integrationOnly
        )

    print(f"MPI_COMM_WORLD: {mpi4py.MPI.COMM_WORLD.Get_size()}")
    option = pypesto.optimize.OptimizeOptions(allow_failed_starts=False)

    problem = importer.create_problem(objective, force_compile=precompile)

    # if precompile:
    #    sys.exit(0)

    optimizer = get_optimizer(
        algorithm_name,
        problem,
        walltime,
        nworkers,
        os.path.splitext(os.path.basename(yaml_file))[0],
    )

    result = None
    if type(optimizer) == SacessOptimizer:
        result = optimizer.minimize()

        history_dir = f"/workspace/{yaml_file}/{algorithm_name}/{name_run}_history"
        for history_index, history in enumerate(optimizer.histories):
            Hdf5History.from_history(
                other=history,
                file=f"{history_dir}_index_{history_index}.hdf5",
                id_=str(history_index),
            )

    return problem, result


def get_optimizer(
    optimizer_name,
    problem,
    problem_difficulty=9,
    num_workers=11,
    name_of_model="merged",
):
    """Return pyPESTO optimizer"""
    method = None
    local_optim = None

    ess_init_args = get_default_ess_options(num_workers=num_workers, dim=problem.dim)
    if optimizer_name.startswith("sacess_"):
        local_optim = optimizer_name.split("_")[1]
        if local_optim.startswith("nlopt"):
            local_optim = "_".join(optimizer_name.split("_")[1:3])
        optimizer_name = optimizer_name.split("_")[0]
    else:
        local_optim = False
        optimizer_name = "sacess"

    wall_time_for_sacess = 60 * 60 * problem_difficulty

    local_optimizer = None
    if optimizer_name.startswith("sacess"):
        if local_optim:
            if local_optim == "ipopt":
                local_optimizer = SacessIpoptFactory(
                    ipopt_options={"max_wall_time": wall_time_for_sacess}
                )

            if local_optim == "cmaes":
                local_optimizer = SacessCmaFactory(
                    options={"timeout": wall_time_for_sacess}
                )

            if local_optim == "fides":
                local_optimizer = SacessFidesFactory(
                    fides_kwargs={"hessian_update": fides.BFGS()}
                )

            if local_optim.startswith("nlopt"):
                local_optimizer = pypesto.optimize.NLOptimizer(
                    method=int(local_optim.split("_")[1])
                )
            else:
                if (
                    local_optim == "ipopt"
                    or local_optim == "cmaes"
                    or local_optim == "fides"
                ):
                    # already set to ipopt, cmaes, or fides
                    pass
                else:
                    # scipy optimizers go then here
                    local_optimizer = pypesto.optimize.ScipyOptimizer(
                        method=local_optim
                    )

    sacess_output_name = f"{optimizer_name}_{local_optim}"
    if not local_optim:
        sacess_output_name = f"{optimizer_name}"

    # wall_time_for_sacess = 3*60 # 2 minutes

    sacess_optimizer = SacessOptimizer(
        num_workers=num_workers,
        problem=problem,
        max_walltime_s=wall_time_for_sacess,
        autosave_dir=pathlib.Path(
            f"/workspace/sacess_temp_dir/{name_of_model}/{sacess_output_name}/"
        ),
        options=SacessOptions(
            adaptation_min_evals=500, adaptation_sent_offset=10, adaptation_sent_coeff=5
        ),
    )
    sacess_optimizer.set_local_optimizer(local_optimizer)

    opt_all = {
        "sacess": sacess_optimizer,
        #               'sacess' : SacessOptimizer(problem=problem, max_walltime_s=wall_time_for_sacess, tmpdir = f"/workspace/sacess_temp_dir/{name_of_model}/{optimizer_name}_{local_optim}/", ess_init_args=ess_init_args, options=SacessOptions(adaptation_min_evals=500, adaptation_sent_offset=10, adaptation_sent_coeff=5)),
        "L-BFGS-B": pypesto.optimize.ScipyOptimizer(
            method="L-BFGS-B", options={"disp": False}
        ),
        "SLSQP": pypesto.optimize.ScipyOptimizer(
            method="SLSQP", options={"disp": False}
        ),
        "fides": pypesto.optimize.FidesOptimizer(
            options={}, hessian_update=fides.BFGS()
        ),
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
        "ipopt": pypesto.optimize.IpoptOptimizer(options={}),
        "ls_trf": pypesto.optimize.ScipyOptimizer(
            method="ls_trf", options={"disp": False}
        ),
    }

    if optimizer_name.startswith("nlopt"):
        method = int(optimizer_name.split("_")[1])
        optimizer_name = optimizer_name.split("_")[0]
        opt_all["nlopt"] = pypesto.optimize.NLOptimizer(method=method)

    return opt_all[optimizer_name]


def parse_cli_args():
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(description="Run pyPESTO optimization")

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


def save_results(result, problem, output_folder, yaml_file, algorithm_name, name_run):
    hdf5_writer = save_to_hdf5.OptimizationResultHDF5Writer(
        f"/workspace/{yaml_file}/{algorithm_name}/{name_run}_result.h5"
    )
    hdf5_writer.write(result, overwrite=True)


if __name__ == "__main__":
    args = parse_cli_args()

    petab_problem = petab.Problem.from_yaml(f"{args.petab_dir}/{args.yaml_file}.yaml")
    preprocess_problem(petab_problem, args.yaml_file)
    importer = pypesto.petab.PetabImporter(
        petab_problem, output_folder=f"{args.output_folder}/{args.yaml_file}"
    )

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
    hard_problem = any(hard in args.yaml_file for hard in hard_problems)
    nworkers = 11
    walltime = 1
    if hard_problem:
        nworkers = 23
        walltime = 9
    if args.algorithm_name.startswith("sacess"):
        precompile = args.precompile
        problem, result = run_optimization(
            importer,
            args.algorithm_name,
            args.output_folder_data,
            args.yaml_file,
            args.algorithm_name,
            int(args.num_starts),
            args.name_run,
            args.asa_or_fsa,
            walltime,
            nworkers,
            precompile,
        )
        save_results(
            result,
            problem,
            args.output_folder_data,
            args.yaml_file,
            args.algorithm_name,
            args.name_run,
        )
    else:
        run_optimization(
            importer,
            args.algorithm_name,
            args.output_folder_data,
            args.yaml_file,
            args.algorithm_name,
            int(args.num_starts),
            args.name_run,
            args.asa_or_fsa,
            walltime,
            nworkers,
            args.precompile,
        )
