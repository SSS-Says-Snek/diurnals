# Bundle GResource file
gnome.compile_resources('diurnals',
  '@0@.gresource.xml'.format(application_id),
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

# Configure appstream metadata
appstream_file = i18n.merge_file(
  input: '@0@.metainfo.xml.in'.format(application_id),
  output: '@0@.metainfo.xml'.format(application_id),
  install: true,
  install_dir: join_paths(get_option('datadir'), 'metainfo'),

  po_dir: '../po'
)

# Configure desktop file
desktop_file = i18n.merge_file(
  input: '@0@.desktop.in'.format(application_id),
  output: '@0@.desktop'.format(application_id),
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications'),

  type: 'desktop',
  po_dir: '../po'
)

# Configure schemas
configure_file(
  input: '@0@.gschema.xml.in'.format(application_id),
  output: '@0@.gschema.xml'.format(application_id),
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
  '@0@.svg'.format(application_id),
  install_dir: join_paths(get_option('datadir'), 'icons/hicolor/scalable/apps')
)
