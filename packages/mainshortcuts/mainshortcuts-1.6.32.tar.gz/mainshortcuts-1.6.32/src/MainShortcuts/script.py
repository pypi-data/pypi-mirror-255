import os, traceback
import MainShortcuts as ms
class _MainCore:
  def __init__(self,color=True):
    self.args=ms.proc.args # Все аргументы запуска (то же самое, что и sys.argv)
    self.core_name="MainCore"
    self.core_version=1
    self.dir=ms.path.info(__file__)["dir"] # Папка, в которой находится программа
    self.exception=traceback.format_exc
    self.pid=os.getpid() # PID программы
    self.run=__name__=="__main__" # Запущена программа или её импортируют?
    self.color_names=[
      "",
      "BG_BLACK",
      "BG_BLUE",
      "BG_GREEN",
      "BG_LIGHTBLACK",
      "BG_LIGHTBLUE",
      "BG_LIGHTGREEN",
      "BG_LIGHTPINK",
      "BG_LIGHTRED",
      "BG_LIGHTWHITE",
      "BG_LIGHTYELLOW",
      "BG_PINK",
      "BG_RED",
      "BG_WHITE",
      "BG_YELLOW",
      "BLACK",
      "BLUE",
      "GREEN",
      "HIGH",
      "LIGHTBLACK",
      "LIGHTBLUE",
      "LIGHTGREEN",
      "LIGHTPINK",
      "LIGHTRED",
      "LIGHTWHITE",
      "LIGHTYELLOW",
      "LOW",
      "PINK",
      "RED",
      "RESET",
      "WHITE",
      "YELLOW"
      ]
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
mcore=_MainCore()
cprint=mcore.cprint
cformat=mcore.cformat
argv=mcore.args[1:]
def mkdir(path=argv):
  if type(path)==str:
    p=[path]
  elif type(path)==tuple:
    p=list(path)
  else:
    p=path
  for i in p:
    try:
      ms.dir.create(i)
    except Exception as e:
      cprint(e,start="RED")
def jsonPretty(path=argv):
  if type(path)==str:
    p=[path]
  elif type(path)==tuple:
    p=list(path)
  else:
    p=path
  for i in p:
    try:
      d=ms.json.read(i)
      ms.json.write(i,d,mode="p")
    except Exception as e:
      cprint(e,start="RED")
def jsonCompress(path=argv):
  if type(path)==str:
    p=[path]
  elif type(path)==tuple:
    p=list(path)
  else:
    p=path
  for i in p:
    try:
      d=ms.json.read(i)
      ms.json.write(i,d,mode="c")
    except Exception as e:
      cprint(e,start="RED")
def getCore(path=argv):
  if type(path)==str:
    p=[path]
  elif type(path)==tuple:
    p=list(path)
  else:
    p=path
  from MainShortcuts.MainCore import __file__ as corePath
  for i in p:
    try:
      if ms.path.exists(i):
        a=ms.file.read(i)
        b=ms.file.read(corePath).strip()
        c=b.rstrip()+"\n"+a
        ms.file.write(i,c.rstrip())
        cprint(f'MainCore added to the beginning of the file "{i}"',start="GREEN")
      else:
        ms.file.copy(corePath,i)
        cprint(f'MainCore is written to file "{i}"',start="GREEN")
    except Exception as e:
      cprint(e,start="RED")
def getCoreMini(path=argv):
  if type(path)==str:
    p=[path]
  elif type(path)==tuple:
    p=list(path)
  else:
    p=path
  d="from MainShortcuts.MainCore import ms, _MainCore\nmcore=_MainCore(__name__=__name__,__file__=__file__)\ncprint=mcore.cprint\ncformat=mcore.cformat\n"
  for i in p:
    try:
      if ms.path.exists(i):
        a=ms.file.read(i)
        c=d+a
        ms.file.write(i,c.rstrip())
        cprint(f'MainCore added to the beginning of the file "{i}"',start="GREEN")
      else:
        ms.file.write(i,d)
        cprint(f'MainCore is written to file "{i}"',start="GREEN")
    except Exception as e:
      cprint(e,start="RED")
