from ipykernel.kernelapp import IPKernelApp
from .juptyer_cobol_kernel import COBOLKernel
IPKernelApp.launch_instance(kernel_class=COBOLKernel)
