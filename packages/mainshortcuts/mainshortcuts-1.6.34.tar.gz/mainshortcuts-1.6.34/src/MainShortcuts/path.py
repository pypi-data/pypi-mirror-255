import MainShortcuts.addon as _a
import os as _os
import shutil as _shutil
sep=_os.sep # Разделитель в пути файла
extsep=_os.extsep # Разделитель в расширении файла
separator=sep
pathsep=sep
def exists(path): # Объект существует?
  return _os.path.exists(path)
def merge(array,sep=pathsep): # Собрать путь к объекту из массива
  return sep.join(array)
def split(path,sep=pathsep): # Разложить путь к объекту на массив
  return path.split(sep)
def info(path=_os.getcwd(),listdir=False,listlinks=False,sep=pathsep): # Информация о пути
  i={
    "dir":None, # Папка, в которой находится объект
    "dirs":None, # Рекурсивный список папок (если аргумент listdir=True)
    "exists":None, # Существует ли объект? | True/False
    "ext":None, # Расширение файла, даже если это папка
    "files":None, # Рекурсивный список файлов (если аргумент listdir=True)
    "fullname":None, # Полное название объекта (включая расширение)
    "fullpath":None, # Полный путь к объекту
    "link":None, # Это ссылка или оригинал? | True/False
    "name":None, # Название файла без расширения, даже если это папка
    "path":None, # Полученный путь к объекту
    "realpath":None, # Путь к оригиналу, если указана ссылка
    "relpath":None, # Относительный путь
    "size":None, # Размер. Для получения размера папки укажите аргумент listdir=True
    "split":[], # Путь, разделённый на массив
    "type":None # Тип объекта | "file"/"dir"
    }
  i["path"]=path
  i["split"]=split(path)
  i["dir"]=merge(i["split"][:-1])
  i["fullname"]=_os.path.basename(path)
  i["fullpath"]=_os.path.abspath(path)
  i["relpath"]=_os.path.relpath(path)
  if "." in i["fullname"]:
    i["ext"]=i["fullname"].split(".")[-1]
    i["name"]=".".join(i["fullname"].split(".")[:-1])
  else:
    i["ext"]=None
    i["name"]=i["fullname"]
  i["exists"]=exists(path)
  if i["exists"]:
    i["link"]=_os.path.islink(path)
    if i["link"]:
      i["realpath"]=_os.path.realpath(path)
    if _os.path.isfile(path):
      i["size"]=_os.path.getsize(path)
      i["type"]="file"
    elif _os.path.isdir(path):
      i["type"]="dir"
      if listdir:
        tmp=_a.listdir(path,listlinks)
        i["dirs"]=tmp["d"]
        i["files"]=tmp["f"]
        i["size"]=tmp["s"]
    else:
      i["type"]="unknown"
  return i
def delete(path): # Удалить
  inf=info(path)
  if inf["exists"]:
    if inf["type"]=="file":
      _os.remove(path)
    elif inf["type"]=="dir":
      _shutil.rmtree(path)
    else:
      raise Exception("Unknown type: "+inf["type"])
rm=delete
# del=delete
def copy(fr,to): # Копировать
  type=info(fr)["type"]
  if type=="file":
    _shutil.copy(fr,to)
  elif type=="dir":
    _shutil.copytree(fr,to)
  else:
    raise Exception("Unknown type: "+type)
cp=copy
def move(fr,to): # Переместить
  _shutil.move(fr,to)
mv=move
def rename(fr,to): # Переименовать
  _os.rename(fr,to)
rn=rename
def link(fr,to,force=False): # Сделать символическую ссылку
  if exists(to) and force:
    delete(to)
  _os.symlink(fr,to)
ln=link
def format(path,replace_to="_",replace_errors=True,sep=pathsep): # Форматировать путь к файлу (изменить разделитель, удалить недопустимые символы)
  for i in ["/","\\"]:
    path=path.replace(i,sep)
  if replace_errors:
    for i in ["\n",":","*","?","\"","<",">","|","+","%","!","@"]:
      path=path.replace(i,replace_to)
  return path
