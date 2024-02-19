noimport={}
import MainShortcuts.path as m_path
try:
  import MainShortcuts.file as file
except Exception as e:
  noimport["byte"]=e
  noimport["text"]=e
try:
  import MainShortcuts.json as json
except Exception as e:
  noimport["json"]=e
try:
  import pickle
except Exception as e:
  noimport["pickle"]=e
try:
  import _pickle as cPickle
except Exception as e:
  noimport["cPickle"]=e
try:
  import toml
except Exception as e:
  noimport["toml"]=e
types=["auto","json","pickle","cPickle","toml","text","byte"]
def _checkType(path,type):
  ext=m_path.info(path)["ext"].lower()
  for i in types:
    if type.lower()==i.lower():
      type=i
      break
  if not type in types:
    raise Exception('Type "{0}" not supported'.format(type))
  elif type!="auto":
    return type
  elif ext in ["json"]:
    return "json"
  elif ext in ["pickle","pkl"]:
    return "pickle"
  elif ext in ["cpickle","dpb"]:
    return "cPickle"
  elif ext in ["toml"]:
    return "toml"
  elif ext in ["txt"]:
    return "text"
  elif ext in ["dat","bin"]:
    return "byte"
  else:
    raise Exception('Cannot determine type by extension "{0}"'.format(ext))
def _checkImport(type):
  if type in noimport:
    raise ImportError(noimport[type])
    return False
  else:
    return True
def _dict_update(a,b):
  for k,v in b.items():
    a[k]=v
  return a
class cfg:
  # Код
  def __init__(self,path,
    data=None,
    default={},
    type="auto", # "auto" - определение по расширению файла
    json_args={},
    pickle_args={},
    cPickle_args={},
    toml_args={},
    text_args={},
    byte_args={}
    ):
    # Код
    self.json_args={
      "mode":"c",
      "indent":2,
      "sort":True,
      "encoding":"utf-8"
      }
    self.pickle_args={
      "protocol":None,
      "fix_imports":True,
      "buffer_callback":None,
      "encoding":"ASCII",
      "errors":"strict",
      "buffers":None
      }
    self.cPickle_args={}
    self.toml_args={
      "encoding":"utf-8"
      }
    self.text_args={
      "encoding":"utf-8"
      }
    self.byte_args={}
    self.path=path
    self.data=data
    self.default=default
    self.type=_checkType(path,type)
    _checkImport(self.type)
    self.json_args.update(json_args)
    self.pickle_args.update(pickle_args)
    self.cPickle_args.update(cPickle_args)
    self.toml_args.update(toml_args)
    self.text_args.update(text_args)
    self.byte_args.update(byte_args)
  def __getitem__(self,k):
    return self.data[k]
  def __setitem__(self,k,v):
    self.data[k]=v
  def load(self,path=None,type=None,json_args={},pickle_args={},toml_args={},text_args={}):
    # Загрузка из файла
    if path==None:
      path=self.path
    if type==None:
      type=self.type
    else:
      type=_checkType(path,type)
    _checkImport(type)
    if type=="json":
      args=self.json_args
      args.update(json_args)
      self.data=json.read(path,encoding=args["encoding"])
    elif type=="pickle":
      args=self.pickle_args
      args.update(pickle_args)
      with open(path,"rb") as f:
        self.data=pickle.load(f,
          fix_imports=args["fix_imports"],
          encoding=args["encoding"],
          errors=args["errors"],
          buffers=args["buffers"]
          )
    elif type=="cPickle":
      with open(path,"rb") as f:
        self.data=cPickle.load(f)
    elif type=="toml":
      args=self.toml_args
      args.update(toml_args)
      with open(path,"r",encoding=args["encoding"]) as f:
        self.data=toml.load(f)
    elif type=="text":
      args=self.text_args
      args.update(text_args)
      self.data=file.read(path,encoding=args["encoding"])
    elif type=="byte":
      self.data=file.open(path)
    if isinstance(self.data,dict):
      self.data=_dict_update(self.default,self.data)
    return self.data
  def save(self,path=None,type=None,json_args={},pickle_args={},cPickle_args={},toml_args={},text_args={}):
    # Сохранение в файл
    if path==None:
      path=self.path
    if type==None:
      type=self.type
    else:
      type=_checkType(path,type)
    _checkImport(type)
    if type=="json":
      args=self.json_args
      args.update(json_args)
      json.write(path,self.data,mode=args["mode"],indent=args["indent"],sort=args["sort"],encoding=args["encoding"])
    elif type=="pickle":
      args=self.pickle_args
      args.update(pickle_args)
      with open(path,"wb") as f:
        pickle.dump(self.data,f,
          protocol=args["protocol"],
          fix_imports=args["fix_imports"],
          buffer_callback=args["buffer_callback"]
          )
    elif type=="cPickle":
      args=self.cPickle_args
      args.update(cPickle_args)
      with open(path,"wb") as f:
        cPickle.dump(self.data,f)
    elif type=="toml":
      args=self.toml_args
      args.update(toml_args)
      with open(path,"w",encoding=args["encoding"]) as f:
        toml.dump(self.data,f)
    elif type=="text":
      args=self.text_args
      args.update(text_args)
      file.write(path,self.data,encoding=args["encoding"])
    elif type=="byte":
      file.save(path,self.data)
  def set_default(self,data=None):
    if data==None:
      data=self.data
    self.data=_dict_update(self.default,data)
    return self.data
  read=load
  open=load
  write=save
