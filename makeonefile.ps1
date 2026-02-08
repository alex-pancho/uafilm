pyinstaller --onefile `
  --add-data "miniapp/templates;miniapp/templates" `
  --add-data "miniapp/static;miniapp/static" `
  --add-data "database/films.sqlite;." `
  index.py
