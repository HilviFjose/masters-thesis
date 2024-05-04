import numpy as np
import multiprocessing as mp
from typing import Callable
from config.main_config import num_of_paralell_iterations

def process_parallel(job_processor: Callable, function_kwargs: dict, jobs: list, mp_config: dict, paralellNum: int, profile = False):
    """Processes a set of jobs in parallel

    Args:
        job_processor (Callable): The function used to process jobs
        function_kwargs (dict): Arguments to pass to job_processor
        jobs (list): Jobs to be processed
        mp_config (dict): Multiprocessing config

    Returns:
        list: List of results of processed jobs
    """
    #parallel, n_processes = process_in_parallel(n_jobs=len(jobs), **mp_config)

    #if parallel:
    #n_processes = mp_config['max_processes']
    n_processes = paralellNum 
    avg_length = len(jobs) // n_processes
    remainder = len(jobs) % n_processes

    workloads = [jobs[i * avg_length + min(i, remainder):(i + 1) * avg_length + min(i + 1, remainder)] for i in range(n_processes)]

    arg_tuples = [(job_processor, workloads[i], function_kwargs) for i in range(n_processes)]

    with mp.Pool(processes=n_processes) as pool:
        res = pool.starmap_async(function_wrapper, arg_tuples)
        res.wait()
        result = res.get()
        results = [item for sublist in result for item in sublist]
        return results
'''  
def process_parallel_withFullCpu(job_processor: Callable, function_kwargs: dict, jobs: list, mp_config: dict, paralellNum: int, profile = False):
    """Processes a set of jobs in parallel

    Args:
        job_processor (Callable): The function used to process jobs
        function_kwargs (dict): Arguments to pass to job_processor
        jobs (list): Jobs to be processed
        mp_config (dict): Multiprocessing config

    Returns:
        list: List of results of processed jobs
    """
    #parallel, n_processes = process_in_parallel(n_jobs=len(jobs), **mp_config)

    #if parallel:
    #n_processes = mp_config['max_processes']
    n_processes = paralellNum 
    avg_length = len(jobs) // n_processes
    remainder = len(jobs) % n_processes

    workloads = [jobs[i * avg_length + min(i, remainder):(i + 1) * avg_length + min(i + 1, remainder)] for i in range(n_processes)]

    arg_tuples = [(job_processor, workloads[i], function_kwargs) for i in range(n_processes)]

    with mp.Pool(processes=n_processes) as pool:
        res = pool.starmap_async(function_wrapper, arg_tuples)
        res.wait()
        result = res.get()
        results = [item for sublist in result for item in sublist]
        return results
'''     
def setup(t0: float, tn: float, tj: float) -> dict:
    """Sets up multiprocessing

    Args:
        t0 (float): Time to initialize one process
        tn (float): Time per extra jobs initialized
        tj (float): Time to compute one job

    Returns:
        dict: Configuration that can be passed as mp_config
    """
    print()
    print('Using multiprocessing')
    max_processes = mp.cpu_count()
    print('Multiprocess configuration:')
    print('Number of processes:'.ljust(30) + str(max_processes).rjust(10))
    if not (mp.get_start_method() == 'spawn'):
        try:
            mp.set_start_method('spawn')
        except RuntimeError:
            pass
    print('Multiprocessing start method:'.ljust(30) + str(mp.get_start_method()).rjust(10))
    print()
    return {
            "t0": t0,
            "tn": tn,
            "tj": tj,
            "max_processes": max_processes
        }

def function_wrapper(function: Callable, jobs: list, kwargs: dict) -> list:
    """Wrapper for multiprocessing

    Args:
        function (Callable): Function to call
        jobs (list): List of jobs to be processed
        kwargs (dict): Arguments to pass to function

    Returns:
        list: List of results of processed jobs
    """
    return [function(job, **kwargs) for job in jobs]    

def t_parallel(t0, tn, n_jobs, tj, n):
    """Calculates time required to process jobs in parallel

    Args:
        t0 (float): Setup time for first job
        tn (float): Setup time for extra jobs
        n_jobs (int): Number of jobs to compute
        tj (float): Computation time per job
        n (int): Number of processes

    Returns:
        float: Total computation time
    """
    return t0 + tn*(n - 1) + (n_jobs/n) * tj

def processing_times(max_processes: int, t0: float, tn: float, n_jobs: int, tj: float) -> float:
    """Returns processing times from 2 to max_processes processes

    Args:
        max_processes (int): Max number of processes
        t0 (float): Setup time for first job
        tn (float): Setup time for extra jobs
        n_jobs (int): Number of jobs to compute
        tj (float): Computation time per job

    Returns:
        float: Processing times for jobs from 2 to max_processes processes
    """
    return [t_parallel(t0, tn, n_jobs, tj, n) for n in range(2, max_processes + 1)]

def process_in_parallel(max_processes: int, t0: float, tn: float, n_jobs: int, tj: float) -> tuple[bool, int]:
    """Decides whether to process in parallel, and how many processes to run

    Args:
        max_processes (int): Max number of processes
        t0 (float): Setup time for first job
        tn (float): Setup time for extra jobs
        n_jobs (int): Number of jobs to compute
        tj (float): Computation time per job

    Returns:
        tuple[bool, int]: Whether to process in parallel, and how many processes to run
    """
    t_parallels = processing_times(max_processes, t0, tn, n_jobs, tj)
    t_serial = n_jobs * tj

    if np.amin(t_parallels) < t_serial:
        return True, np.argmin(t_parallels) + 1
    else:
        return False, 1
