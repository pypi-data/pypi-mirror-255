import MainShortcuts.path as m_path
import codecs as _codecs
import os as _os
import shutil as _shutil
def read(path,encoding="utf-8"): # Прочитать текстовый файл
  if m_path.info(path)["type"]=="file":
    with _codecs.open(path,"r",encoding=encoding) as f:
      text=f.read()
  else:
    text=""
  return text
def write(path,text="",encoding="utf-8",force=False): # Записать текстовый файл
  if m_path.info(path)["type"]=="dir" and force:
    _os.remove(path)
  with _codecs.open(path,"w",encoding=encoding) as f:
    f.write(str(text))
  return True
def open(path): # Открыть содержимое файла
  if _os.path.exists(path):
    with open(path,"rb") as f:
      content=f.read()
  else:
    content=None
  return content
def save(path,content,force=False): # Сохранить содержимое файла
  if m_path.info(path)["type"]=="dir" and force:
    _os.remove(path)
  with open(path,"wb") as f:
    f.write(content)
  return True
def delete(path):
  type=m_path.info(path)["type"]
  if type=="file":
    _os.remove(path)
  else:
    raise Exception("Unknown type: "+typt)
def copy(fr,to,force=False):
  type=m_path.info(fr)["type"]
  if type=="file":
    if m_path.exists(to) and force:
      m_path.delete(to)
    _shutil.copy(fr,to)
  else:
    raise Exception("Unknown type: "+type)
def move(fr,to,force=False):
  type=m_path.info(fr)["type"]
  if type=="file":
    if m_path.exists(to) and force:
      m_path.delete(to)
    _shutil.move(fr,to)
  else:
    raise Exception("Unknown type: "+type)
def rename(fr,to,force=False):
  type=m_path.info(fr)["type"]
  if type=="file":
    if m_path.exists(to) and force:
      m_path.delete(to)
    _os.rename(fr,to)
  else:
    raise Exception("Unknown type: "+type)