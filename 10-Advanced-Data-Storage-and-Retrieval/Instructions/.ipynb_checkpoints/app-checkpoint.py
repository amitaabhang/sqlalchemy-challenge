{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      " * Serving Flask app \"__main__\" (lazy loading)\n",
      " * Environment: production\n",
      "   WARNING: This is a development server. Do not use it in a production deployment.\n",
      "   Use a production WSGI server instead.\n",
      " * Debug mode: on\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      " * Restarting with windowsapi reloader\n"
     ]
    },
    {
     "ename": "SystemExit",
     "evalue": "1",
     "output_type": "error",
     "traceback": [
      "An exception has occurred, use %tb to see the full traceback.\n",
      "\u001b[1;31mSystemExit\u001b[0m\u001b[1;31m:\u001b[0m 1\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\amita\\anaconda3\\lib\\site-packages\\IPython\\core\\interactiveshell.py:3426: UserWarning: To exit: use 'exit', 'quit', or Ctrl-D.\n",
      "  warn(\"To exit: use 'exit', 'quit', or Ctrl-D.\", stacklevel=1)\n"
     ]
    }
   ],
   "source": [
    "# 1. import Flask\n",
    "from flask import Flask, jsonify\n",
    "\n",
    "import numpy as np\n",
    "import pandas as pd\n",
    "import datetime as dt\n",
    "\n",
    "import sqlalchemy\n",
    "from sqlalchemy.ext.automap import automap_base\n",
    "from sqlalchemy.orm import Session\n",
    "from sqlalchemy import create_engine, func\n",
    "\n",
    "engine = create_engine(\"sqlite:///Resources/hawaii.sqlite\", echo=False)\n",
    "\n",
    "# reflect the tables\n",
    "# Reflect Database into ORM classes\n",
    "Base = automap_base()\n",
    "Base.prepare(engine, reflect=True)\n",
    "\n",
    "Base.classes.keys()\n",
    "\n",
    "Station = Base.classes.station\n",
    "Measurement = Base.classes.measurement\n",
    "\n",
    "session = Session(engine)\n",
    "\n",
    "results =session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]\n",
    "\n",
    "recent_date = dt.datetime.strptime(results , '%Y-%m-%d')\n",
    "\n",
    "new_date = recent_date - dt.timedelta(days = 365)\n",
    "\n",
    "results_stn = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station)\\\n",
    ".order_by(func.count(Measurement.station).desc()).all()\n",
    "active_station_id = results_stn[0][0]\n",
    "\n",
    "# 2. Create an app, being sure to pass __name__\n",
    "app = Flask(__name__)\n",
    "\n",
    "@app.route(\"/\")\n",
    "def welcome():\n",
    "    return (\n",
    "        f\"Welcome to the Mesaurements and Station API!<br/>\"\n",
    "        f\"Available Routes:<br/>\"\n",
    "        f\"/api/v1.0/precipitation<br/>\"\n",
    "        f\"/api/v1.0/stations<br/>\"\n",
    "        f\"/api/v1.0/tobs<br/>\"\n",
    "        f\"/api/v1.0/&lt;start&gt;<br>\"\n",
    "        f\"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br><br/>\"\n",
    "    )\n",
    "\n",
    "\n",
    "# 3. Define what to do when a user hits the index route\n",
    "@app.route(\"/api/v1.0/precipitation\")\n",
    "def precipitation():\n",
    "    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= new_date).all()\n",
    "    prec = {result[0]:result[1] for result in results}\n",
    "    return jsonify(prec)\n",
    "\n",
    "\n",
    "# 4. Define what to do when a user hits the /about route\n",
    "@app.route(\"/api/v1.0/stations\")\n",
    "def stations():\n",
    "    results = session.query(Station.station).all()\n",
    "    np_result = list(np.ravel(results))\n",
    "    return jsonify(stations = np_result)\n",
    "\n",
    "\n",
    "@app.route(\"/api/v1.0/tobs\")\n",
    "def tobs():\n",
    "    recentyear_temp_data =session.query( Measurement.tobs).filter(Measurement.date >= new_date).filter(Measurement.station == active_station_id).all()\n",
    "    np_temp_result = list(np.ravel(recentyear_temp_data))\n",
    "    return jsonify(temps = np_temp_result)\n",
    "\n",
    "\n",
    "@app.route(\"/api/v1.0/<start>\")\n",
    "@app.route(\"/api/v1.0/<start>/<end>\")\n",
    "def stats(start, end = None):\n",
    "    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]\n",
    "    if not end:\n",
    "        results = session.query(*sel).filter(Measurement.date > start).all()\n",
    "        final_result = list(np.ravel(results))\n",
    "        return jsonify(temps = final_result)\n",
    "    else:\n",
    "        results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()\n",
    "        final_result = list(np.ravel(results))\n",
    "        return jsonify(temps = final_result)\n",
    "\n",
    "\n",
    "if __name__ == \"__main__\":\n",
    "    app.run(debug=True)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
