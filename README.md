# DoctorBot

## Installation

#### Python module
`sudo pip3 install -r requirement.txt`
#### apt-get module
```
sudo chmod +x setup_environment.sh
sudo ./setup_environment.sh
```
#### Document Web APIs (no need in milestone 1)
* http://localhost:8000/docs/
* Usage:
```
cd ~/DoctorBot/doctorbot
npm install
webpack
python3 manage.py check
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000
```
## Run DoctorBot
```
cd ~/DoctorBot/brain/brain_libs/LU_model
python3 Doctorbot.py
```