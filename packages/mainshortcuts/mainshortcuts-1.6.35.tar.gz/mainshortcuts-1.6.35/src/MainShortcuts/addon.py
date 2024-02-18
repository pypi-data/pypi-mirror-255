import os as _o
def listdir(a,listlinks):
  s=0
  f=[]
  d=[]
  for i in _o.listdir(a):
    i=_o.path.join(a,i)
    if _o.path.isfile(i):
      f.append(i)
      if not _o.path.islink(i):
        s+=_o.path.getsize(i)
    if _o.path.isdir(i):
      d.append(i)
      if listlinks or not _o.path.islink(i):
        m=listdir(i,listlinks)
        if not _o.path.islink(i):
          s+=m["s"]
        f+=m["f"]
        d+=m["d"]
  return {"s":s,"f":f,"d":d}
