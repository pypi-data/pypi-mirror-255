import os as _os
import subprocess as _subprocess
import sys as _sys
args=_sys.argv # Аргументы запуска программы
pid=_os.getpid() # PID текущего процесса
def run(args): # Запустить процесс ("nano example.txt" -> ["nano","example.txt"])
  p=_subprocess.Popen(args,stdout=_subprocess.PIPE)
  code=p.wait()
  out,err=p.communicate()
  if isinstance(out,bytes):
    out=out.decode("utf-8")
  elif not isinstance(out,str):
    out=str(out)
  if isinstance(err,bytes):
    err=err.decode("utf-8")
  elif not isinstance(err,str):
    err=str(err)
  return {"code":code,"output":out,"error":err,"c":code,"o":out,"e":err}