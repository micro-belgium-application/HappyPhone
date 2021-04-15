python -m venv env
cd ./env/Scripts
call activate
cd ..\..
pip install -r requirements.txt
cd ./env/Scripts
call deactivate
cd ..\..