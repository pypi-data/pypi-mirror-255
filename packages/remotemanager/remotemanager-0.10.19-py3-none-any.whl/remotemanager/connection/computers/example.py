from remotemanager.connection.computers.base import BaseComputer, required, optional
from remotemanager.connection.computers.parsers import torque, slurm


class Example_Torque(BaseComputer):
    """
    example class for connecting to a remote computer using a torque scheduler
    """

    def __init__(self, **kwargs):
        if "host" not in kwargs:
            kwargs["host"] = "remote.address.for.connection"

        super().__init__(**kwargs)

        self.submitter = "qsub"
        self.shebang = "#!/bin/bash"
        self._parser = torque

        self.mpi = required("ppn")
        self.omp = required("omp")
        self.nodes = required("nodes")
        self.queue = required("q")
        self.time = required("walltime")
        self.jobname = optional("N")
        self.outfile = optional("o")
        self.errfile = optional("e")

        self._internal_extra = ""


class Example_Slurm(BaseComputer):
    """
    example class for connecting to a remote computer using a slurm scheduler
    """

    def __init__(self, **kwargs):
        if "host" not in kwargs:
            kwargs["host"] = "remote.address.for.connection"

        super().__init__(**kwargs)

        self.submitter = "sbatch"
        self.shebang = "#!/bin/bash"
        self._parser = slurm

        self.mpi = required("ntasks")
        self.omp = required("cpus-per-task")
        self.nodes = required("nodes")
        self.queue = required("queue")
        self.time = required("walltime")
        self.jobname = optional("job-name")
        self.outfile = optional("output")
        self.errfile = optional("error")
