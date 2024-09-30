project('todoist_dailies',
  version: '0.0.2',
  meson_version: '>= 0.57.0'
)

dependency('gtk4')
dependency('libadwaita-1', version: '>= 1.0')
dependency('glib-2.0')
dependency('pygobject-3.0', version: '>= 3.29.1')

i18n = import('i18n')
gnome = import('gnome')

application_id = 'io.github.sss_says_snek.todoist_dailies' # APPLICATION ID
pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'src') # e.g /usr/local/share/todoist-dailies/src

py_mod = import('python')
py_installation = py_mod.find_installation('python3', modules: ['schedule', 'todoist_api_python']) # Python dependencies
py_installation.dependency()

# Configuration
conf = configuration_data()
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('BUILD_TYPE', get_option('buildtype'))
conf.set('pkgdatadir', pkgdatadir)
conf.set('APP_ID', application_id)
conf.set('VERSION', meson.project_version())
conf.set('PYTHON', py_installation.full_path())

subdir('data')
subdir('src')

gnome.post_install(
  glib_compile_schemas: true,
  gtk_update_icon_cache: true,
  update_desktop_database: true,
)
