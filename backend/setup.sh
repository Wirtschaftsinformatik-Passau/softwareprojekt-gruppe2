VENV_NAME= backend_tose_venv

python3.10 -m venv $VENV_NAME

source $VENV_NAME/bin/activate

pip install -r requirements.txt

make migrate

deactivate