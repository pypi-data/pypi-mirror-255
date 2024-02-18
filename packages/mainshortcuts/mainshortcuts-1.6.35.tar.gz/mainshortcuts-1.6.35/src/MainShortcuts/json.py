import MainShortcuts.path as m_path
import json as _json
_print=print
def encode(data,mode="c",indent=2,sort=True): # Данные в текст
  if mode in ["c","compress","min","zip"]: # Сжатый
    t=_json.dumps(data,separators=[",",":"],sort_keys=sort)
  elif mode in ["pretty","p","print","max"]: # Развёрнутый
    t=_json.dumps(data,indent=int(indent),sort_keys=sort)
  else: # Без параметров
    t=_json.dumps(data,sort_keys=sort)
  return t
def decode(text): # Текст в данные
  return _json.loads(str(text))
def write(path,data,encoding="utf-8",mode="c",indent=2,sort=True,force=False): # Данные в файл
  if m_path.info(path)["type"]=="dir" and force:
    _os.remove(path)
  with open(path,"w",encoding=encoding) as f:
    f.write(encode(data,mode=mode,indent=indent,sort=sort))
  return True
def read(path,encoding="utf-8"): # Данные из файла
  with open(path,"r",encoding=encoding) as f:
    return _json.load(f)
def print(data,mode="p",indent=2,sort=True): # Вывести JSON в консоль
  _print(encode(data,mode=mode,indent=indent,sort=sort))
def sort(data): # Сортировать ключи словарей ({"b":1,"c":2,"a":3} -> {"a":3,"b":1,"c":2})
  return decode(encode(data,mode="c",sort=True))
def rebuild(text,mode="c",indent=2,sort=True): # Перестроить JSON в тексте
  return encode(decode(text),mode=mode,indent=indent,sort=sort)
def rewrite(path,encoding="utf-8",mode="c",indent=2,sort=True): # Перестроить JSON в файле
  return write(path,read(path,encoding=encoding),encoding=encoding,mode=mode,indent=indent,sort=sort)