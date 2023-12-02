export VENV_NAME=test_env

python3.10 -m venv $VENV_NAME

source $VENV_NAME/bin/activate

pip install -r reqs.txt

deactivate