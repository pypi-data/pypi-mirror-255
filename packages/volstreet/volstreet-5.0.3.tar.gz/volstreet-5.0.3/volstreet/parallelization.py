from joblib import Parallel, delayed


def execute_in_parallel(tasks, n_jobs=-1):
    """
    Executes tasks in parallel using joblib's Parallel and delayed functions.

    Parameters:
    tasks: List of tasks where each task is either:
           1. A tuple with the first element being a function and the second element being a tuple of arguments.
           2. A callable function that encapsulates all its required arguments.
    n_jobs: Number of jobs to run in parallel. -1 means using all processors.

    Returns:
    List of results corresponding to each task.
    """
    results = Parallel(n_jobs=n_jobs)(
        delayed(task[0])(*task[1]) if isinstance(task, tuple) else delayed(task)()
        for task in tasks
    )
    return results
