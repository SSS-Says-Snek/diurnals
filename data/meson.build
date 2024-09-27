appstream_file = i18n.merge_file(
  input: 'io.github.sss_says_snek.todoist_dailies.metainfo.xml.in',
  output: 'io.github.sss_says_snek.todoist_dailies.metainfo.xml',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'metainfo'),

  po_dir: '../po'
)

desktop_file = i18n.merge_file(
  input: 'io.github.sss_says_snek.todoist_dailies.desktop.in',
  output: 'io.github.sss_says_snek.todoist_dailies.desktop',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications'),

  type: 'desktop',
  po_dir: '../po'
)

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

# Install icons
install_data(
  'io.github.sss_says_snek.todoist_dailies.svg',
  install_dir: join_paths(get_option('datadir'), 'icons/hicolor/scalable/apps')
)
