def filter(a,whitelist=None,blacklist=[]):
  if whitelist==None:
    whitelist=a
  b=[]
  for i in a:
    if (i in whitelist) and (not i in blacklist):
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