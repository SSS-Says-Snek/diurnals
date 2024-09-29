sources = [
  '__init__.py',
  'api_dialog.py',
  'config_window.py',
  'config_schedule_row.py',
  'statusicon.py',
  'todoist_worker.py',
  'todoist_element.py',
  'window.py',
  'main.py',
  'style.css' # shhh
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
  input: 'todoist_dailies.in',
  output: 'todoist_dailies',
  configuration: conf,

  install: true,
  install_mode: 'rwxr-xr-x',
  install_dir: get_option('bindir')
)

