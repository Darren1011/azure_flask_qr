#!/bin/bash

# Navigate to the Flask backend directory and start the server
cd flask-react-qr
gunicorn --bind=0.0.0.0 --timeout 600 app:app &

# Navigate to the React frontend directory, install dependencies, build, and serve it
cd ../qr-frontend
npm install
npm start
