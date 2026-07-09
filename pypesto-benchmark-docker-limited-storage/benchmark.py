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

def check_versions():
    """ Check for required versions """
    if amici.__version__ != "0.2.18" or petab.__version__ != "0.5.0" or fides.__version__ != "0.7.8":
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


def run_optimization(importer, optimizer, output_folder, yaml_file, algorithm_name, num_starts, name_run, asa_or_fsa, walltime):
    """Run optimization"""
    pypesto.logging.log_to_console(logging.INFO)
    objective = importer.create_objective(guess_steadystate=False)

    # default is FSA unless specified as ASA
    objective.amici_solver.setSensitivityMethod(amici.SensitivityMethod_forward)
    objective.amici_solver.setSensitivityMethodPreequilibration(amici.SensitivityMethod_forward)
    objective.amici_model.setSteadyStateSensitivityMode(amici.SteadyStateSensitivityMode.integrationOnly)
    objective.amici_model.setSteadyStateComputationMode(amici.SteadyStateSensitivityMode.integrationOnly)

    # or request ASA
    if asa_or_fsa == "ASA":
      objective.amici_solver.setSensitivityMethod(amici.SensitivityMethod_adjoint)
      objective.amici_solver.setSensitivityMethodPreequilibration(amici.SensitivityMethod_adjoint)
      objective.amici_model.setSteadyStateSensitivityMode(amici.SteadyStateSensitivityMode.integrationOnly)
      objective.amici_model.setSteadyStateComputationMode(amici.SteadyStateSensitivityMode.integrationOnly)


    print(f"MPI_COMM_WORLD: {mpi4py.MPI.COMM_WORLD.Get_size()}")
    option = pypesto.optimize.OptimizeOptions(allow_failed_starts=True)
    problem = importer.create_problem(objective, force_compile=False)
    problem.init_time = MPI.Wtime()

    print("Running parallel")
    #engine = pypesto.engine.mpi_pool.MPIPoolEngine()
    option.filename_path = output_folder + f'/{yaml_file}/' + f'{algorithm_name}/' + f'{asa_or_fsa}_' + f'{name_run}'
    option.timestamp = datetime.timestamp(datetime.now())

    os.makedirs( output_folder + f'/{yaml_file}/' + f'{algorithm_name}/' , exist_ok=True)
    np.random.seed(int(os.getpid()) + int(time.time()))
    

    result = pypesto.optimize.minimize(problem=problem, n_starts=num_starts, optimizer=optimizer, options=option, history_options=None, wall_time_limit=walltime)

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
               'ipopt': pypesto.optimize.IpoptOptimizer(options={}),
               'ls_trf': pypesto.optimize.ScipyOptimizer(method='ls_trf',
                                                        options={'disp': False}) }
                # 'verb_log': 0, 'maxiter': 1000 }),
    print(optimizer_name)

    return opt_all[optimizer_name]


def parse_cli_args():
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(
        description='Run pyPESTO optimization')

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
                       required=True,
                       help="Folder to write optimization results")

    parser.add_argument('-n', '--name-run', dest='name_run',
                        required=False, default=False, help="Name run")

    parser.add_argument('--asa-or-fsa', dest='asa_or_fsa', required=True)

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    #if not check_versions():
    #    sys.exit(0)
        
    args = parse_cli_args()

    petab_problem = petab.Problem.from_yaml(f'{args.petab_dir}/{args.yaml_file}.yaml')
    preprocess_problem(petab_problem, args.yaml_file)
    importer = pypesto.petab.PetabImporter(petab_problem, output_folder=f'{args.output_folder}/{args.yaml_file}')
    obj = importer.create_objective()

    print(obj.amici_solver.getAbsoluteTolerance())
    print(obj.amici_solver.getRelativeTolerance())   

    optimizer = get_optimizer(args.algorithm_name)
    hard_problems = ['Alkan', 'Bachmann', 'Beer', 'Chen', 'Fujita', 'Isensee', 'Lucarelli', 'Raimundez', 'Zheng', 'Froehlich', 'Lang']
    walltime = 3.0 * 60 * 60
    hard_problem = any(hard in args.yaml_file for hard in hard_problems)
    if hard_problem: walltime = 9.0 * 60 * 60

    # set walltime for optimizer which supports it
    if optimizer.supports_maxtime(): optimizer.set_maxtime(walltime)

    run_optimization(importer, optimizer, args.output_folder_data, args.yaml_file, args.algorithm_name, int(args.num_starts), args.name_run, args.asa_or_fsa, walltime
