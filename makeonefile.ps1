pyinstaller --onefile --windowed `
  --icon "icons8-dale-96.ico" `
  --add-data "miniapp/templates;miniapp/templates" `
  --add-data "miniapp/static;miniapp/static" `
  --add-data "database/films.sqlite;database" `
  --add-data "icons8-dale-96.ico;." `
  index.py
