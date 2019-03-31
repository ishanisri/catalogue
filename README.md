# Catalogue
A webapp for cloak room management system.

The app is written in Flask and JQuery and the database used is SQLite3.
It can be used to improve management of items in hostel cloak room.
It uses sockets to send notifications to users about their belongings.


Steps to install:
1. `git clone https://github.com/ishanisri/catalogue.git`
2. `pip install flask`
3. `pip install flask_socketio`
4. `pip install simplejson`
5.  `python app.py`

The project runs at `127.0.0.1:5000` by default. The port can be changed in the app.py file as `socketio.run(app, host='localhost', port=port_number)`.

