# Bundle GResource file
gnome.compile_resources('todoist_dailies',
  'io.github.sss_says_snek.todoist_dailies.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

# Configure appstream metadata
appstream_file = i18n.merge_file(
  input: 'io.github.sss_says_snek.todoist_dailies.metainfo.xml.in',
  output: 'io.github.sss_says_snek.todoist_dailies.metainfo.xml',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'metainfo'),

  po_dir: '../po'
)

# Configure desktop file
desktop_file = i18n.merge_file(
  input: 'io.github.sss_says_snek.todoist_dailies.desktop.in',
  output: 'io.github.sss_says_snek.todoist_dailies.desktop',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications'),

  type: 'desktop',
  po_dir: '../po'
)

# Configure schemas
configure_file(
  input: 'io.github.sss_says_snek.todoist_dailies.gschema.xml.in',
  output: 'io.github.sss_says_snek.todoist_dailies.gschema.xml',
  configuration: conf,
  install: true,
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)

# VALIDATION
appstream_utils = find_program('appstreamcli', required: false)
if appstream_utils.found()
  test('Validate appstream file', appstream_utils,
    args: ['validate', '--no-net', '--explain', appstream_file]
    )
endif

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils,
    args: [desktop_file]
  )
endif

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file', compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()]
  )
endif

# Install icons
install_data(
  'io.github.sss_says_snek.todoist_dailies.svg',
  install_dir: join_paths(get_option('datadir'), 'icons/hicolor/scalable/apps')
)
