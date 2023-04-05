# class GitRepo
if "__file__" in dir():
  print(f"Loading from '{__file__}'")
import os
import shutil
import requests
from github import Github
import ipywidgets as widgets
#from ipywidgets import Output, HBox, VBox, Label, Button, Layout, Textarea, Dropdown, FileUpload, Tab, Accordion
from ipywidgets import Dropdown, Button, HBox, VBox, Layout, Label, Text
#from IPython.display import clear_output, display, HTML
from IPython.display import clear_output

from get_userlib_path import get_userlib_path
#from get_notebook_dir import get_notebook_dir
from get_jupyter_root_dir import get_jupyter_root_dir
class GitRepo:
  def GUI(self):
    btn_layout = Layout(border='double',width='10%')
    d_layout = Layout(width='30%')
    
    d1 = Dropdown(options = self.fullnames,
      value=None, description='Repositories:', disabled=False, layout=d_layout
    )
    self.b11 = Button(description = 'Clone',
      tooltip = f"Clone repositories to '{self.targetdir}'",
      button_style='', icon = 'check', layout = btn_layout
    )
    b12 = Button(description = 'Remove',
      tooltip = "Remove repositories",
      button_style='', icon = 'check', layout = btn_layout
    )
    b13 = Button(description = 'Download',
      tooltip = "Download tarball",
      button_style='', icon = 'check', layout = btn_layout
    )
    hr = widgets.HTML(value='<hr style="border: 1px solid green;  border-radius: 5px;   margin-top: 0px; margin-bottom: 0px;">')
    br = widgets.HTML(value='<br>')
    self.lb1 = Label(value = f" to {self.targetdir.replace(os.sep,'/')}", layout=Layout(width='40%'))
    self.lb1.style=dict(font_style='normal', font_weight='bolder', text_decoration='underline', font_size='14px')
    tx1 = Text(value='', placeholder='Enter repo short name',
            description='New reposytory:', disabled=False, layout=d_layout
    )    
    b14 = Button(description = 'Create',
      tooltip = "Create repository",
      button_style='', icon = 'check', layout = btn_layout
    )
    
    d2 = Dropdown(options = (),
      value = None, description = 'Files:', disabled=False, layout=d_layout
    )
    b21 = Button(description = 'Update',
      tooltip = f'Update file',
      button_style='', icon = 'check', layout = btn_layout
    )
    b22 = Button(description = 'Remove',
      tooltip = f'Remove file',
      button_style='', icon = 'check', layout = btn_layout
    )
    b23 = Button(description = 'Read',
      tooltip = f'Read file',
      button_style='', icon ='check', layout=btn_layout
    )
    b24 = Button(description = 'Upload',
      tooltip = f'Upload file',
      button_style='', icon='check', layout=btn_layout
    )
    # ........................................
    def on_d1(change):
      self.b11.disabled = False
      b12.disabled = False
      b13.disabled = False
      change_new = change if type(change) is str else change.new
      #b11.description = f"Clone {change_new}"
      self.b11.tooltip = f"Clone '{change_new}' to '{self.targetdir}'"
      b12.tooltip = f"Remove '{change_new}'"
      self.__call__(change_new)
      self.lb1.value = f" to {self.dir__().replace(os.sep,'/')}"
      _options = [file if file in self.files else f"?{file}" for file in self.content]
      for file in self.files:
        if not file in self.content:
          _options.append(f"*{file}")
      d2.options = _options
      if _options:
        d2.value = _options[0]
    d1.observe(on_d1, names='value')    
    def on_b11(b):
      self.clone(d1.value)
    self.b11.on_click(on_b11)
    def on_b12(b):
      self.deleterepo(None)
      d1.options = self.fullnames
    b12.on_click(on_b12)
    def on_b14(b):
      self.createrepo(tx1.value)
      d1.options = self.fullnames
    b14.on_click(on_b14)
    
    def on_d2(change):
      if change.new is None:
        return
      _file = change.new
      b21.disabled = _file[0] in '?*'
      b22.disabled = _file[0] == '*'
      b23.disabled = _file[0] == '*'
      b24.disabled = _file[0] != '*'
      
      b21.tooltip = f"Update {_file}"
      b22.tooltip = f"Remove {_file}"
      b23.tooltip = f"Read {_file}"
      b24.tooltip = f"Create {_file[1:]}"
      
    def on_b21(b): #Update
      self.updatefiles(None, d2.value)
    b21.on_click(on_b21)
    def on_b22(b): #Remove
      self.deletefiles(None, d2.value[1:] if d2.value[0]=='?' else d2.value)
      on_d1(d1.value)
    b22.on_click(on_b22)
    def on_b23(b): #Read
      self.readfiles(None, d2.value[1:] if d2.value[0]=='?' else d2.value)
      on_d1(d1.value)
    b23.on_click(on_b23)
    def on_b24(b): #Create
      self.createfiles(None, d2.value[1:])
      on_d1(d1.value)
    b24.on_click(on_b24)
    
    d2.observe(on_d2, names='value')
    H1 = VBox([HBox([tx1, b14]), HBox([d1, self.b11, self.lb1, b12, b13])])
    H2 = HBox([d2, b21, b22, b23, b24])
    self.V1= VBox([H1, hr ,H2])
    self.V1.layout.border = "2px solid"
    self.V1.box_style = 'success'
    for _b in [self.b11, b12, b13, b21, b22, b23, b24]:
      _b.disabled = True
    clear_output()
    display(self.V1)
    # ..........
  def refresh(self):
    self.repos = self.u.get_repos()
    self.fullnames = [_.full_name if not _.archived else None for _ in self.repos]
    while None in self.fullnames:
      self.fullnames.remove(None)
    # ..............
  def __init__(self, token=None, targetdir=None, prefix='$',  GUI=True): 
    #github = GitRepo(token="<token>", targetdir='userlib')
    self.g = Github(token)
    self.u = self.g.get_user()
    self.targetdir = os.path.join(get_jupyter_root_dir(), targetdir) if targetdir else get_userlib_path()
    self.prefix = prefix
    self.refresh()
    if GUI:
      self.GUI()    
    # ..................................................................
  def __repr__  (self):
    display([f"{_}: {self.fullnames[_]}" for _ in range(len(self.fullnames))])
    display(self.targetdir)
    return ''
    # .................
  def __call__(self, idrepo):
    if idrepo is None:
      return self.repo
    if type(idrepo) is str:
      self.repo = self.g.get_repo(idrepo)
    if type(idrepo) is int:
      self.repo = self.g.get_repo(self.fullnames[idrepo])
    self.content = []
    if self.repo.size > 0:
      contents = self.repo.get_contents("")    
      for file_content in contents:
        if file_content.type == "dir":
          contents.extend(self.repo.get_contents(file_content.path))
        else:
          self.content.append(file_content.path)
    _filelist = []
    dir__ = self.dir__()
    for root, dirs, files in os.walk(dir__):
      for file in files:
        _file = os.path.join(root, file)
        if ".ipynb_checkpoints" in _file or "__pycache__" in _file:
          pass
        else:
          _filelist.append(_file)
    self.files = [_.replace(f"{dir__}{os.sep}", '').replace(os.sep,'/') for _ in _filelist]
    return self.repo
    # .......................
  def dir__(self, *repo):
    _repo = repo[0] if repo else self.repo
    if os.path.basename(self.targetdir) == _repo.name:
      return self.targetdir
    else:  
      return os.path.abspath(f"{self.targetdir}/{self.prefix}{_repo.name}")
    # ...................
  def clone(self, *reponames, show=True):
    #github.clone('sergio53/xlsNavigator', 10, 'sergio53/2022-06-26-resilience_laboM')
    if not os.path.exists(self.targetdir):
      os.makedirs(self.targetdir)
    for reponame in reponames:
      repo = self.__call__(reponame)      
      rn = self.dir__(repo)
      if show: print("")
      if rn == self.targetdir:
        for files in os.listdir(rn):
          path = os.path.join(rn, files)
          try:
            shutil.rmtree(path)
          except OSError:
            os.remove(path)        
      else:
        if os.path.exists(rn):
          shutil.rmtree(rn)
          if show: print(f"shutil.rmtree('{rn}')")
        os.makedirs(rn)

      if repo.size>0:
        contents = repo.get_contents("")
        while contents:
          file_content = contents.pop(0)
          targ = "%s/%s" % (rn,file_content.path)
          if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
            if show: print(targ)
            os.makedirs(targ)
          else:
            if show: print(targ)
            f = open(targ, 'w+b')
            dc = repo.get_contents(file_content.path)  
            if dc.encoding !='none':
              f.write(dc.decoded_content)
            else:
              f.write(dc)
            f.close()
      print(f"'{repo.full_name}' is cloned")
      # .................................
  def readfiles(self, reponame, *filenames, show=True):
    repo = self.repo if reponame is None else self.__call__(reponame)
    rn = self.dir__(repo)    
    if not os.path.exists(rn):
      os.makedirs(rn)
    if show:
      print(f"'{repo.full_name}' to '{rn}'")

    for filename in filenames:
      contents = repo.get_contents(filename)
      while contents:
        file_content = contents.pop(0)
        targ = os.path.abspath(os.path.join(rn, file_content.path))
        if file_content.type == "dir":
          contents.extend(repo.get_contents(file_content.path))
        else:
          dirname = os.path.dirname(targ)
          if not os.path.exists(dirname):
            os.makedirs(dirname)
          f = open(targ, 'w+b')
          if file_content.encoding !='none':
            f.write(file_content.decoded_content)
            if show: print(f"'{targ}' readed")
          else:
            try:
              r = requests.get(file_content.raw_data['download_url'], allow_redirects=True)
              f.write(r.content)  
              if show: print(f"'{targ}' LOADED")
            except:
              self.targ = targ
              self.file_content = file_content
              if show: print(f"'(!!!)\t{targ}' not LOADED")
          f.close()    
    # ............................................
  def updatefiles(self, reponame, *filenames, show=True):
    #github.update('sergio53/2022-07-11-post_tenacite','post_tenacite.ipynb')
    repo = self.repo if reponame is None else self.__call__(reponame)
    rn = self.dir__(repo)    
    if filenames:
      _filenames = filenames
    else:
      listOfFiles = list()
      for (dirpath, dirnames, filenames) in os.walk(rn):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]
      _filenames = [_.replace(f"{rn}{os.path.sep}",'').replace(os.path.sep,"/") for _ in listOfFiles]      
      
    for filename in _filenames:
      data = open(f"{rn}/{filename}", "r").read()
      contents = repo.get_contents(filename)
      _update = repo.update_file(contents.path, "updated", data, contents.sha)
      if show and _update:
        print(f"'{repo.full_name}:: {filename}' updated")
    # ..............................................    
  def createfiles(self, reponame, *filenames, show=True):
    repo = self.repo if reponame is None else self.__call__(reponame)
    rn = self.dir__(repo)
    for filename in filenames:
      data = open(f"{rn}/{filename}", "rb").read()
      repo.create_file(filename, "created", data)
      if show:
        print(f"'{repo.full_name}:: {filename}' created")
    # ..............................................
  def deletefiles(self, reponame, *filenames, show=True):
    repo = self.repo if reponame is None else self.__call__(reponame)
    rn = self.dir__(repo)
    for filename in filenames:
      contents = repo.get_contents(filename)
      repo.delete_file(contents.path, "delete", contents.sha)
      if show:
        print(f"'{repo.full_name}:: {filename}' deleted")
    # ..............................................
  def localdrop(self, reponame, show=True):
    repo = self.repo if reponame is None else self.__call__(reponame)
    rn = self.dir__(repo)
    if rn != self.targetdir:
      if os.path.exists(rn):
        shutil.rmtree(rn)
        if show: print(f"shutil.rmtree('{rn}')")
    else:
      if show: print(f"disable shutil.rmtree('{rn}')")
    # ................................
  def createrepo(self, reponame, show=True):
    repo = self.u.create_repo(reponame)
    self.refresh()
    if show:
      print(f"Repositoriy '{repo.full_name}' created")
    # ......................................
  def deleterepo(self, reponame, show=True):
    repo = self.repo if reponame is None else self.__call__(reponame)
    repo.delete()
    self.refresh()
    if show:
      print(f"Repositoriy '{repo.full_name}' deleted")
    # ......................................  
      
      
      
      