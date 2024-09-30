sources = [
  '__init__.py',
  'config_window.py',
  'config_schedule_row.py',
  'todoist_worker.py',
  'todoist_element.py',
  'welcome_carousel.py',
  'window.py',
  'main.py',
]

# Configure constants
configure_file(
  input: 'constants.py',
  output: 'constants.py',
  configuration: conf,
  install_dir: moduledir
)

install_data(sources, install_dir: moduledir)

# Configure diurnals bin
configure_file(
  input: 'diurnals.in',
  output: 'diurnals',
  configuration: conf,

  install: true,
  install_mode: 'rwxr-xr-x',
  install_dir: get_option('bindir')
)

