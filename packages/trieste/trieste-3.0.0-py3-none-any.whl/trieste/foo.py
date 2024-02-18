from gpflow.kernels import MultioutputKernel, Kernel


def foo(k: Kernel) -> int:
    if isinstance(k, MultioutputKernel):
        return 1
    else:
        return 2

