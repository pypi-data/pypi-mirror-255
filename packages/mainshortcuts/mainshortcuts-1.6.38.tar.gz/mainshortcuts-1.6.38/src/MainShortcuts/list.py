import re
def filter(a,whitelist=None,blacklist=[],regex=False,begin=None,end=None):
  if whitelist==None:
    whitelist=a
  if type(whitelist)==str:
    whitelist=[whitelist]
  if type(blacklist)==str:
    blacklist=[blacklist]
  b=[]
  for i in a:
    add=True
    if begin!=None:
      if str(i).startswith(str(begin)):
        add=True
      else:
        add=False
    if end!=None and add:
      if str(i).endswith(str(end)):
        add=True
      else:
        add=False
    if regex and add:
      reW=False
      for i2 in whitelist:
        if re.match(str(i2),str(i))!=None:
          reW=True
          break
      reB=False
      for i2 in blacklist:
        if re.match(str(i2),str(i))!=None:
          reB=True
          break
      if reW and not reB:
        add=True
      else:
        add=False
    if add and not regex:
      if (i in whitelist) and (not i in blacklist):
        add=True
      else:
        add=False
    if add:
      b.append(i)
  return b
def rm_duplicates(a,trim=False,case=False):
  b=[]
  trim=str(trim).lower()
  case=str(case).lower()
  for i in a:
    if trim in ["true","lr","rl","all"]:
      i=i.strip()
    elif trim in ["l","left"]:
      i=i.lstrip()
    elif trim in ["r","right"]:
      i=i.rstrip()
    if case in ["l","lower","low"]:
      i=i.lower()
    elif case in ["u","upper","up"]:
      i=i.upper()
    elif case in ["capitalize","cap"]:
      i=i.capitalize()
    if not i in b:
      b.append(i)
  return b
