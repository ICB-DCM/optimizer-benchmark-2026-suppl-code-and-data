#!/usr/bin/env python3

import os
import logging
import re
import argparse
from datetime import date, datetime
import sys
import time

import mpi4py

from mpi4py import MPI

import cyipopt

import pypesto
import amici
import pypesto.petab
import pypesto.optimize
import petab
import pypesto.logging
import numpy as np
import fides
import nlopt
from pypesto.engine.mpi_pool import MPIPoolEngine

print(f"Start time stamp: {time.time()}")

def check_versions():
    """ Check for required versions """
    if amici.__version__ != "0.30.1" or petab.__version__ != "0.5.0" or fides.__version__ != "0.7.8":
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
            ['std_yPKDt', 'std_yPI4K3Bt', 'std_yCERTt'],
            petab.ESTIMATE
        ] = 0
    
    if model in ['Brannmark_JBC2010', 'Fiedler_BMCSystBiol2016', 'Borghans_BiophysChem1997']:
        # timepoint specific overrides are needed to be overriden for some models
        petab.flatten_timepoint_specific_output_overrides(problem)


def run_optimization(importer, optimizer, output_folder, yaml_file, algorithm_name, num_starts, name_run, asa_or_fsa, precompile, output_file, walltime):
    """Run optimization"""
    pypesto.logging.log_to_console(logging.INFO)
    objective = importer.create_objective(guess_steadystate=False)

    # default is FSA unless specified as ASA
    objective.amici_solver.setSensitivityMethod(amici.SensitivityMethod_forward)
    objective.amici_solver.setSensitivityMethodPreequilibration(amici.SensitivityMethod_forward)
    objective.amici_model.setSteadyStateSensitivityMode(amici.SteadyStateSensitivityMode.integrationOnly)
    objective.amici_model.setSteadyStateComputationMode(amici.SteadyStateSensitivityMode.integrationOnly)

    # for dogleg trust-ncg and trust-krylov only FSA
    if algorithm_name in ["dogleg", "trust-ncg", "trust-krylov"]: 
        print(f"Using FSA for optimizer {optimizer}")
    else: 
        if asa_or_fsa == "ASA":
          objective.amici_solver.setSensitivityMethod(amici.SensitivityMethod_adjoint)
          objective.amici_solver.setSensitivityMethodPreequilibration(amici.SensitivityMethod_adjoint)
          objective.amici_model.setSteadyStateSensitivityMode(amici.SteadyStateSensitivityMode.integrationOnly)
          objective.amici_model.setSteadyStateComputationMode(amici.SteadyStateSensitivityMode.integrationOnly)


    print(f"MPI_COMM_WORLD: {mpi4py.MPI.COMM_WORLD.Get_size()}")
    option = pypesto.optimize.OptimizeOptions(allow_failed_starts=False)

    if algorithm_name in ["dogleg", "trust-ncg", "trust-krylov"]: 
        print(f"Using `allow_failed_starts=True` for optimizer {optimizer}")
        option = pypesto.optimize.OptimizeOptions(allow_failed_starts=True) 

    # for apptainer runs exchange history file definition
    history_name = f"/workspace/{yaml_file}/{algorithm_name}/{name_run}_id={{id}}.h5"

    hist_options = pypesto.HistoryOptions(trace_record=True, trace_record_grad=True, trace_record_hess=False, trace_record_res=False, trace_record_sres=False, storage_file=None)

    # create problem anew (once)
    problem = importer.create_problem(objective, force_compile=precompile)

    # precompile models non-parallel
    if precompile: sys.exit(0)

    # minimize with new method saving the history of each multi start to a .h5 file
    # This uses the branch reduce_storage from stephanmg/pyPESTO on Github to reduce memory storage and disallow idling of CPUs in parallel multi starts
    # for apptainer with minimize_new
    print(f"Start time stamp minimize_new: {time.time()}")
    result = pypesto.optimize.minimize_new(problem=problem,
                                       n_starts=num_starts,
                                       optimizer=optimizer,
                                       options=option,
                                       history_options=hist_options,
                                       filename=f"/workspace/{yaml_file}/{algorithm_name}/{output_file}",
                                       interval=1,
                                       wall_time_limit=walltime)

    print(f"End time stamp minimize_new: {time.time()}")
    return problem, result


def get_optimizer(optimizer_name):
    """Return pyPESTO optimizer"""
    if optimizer_name.startswith('nlopt'):
        method = int(optimizer_name.split('_')[1])
        optimizer_name = optimizer_name.split('_')[0]
    else:
        print(f"Optimizer not found with name: {optimizer_name}")
        method = None

    opt_all = {'L-BFGS-B': pypesto.optimize.ScipyOptimizer(method='L-BFGS-B',
                                                           options={'disp': False}),
               'SLSQP': pypesto.optimize.ScipyOptimizer(method='SLSQP',
                                                        options={'disp': False}),
               'fides': pypesto.optimize.FidesOptimizer(options={}, hessian_update=fides.BFGS()),
               'nlopt': pypesto.optimize.NLoptOptimizer(method=method),
               'tnc': pypesto.optimize.ScipyOptimizer(method='TNC', options={'disp': False}),
               'newton-cg': pypesto.optimize.ScipyOptimizer(method='Newton-CG', options={'disp': False}),
               'cg': pypesto.optimize.ScipyOptimizer(method='cg', options={'disp': False}),
               'BFGS': pypesto.optimize.ScipyOptimizer(method='BFGS', options={'disp': False}),
               'trust-krylov': pypesto.optimize.ScipyOptimizer(method='trust-krylov', options={'disp': False}),
               'trust-ncg': pypesto.optimize.ScipyOptimizer(method='trust-ncg', options={'disp': False}),
               'dogleg': pypesto.optimize.ScipyOptimizer(method='dogleg', options={'disp': False}),
               'Powell': pypesto.optimize.ScipyOptimizer(method='Powell', options={'disp': False}),
               'COBYLA': pypesto.optimize.ScipyOptimizer(method='COBYLA', options={'disp': False}),
               'Nelder-Mead': pypesto.optimize.ScipyOptimizer(method='Nelder-Mead', options={'disp': False}),
               'least_squares': pypesto.optimize.ScipyOptimizer(method='least_squares', options={'disp': False}),
               'pyswarm': pypesto.optimize.PyswarmOptimizer(options={}),
               'cmaes': pypesto.optimize.CmaOptimizer(options={}),
               'ipopt': pypesto.optimize.IpoptOptimizer(options={"print_level": 12}),
               'ls_trf': pypesto.optimize.ScipyOptimizer(method='ls_trf',
                                                        options={'disp': False}) }

    return opt_all[optimizer_name]


def parse_cli_args():
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(
        description='Run pyPESTO optimization')

    parser.add_argument('-z', dest="output_file")

    parser.add_argument('-d', '--petab-dir', dest='petab_dir',
                        help='Directory of the PEtab model')

    parser.add_argument('-y', '--yaml-file', dest='yaml_file',
                        required=True,
                        help='Name of the yaml model')

    parser.add_argument('-a', '--algorithm', dest='algorithm_name',
                        required=True,
                        help='Algorithm used for optimization')

    parser.add_argument('-s', '--num-starts', dest='num_starts',
                        required=True,
                        help='Number of multistarts')

    parser.add_argument('-o', '--output-folder-model', dest='output_folder',
                        required=True,
                        help='Folder to write compiled AMICI models')

    parser.add_argument('-x', '--output-folder-data', dest='output_folder_data', # was -m
                       required=False,
                       help="Folder to write optimization results")

    parser.add_argument('-n', '--name-run', dest='name_run',
                        required=False, default=False, help="Name run")

    parser.add_argument('--asa-or-fsa', dest='asa_or_fsa', required=True)

    parser.add_argument('--precompile', dest='precompile', required=False)

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    # check versions
    if not check_versions(): sys.exit(0)

    # get command line arguments
    args = parse_cli_args()

    # get problem
    petab_problem = petab.Problem.from_yaml(f'{args.petab_dir}/{args.yaml_file}.yaml')
    preprocess_problem(petab_problem, args.yaml_file)
    importer = pypesto.petab.PetabImporter(petab_problem, output_folder=f'{args.output_folder}/{args.yaml_file}')

    # get optimizer
    optimizer = get_optimizer(args.algorithm_name)

    # set walltime depending on problem class
    hard_problems = ['Alkan', 'Bachmann', 'Beer', 'Chen', 'Fujita', 'Isensee', 'Lucarelli', 'Raimundez', 'Zheng', 'Froehlich', 'Lang']
    walltime = 3.0 * 60 * 60
    hard_problem = any(hard in args.yaml_file for hard in hard_problems)
    if hard_problem: walltime = 9.0 * 60 * 60

    # set walltime for optimizer which supports it
    if optimizer.supports_maxtime(): optimizer.set_maxtime(walltime)

    # finally run optimization with walltime limit
    run_optimization(importer, optimizer, args.output_folder_data, args.yaml_file, args.algorithm_name, int(args.num_starts), args.name_run, args.asa_or_fsa, args.precompile, args.output_file, walltime)

    print(f"End time stamp: {time.time()}")
