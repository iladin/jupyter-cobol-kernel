# %%
from ipykernel.kernelbase import Kernel


class COBOLKernel(Kernel):
    implementation = 'jupyter_COBOL_kernel'
    implementation_version = '0.1'
    language = 'COBOL'

    def __init__(self, *args, **kwargs):
        super(COBOLKernel, self).__init__(*args, **kwargs)
        self.files = []
        mastertemp = tempfile.mkstemp(suffix='.out')
        os.close(mastertemp[0])
        self.master_path = mastertemp[1]
        filepath = path.join(path.dirname(
            path.realpath(__file__)), 'resources', 'master.c')
        subprocess.call(['cobc', filepath, '-o', self.master_path])
# %%
!pip install - U autopep8 - -user
