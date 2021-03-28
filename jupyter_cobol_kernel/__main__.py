from ipykernel.kernelapp import IPKernelApp
from . import jupyter_cobol_kernel
IPKernelApp.launch_instance(kernel_class=jupyter_cobol_kernel.COBOLKernel)
