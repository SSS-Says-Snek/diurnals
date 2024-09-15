desktop_file = i18n.merge_file(
  input: 'com.bmcomis2018.todoist-dailies.desktop.in',
  output: 'com.bmcomis2018.todoist-dailies.desktop',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications'),

  type: 'desktop',
  po_dir: '../po'
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils,
    args: [desktop_file]
  )
endif

# Install icons
install_data(
  'com.bmcomis2018.todoist-dailies.svg',
  install_dir: join_paths(get_option('datadir'), 'icons/hicolor/scalable/apps')
)
