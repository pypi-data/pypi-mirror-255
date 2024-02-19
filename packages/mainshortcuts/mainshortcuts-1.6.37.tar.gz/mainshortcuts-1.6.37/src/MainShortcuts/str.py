def array2str(a):
  b=[]
  for i in a:
    b.append(str(i))
  return b
def dict2str(a):
  b={}
  for key,value in a.items():
    b[key]=str(value)
  return b
class replace:
  def multi(text=None,dict=None): # Мульти-замена {"что заменить":"чем заменить"}
    t=str(text)
    for key,value in dict.items():
      t=t.replace(key,str(value))
    return t
  def all(text=None,fr=None,to=None): # Замена пока заменяемый текст не исчезнет
    t=str(text)
    a=str(fr)
    b=str(to)
    if a in b:
      raise endlessCycle('"{0}" is contained in "{1}", this causes an infinite loop'.format(a,b))
    while a in t:
      t=t.replace(a,b)
    return t