project('todoist-dailies',
  version: '0.0.1',
  meson_version: '>= 0.55.0'
)

dependency('gtk4')
dependency('libadwaita-1', version: '>= 1.0')
dependency('glib-2.0')
dependency('pygobject-3.0', version: '>= 3.29.1')

i18n = import('i18n')
application_id = 'com.bmcomis2018.todoist-dailies'

subdir('data')
subdir('src')
