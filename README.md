# ZeusUploader

### Setup
 - `pip install pipenv`
 - `pipenv shell`
 - `pipenv install`

### Build
`pyinstaller --icon=logo.ico --add-data "logo.ico;." .\uploader.py --windowed --hidden-import babel.numbers`

*Note: You can create a shortcut of uploader.exe wherever you like.*