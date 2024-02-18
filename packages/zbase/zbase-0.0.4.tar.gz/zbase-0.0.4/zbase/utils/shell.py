import subprocess
from typing import Dict

def exec(cmd:str, cwd:str=None,env:Dict[str,str]=None, **kwargs) -> (str,str,int):
    """
    :param cmd: shell command
    :param cwd: current working directory
    :param env: environment variables
    :return: (stdout,stderr,returncode)
    """
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd,env=env,**kwargs)
    stdout, stderr = p.communicate()
    return stdout.decode(), stderr.decode(), p.returncode


def run(cmd:str, cwd:str=None,env:Dict[str,str]=None,**kwargs) -> int:

    """
    :param cmd: shell command
    :param cwd: current working directory
    :param env: environment variables
    :return: returncode
    """
    return subprocess.run(cmd, shell=True, cwd=cwd,env=env,**kwargs).returncode
