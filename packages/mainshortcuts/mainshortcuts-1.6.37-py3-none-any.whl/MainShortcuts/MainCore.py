import os, traceback
import MainShortcuts as ms
class _dictplus_storage:
  def __init__(self):
    self.d={}
class dictplus:
  def __init__(self,data={}):
    self._s=_dictplus_storage()
    self._s.d=data
    def __getattr__(self,k):
      if k=="__data__":
        return self._s.d
      else:
        return self._s.d[k]
    def __setattr__(self,k,v):
      if k=="__data__":
        self._s.d=v
      else:
        self._s.d[k]=v
    self.__getattr__=__getattr__
    self.__setattr__=__setattr__
  def __repr__(self):
    return f"dictplus({str(self._s.d)})"
  def __dir__(self):
    return list(self._s.d.keys())+["__data__"]
  def __len__(self):
    return len(self._s.d.keys())
  def __contains__(self,k):
    return (k in self._s.d)
  def __eq__(self,o):
    if type(o)==dict:
      return self._s.d==o
    else:
      return self._s.d==o.__data__
  def __getitem__(self,k):
    return self._s.d[k]
  def __setitem__(self,k,v):
    self._s.d[k]=v
  def __delitem__(self,k):
    self._s.d.pop(k)
  def __delattr__(self,k):
    self._s.d.pop(k)
class _MainCore:
  def __init__(self,color=True,__name__=__name__,__file__=__file__):
    """Параметры:
  color - разрешить цветной текст (по умолчанию: True)
  __name__ и __file__ - укажите если импортируете MainCore из модуля. Если вы записали его в начало файла - не трогайте"""
    self.args=ms.proc.args # Все аргументы запуска (то же самое, что и sys.argv)
    self.core_name="MainCore"
    self.core_version=1
    self.dir=ms.path.info(__file__)["dir"] # Папка, в которой находится программа
    self.exception=traceback.format_exc
    self.pid=os.getpid() # PID программы
    self.run=__name__=="__main__" # Запущена программа или её импортируют?
    self.color_names=["","BG_BLACK","BG_BLUE","BG_GREEN","BG_LIGHTBLACK","BG_LIGHTBLUE","BG_LIGHTGREEN","BG_LIGHTPINK","BG_LIGHTRED","BG_LIGHTWHITE","BG_LIGHTYELLOW","BG_PINK","BG_RED","BG_WHITE","BG_YELLOW","BLACK","BLUE","GREEN","HIGH","LIGHTBLACK","LIGHTBLUE","LIGHTGREEN","LIGHTPINK","LIGHTRED","LIGHTWHITE","LIGHTYELLOW","LOW","PINK","RED","RESET","WHITE","YELLOW"]
    self.colors={}
    for i in self.color_names:
      self.colors[i]=""
    if color:
      try:
        import colorama as clr
        clr.init()
        self.colors["BG_BLACK"]=clr.Back.BLACK
        self.colors["BG_BLUE"]=clr.Back.BLUE
        self.colors["BG_GREEN"]=clr.Back.GREEN
        self.colors["BG_LIGHTBLACK"]=clr.Back.LIGHTBLACK_EX
        self.colors["BG_LIGHTBLUE"]=clr.Back.LIGHTBLUE_EX
        self.colors["BG_LIGHTGREEN"]=clr.Back.LIGHTGREEN_EX
        self.colors["BG_LIGHTPINK"]=clr.Back.LIGHTMAGENTA_EX
        self.colors["BG_LIGHTRED"]=clr.Back.LIGHTRED_EX
        self.colors["BG_LIGHTWHITE"]=clr.Back.LIGHTWHITE_EX
        self.colors["BG_LIGHTYELLOW"]=clr.Back.LIGHTYELLOW_EX
        self.colors["BG_PINK"]=clr.Back.MAGENTA
        self.colors["BG_RED"]=clr.Back.RED
        self.colors["BG_WHITE"]=clr.Back.WHITE
        self.colors["BG_YELLOW"]=clr.Back.YELLOW
        self.colors["BLACK"]=clr.Fore.BLACK
        self.colors["BLUE"]=clr.Fore.BLUE
        self.colors["GREEN"]=clr.Fore.GREEN
        self.colors["HIGH"]=clr.Style.BRIGHT
        self.colors["LIGHTBLACK"]=clr.Fore.LIGHTBLACK_EX
        self.colors["LIGHTBLUE"]=clr.Fore.LIGHTBLUE_EX
        self.colors["LIGHTGREEN"]=clr.Fore.LIGHTGREEN_EX
        self.colors["LIGHTPINK"]=clr.Fore.LIGHTMAGENTA_EX
        self.colors["LIGHTRED"]=clr.Fore.LIGHTRED_EX
        self.colors["LIGHTWHITE"]=clr.Fore.LIGHTWHITE_EX
        self.colors["LIGHTYELLOW"]=clr.Fore.LIGHTYELLOW_EX
        self.colors["LOW"]=clr.Style.DIM
        self.colors["PINK"]=clr.Fore.MAGENTA
        self.colors["RED"]=clr.Fore.RED
        self.colors["RESET"]=clr.Style.RESET_ALL
        self.colors["WHITE"]=clr.Fore.WHITE
        self.colors["YELLOW"]=clr.Fore.YELLOW
      except:
        color=False
  def __repr__(self):
    return ms.json.encode({"name":self.core_name,"version":self.core_version},mode="c")
  def cprint(self,a,start=""): # Вывести цветной текст | cprint("Обычный текст, {BLUE}Синий текст")
    b=str(a).rstrip().format(**self.colors)
    print(self.colors["RESET"]+self.colors[start]+b.rstrip()+self.colors["RESET"])
  def cformat(self,a,start=""): # Аналогично cprint, но вывод в return, и нет strip
    b=str(a).format(**self.colors)
    return self.colors["RESET"]+self.colors[start]+b+self.colors["RESET"]
  def ctest(self): # Вывод всех доступных цветов
    for k,v in self.colors.items():
      if k!="":
        print("{0}{1}: {2}EXAMPLE ░▒▓ ███{0}".format(self.colors["RESET"],k,v))
  def ignoreException(self,target,*args,**kwargs):
    try:
      return target(*args,**kwargs)
    except:
      return self.exception()
if __name__=="__main__":
  mcore=_MainCore()
  cprint=mcore.cprint
  cformat=mcore.cformat