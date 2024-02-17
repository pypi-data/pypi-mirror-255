def slurm(resources: dict) -> list:
    """
    Example parser for a slurm based computer

    Args:
        resources:
            resources dictionary, provided by BaseComputer
    Returns:
        list of resource request lines
    """
    from remotemanager.connection.computers.base import format_time

    output = []
    for k, v in resources.items():
        if k == "time":
            formatted = format_time(v.value)
            output.append(f"#SBATCH --{v.flag}={formatted}")

        elif v:
            output.append(f"#SBATCH --{v.flag}={v.value}")

    return output


def torque(resources: dict) -> list:
    """
    Example parser for a torque based computer

    Args:
        resources:
            resources dictionary, provided by BaseComputer
    Returns:
        list of resource request lines
    """
    from remotemanager.connection.computers.base import format_time

    output = []
    for k, v in resources.items():
        if k in ["mpi", "omp", "nodes", "time"]:
            continue
        if v:
            output.append(f"#PBS -{v.flag} {v.value}")
    # this sort is unnecessary in a real parser, it's just here to help the CI tests
    output = sorted(output)

    output.append(
        f"#PBS -l nodes={resources['nodes'].value}:"
        f"ppn={resources['mpi'].value},"
        f"walltime={format_time(resources['time'].value)}"
    )

    output.append("\ncd $PBS_O_WORKDIR")
    output.append(f"export OMP_NUM_THREADS={resources['omp']}")

    return output
