import os
import sys
import subprocess


def shell_wrapper(command, check=True):
    err = os.system(command)
    if check and err:
        raise ChildProcessError(command)
    return err


def shell_output(command, error=True):
    return shell_result(command, error)[1]


def shell_exitcode(command, error=True):
    return shell_result(command, error)[0]


def shell_result(command, error=True):
    return getstatusoutput(command, error)


def getstatusoutput(cmd, error=True):
    try:
        data = subprocess.check_output(
            cmd, shell=True, text=True,
            stderr=subprocess.STDOUT if error else subprocess.DEVNULL)
        exitcode = 0
    except subprocess.CalledProcessError as ex:
        data = ex.output
        exitcode = ex.returncode
    if data[-1:] == '\n':
        data = data[:-1]
    return exitcode, data


def shell_with_input(command, inputs):
    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    if isinstance(inputs, str):
        inputs = inputs.encode('utf-8')
    outs, errs = p.communicate(input=inputs)
    return p.returncode, outs, errs


def shell_stdout(command, write=None, env=None):
    proc = subprocess.Popen(command,
                            env=env,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True
                            )
    write = write or sys.stdout.write
    while proc.poll() is None:
        stdout = proc.stdout.readline()
        write(stdout)


def shell_tee(command, env=None):
    def write(s):
        nonlocal result
        result += s
        sys.stdout.write(s)

    result = ''
    shell_stdout(command, write=write, env=env)
    return result


def show_win_msg(msg=None, title=None):
    if os.name == 'nt':
        import ctypes
        mb = ctypes.windll.user32.MessageBoxW
        mb(None, msg or 'Message', title or 'Title', 0)
