project('todoist_dailies',
  version: '0.0.1',
  meson_version: '>= 0.55.0'
)

dependency('gobject-introspection-1.0', version: '>= 1.35.0')
dependency('gtk4')
dependency('libadwaita-1', version: '>= 1.0')
dependency('libsoup-3.0')
dependency('glib-2.0')
dependency('pygobject-3.0', version: '>= 3.29.1')

py_mod = import('python')
py_installation = py_mod.find_installation('python3', modules: ['schedule', 'todoist_api_python'])
py_installation.dependency()

pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())

conf = configuration_data()
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('BUILD_TYPE', get_option('buildtype'))
conf.set('pkgdatadir', pkgdatadir)
conf.set('APPID', 'com.bmcomis2018.todoist-dailies')
conf.set('PYTHON', py_installation.path())

moduledir = join_paths(pkgdatadir, 'todoist_dailies')

sources = [
  'todoist_dailies/api_dialog.py',
  'todoist_dailies/config_window.py',
  'todoist_dailies/constants.py',
  'todoist_dailies/statusicon.py',
  'todoist_dailies/todoist_worker.py',
  'todoist_dailies/window.py',
  'todoist_dailies/main.py'
]
# py_installation.install_sources(sources, subdir: 'todoist_dailies')
install_data(sources, install_dir: moduledir)

# install_data('bin/todoist-dailies', install_mode: 'rwxr-xr-x', install_dir: get_option('bindir'))

configure_file(
  input: 'bin/todoist_dailies',
  output: 'todoist_dailies',
  configuration: conf,

  install: true,
  install_mode: 'rwxr-xr-x',
  install_dir: get_option('bindir')
)


# install_subdir('src', install_dir: python_dir)
