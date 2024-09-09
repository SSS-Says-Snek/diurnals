py_mod = import('python')
py_installation = py_mod.find_installation('python3', modules: ['schedule', 'todoist_api_python'])
py_installation.dependency()

pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'src') # e.g /usr/local/share/todoist-dailies/src

# Configuration
conf = configuration_data()
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('BUILD_TYPE', get_option('buildtype'))
conf.set('pkgdatadir', pkgdatadir)
conf.set('APP_ID', 'com.bmcomis2018.todoist-dailies')
conf.set('PYTHON', py_installation.full_path())

sources = [
  '__init__.py',
  'api_dialog.py',
  'config_window.py',
  'statusicon.py',
  'todoist_worker.py',
  'window.py',
  'main.py'
]

# Configure constants
configure_file(
  input: 'constants.py',
  output: 'constants.py',
  configuration: conf,
  install_dir: moduledir
)

install_data(sources, install_dir: moduledir)

# Configure todoist dailies bin
configure_file(
  input: 'todoist-dailies.in',
  output: 'todoist-dailies',
  configuration: conf,

  install: true,
  install_mode: 'rwxr-xr-x',
  install_dir: get_option('bindir')
)

