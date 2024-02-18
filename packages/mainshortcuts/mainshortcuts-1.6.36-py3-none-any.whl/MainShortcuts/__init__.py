__version_tuple__=(1,6,36)
# Данные о модуле
__version__="{}.{}.{}".format(*__version_tuple__)
__depends__={
  "required":[
    "codecs",
    "json",
    "os",
    "platform",
    "shutil",
    "subprocess",
    "sys"
    ],
  "optional":[
    "cPickle",
    "pickle",
    "toml"
    ]
  }
__functions__=[
  "clear",
  "cls",
  "dict.path",
  "dir.copy",
  "dir.create",
  "dir.delete",
  "dir.list",
  "dir.move",
  "dir.rename",
  "exit",
  "file.copy",
  "file.delete",
  "file.move",
  "file.open",
  "file.read",
  "file.rename",
  "file.save",
  "file.write",
  "json.decode",
  "json.encode",
  "json.print",
  "json.read",
  "json.rebuild",
  "json.rewrite",
  "json.sort",
  "json.write",
  "list.filter",
  "list.rm_duplicates",
  "path.copy",
  "path.cp",
  "path.delete",
  "path.exists",
  "path.format",
  "path.info",
  "path.link",
  "path.ln",
  "path.merge",
  "path.move",
  "path.mv",
  "path.rename",
  "path.rm",
  "path.rn",
  "path.split",
  "proc.run",
  "str.array2str",
  "str.dict2str",
  "str.replace.all",
  "str.replace.multi"
  ]
__variables__=[
  "os.platform",
  "os.type",
  "path.sep",
  "path.separator",
  "proc.args",
  "proc.pid"
  ]
__scripts__=[
  "MS-jsonP",
  "MS-jsonC",
  "MS-mkdir",
  "MS-getCore"
  ]
__classes__={
  "cfg":{
    "functions":[
      "load",
      "open",
      "read",
      "save",
      "write"
      ],
    "variables":[
      "byte_args",
      "cPickle_args",
      "data",
      "json_args",
      "path",
      "default",
      "pickle_args",
      "text_args",
      "toml_args",
      "type"
      ]
    }
  }
__all__=__functions__+__variables__+list(__classes__.keys())
__functions__.sort()
__variables__.sort()
__scripts__.sort()
__all__.sort()
# Импорт
try:
  from MainShortcuts.cfg import cfg
except Exception as error:
  print(error)
try:
  import MainShortcuts.dict as dict
except Exception as error:
  print(error)
try:
  import MainShortcuts.dir as dir
except Exception as error:
  print(error)
try:
  import MainShortcuts.file as file
except Exception as error:
  print(error)
try:
  import MainShortcuts.json as json
except Exception as error:
  print(error)
try:
  import MainShortcuts.main as main
  exit=main.exit
  clear=main.clear
  cls=main.cls
except Exception as error:
  print(error)
try:
  import MainShortcuts.os as os
except Exception as error:
  print(error)
try:
  import MainShortcuts.path as path
except Exception as error:
  print(error)
try:
  import MainShortcuts.proc as proc
except Exception as error:
  print(error)
try:
  import MainShortcuts.str as str
except Exception as error:
  print(error)
try:
  import MainShortcuts.list as list
except Exception as error:
  print(error)
