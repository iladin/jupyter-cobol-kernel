# %%
from ipykernel.kernelbase import Kernel
from queue import Queue
from threading import Thread

import subprocess
import tempfile
import os
import os.path as path


class RealTimeSubprocess(subprocess.Popen):
    """
    A subprocess that allows to read its stdout and stderr in real time
    """

    inputRequest = "<inputRequest>"

    def __init__(self, cmd, write_to_stdout, write_to_stderr):
        """
        :param cmd: the command to execute
        :param write_to_stdout: a callable that will be called with chunks of data from stdout
        :param write_to_stderr: a callable that will be called with chunks of data from stderr
        """
        self._write_to_stdout = write_to_stdout
        self._write_to_stderr = write_to_stderr
        self._read_from_stdin = read_from_stdin


        super().__init__(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, bufsize=0)

        self._stdout_queue = Queue()
        self._stdout_thread = Thread(target=RealTimeSubprocess._enqueue_output, args=(self.stdout, self._stdout_queue))
        self._stdout_thread.daemon = True
        self._stdout_thread.start()

        self._stderr_queue = Queue()
        self._stderr_thread = Thread(target=RealTimeSubprocess._enqueue_output, args=(self.stderr, self._stderr_queue))
        self._stderr_thread.daemon = True
        self._stderr_thread.start()

    @staticmethod
    def _enqueue_output(stream, queue):
        """
        Add chunks of data from a stream to a queue until the stream is empty.
        """
        for line in iter(lambda: stream.read(4096), b''):
            queue.put(line)
        stream.close()

    def write_contents(self):
        """
        Write the available content from stdin and stderr where specified when the instance was created
        :return:
        """

        def read_all_from_queue(queue):
            res = b''
            size = queue.qsize()
            while size != 0:
                res += queue.get_nowait()
                size -= 1
            return res

        stdout_contents = read_all_from_queue(self._stdout_queue)
        if stdout_contents:
            self._write_to_stdout(stdout_contents)
        stderr_contents = read_all_from_queue(self._stderr_queue)
        if stderr_contents:
            self._write_to_stderr(stderr_contents)


class COBOLKernel(Kernel):
    implementation = 'jupyter_cobol_kernel'
    implementation_version = '0.1'
    language = 'COBOL'
    banner = "COBOL kernel.\n" \
             "Uses gnucobol, and creates source code files and executables in temporary folder.\n"
    def __init__(self, *args, **kwargs):
        super(COBOLKernel, self).__init__(*args, **kwargs)
        self.files = []
        mastertemp = tempfile.mkstemp(suffix='.out')
        os.close(mastertemp[0])
        self.master_path = mastertemp[1]
        filepath = path.join(path.dirname(
            path.realpath(__file__)), 'resources', 'master.c')
        subprocess.call(['cobc', filepath, '-o', self.master_path])

    def cleanup_files(self):
        """Remove all the temporary files created by the kernel"""
        # keep the list of files create in case there is an exception
        # before they can be deleted as usual
        for file in self.files:
            if(os.path.exists(file)):
                os.remove(file)
        os.remove(self.master_path)

    def new_temp_file(self, **kwargs):
        """Create a new temp file to be deleted when the kernel shuts down"""
        # We don't want the file to be deleted when closed, but only when the kernel stops
        kwargs['delete'] = False
        kwargs['mode'] = 'w'
        file = tempfile.NamedTemporaryFile(**kwargs)
        self.files.append(file.name)
        return file

    def _write_to_stdout(self, contents):
        self.send_response(self.iopub_socket, 'stream', {
                           'name': 'stdout', 'text': contents})

    def _write_to_stderr(self, contents):
        self.send_response(self.iopub_socket, 'stream', {
                           'name': 'stderr', 'text': contents})

    def _read_from_stdin(self):
        return self.raw_input()

    def create_jupyter_subprocess(self, cmd):
        return RealTimeSubprocess(cmd,
                                  self._write_to_stdout,
                                  self._write_to_stderr,
                                  self._read_from_stdin)
    def compile_with_cobc(self, source_filename, binary_filename, cobflags=None, ldflags=None):
        cobflags = [ '-x'] + cobflags
        args = [ 'cobc', source_filename] + cobflags + ['-o', binary_filename] + ldflags
        return self.create_jupyter_subprocess(args)


    def _filter_magics(self, code):

        magics = ({'cobflags': [],
                  'ldflags': [],
                  'args': []})

        actualCode = ''

        for line in code.splitlines():
            if line.startswith('//%'):
                key, value = line[3:].split(":", 2)
                key = key.strip().lower()

                if key in ['ldflags', 'cobflags']:
                    for flag in value.split():
                        magics[key] += [flag]
                elif key == "args":
                    # Split arguments respecting quotes
                    for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', value):
                        magics['args'] += [argument.strip('"')]

                # always add empty line, so line numbers don't change
                actualCode += '\n'

            # keep lines which did not contain magics
            else:
                actualCode += line + '\n'

        return magics, actualCode

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):

        magics = self._filter_magics(code)

        with self.new_temp_file(suffix='.cob') as source_file:
            source_file.write(code)
            source_file.flush()
            with self.new_temp_file(suffix='.out') as binary_file:
                p = self.compile_with_cobc(source_file.name, binary_file.name, magics[0], magics[1])
                while p.poll() is None:
                    p.write_contents()
                p.write_contents()
                if p.returncode != 0:  # Compilation failed
                    self._write_to_stderr(
                            "[COBOL kernel] cobc exited with code {}, the executable will not be executed".format(
                                    p.returncode))

                    # delete source files before exit
                    os.remove(source_file.name)
                    os.remove(binary_file.name)

                    return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [],
                            'user_expressions': {}}
        p = self.create_jupyter_subprocess([self.master_path, binary_file.name] + magics['args'])
        while p.poll() is None:
            p.write_contents()

        # wait for threads to finish, so output is always shown
        p._stdout_thread.join()
        p._stderr_thread.join()

        p.write_contents()

        # now remove the files we have just created
        os.remove(source_file.name)
        os.remove(binary_file.name)

        if p.returncode != 0:
            self._write_to_stderr("[COBOL kernel] Executable exited with code {}".format(p.returncode))
        return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expressions': {}}

    def do_shutdown(self, restart):
        """Cleanup the created source code files and executables when shutting down the kernel"""
        self.cleanup_files()
