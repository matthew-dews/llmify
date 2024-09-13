Note: venv not currently required for running because we pulled the code in directly to get Windows support

# Setup
python3 -m venv env
source env/bin/activate.fish
pip install -r requirements.txt

# Windows git bash
python3 -m venv env
source env/Scripts/activate
pip install -r requirements.txt

# Usage
./llmify.py args

# Formating & type checking
Run `lint.sh`, which will setup a venv and then run the formatter and type checker.

# Packaging
Run `bundle.sh`, which will setup a venv and then run PyInstaller.
