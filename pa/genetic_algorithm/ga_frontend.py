# -*- coding: utf-8 -*-

"""
Copyright 2018 Pantelis Frangoudis, EURECOM

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
#################################################################
Genetic placement algorithm REST front end.

To start it:
python main.py -c ./default.conf 
#################################################################
"""

from ga import helpers
from ga.ga import GA

import yaml
import getopt
import sys
import json
import httplib
import requests
import copy
import threading
import pymongo
import datetime
from flask import Flask, jsonify, request
from flask_restful import reqparse, abort, Api, Resource
import translator

class GAFrontEnd(object):
  """Genetic algorithm front-end server.

  This class implements a REST API for executing the genetic placement algorithm. The server
  operates asynchronously. Callers request a service placement by providing information on
  the NFVI topology and network service, as well as a request identifier and a callback URL.
  When the algorithm has terminated and has come up with a placement, it notifies the caller
  over the registered callback URL. 

  It is also possible for the caller to query the status of a request by specifying the request id.
  A request status can be one of the following: INPROGRESS, SUCCESS, FAIL.

  All request data (input, status, request id, timestamps, placement solution) are stored in 
  a MongoDB database.
  """

  def __init__(self, configuration, api_version=1):
    """Constructor method. A dictionary with configuration options following a call to _load_configuration
    as well as the API version (defaults to 1) need to be provided.
    """
 
    self.api_version = api_version
    self.base_url = "/5gt/so/v" + str(self.api_version) + "/"
    self.configuration = configuration
    self.port = configuration["server_port"]
    self.db_client = pymongo.MongoClient(configuration["db_host"], configuration["db_port"])
    self.db = self.db_client[configuration["db_name"]]
    self.db_collection = self.db["placement_requests"]
    self.db_collection.create_index("ReqId", unique=True)
    # we maintain "raw" requests in a separate collection to avoid some translations
    # the algorithm operates on the "internal" request format.
    # every time there's an update (e.g., changes in request status, this has to 
    # be reflected in both tables
    self.db_collection_external = self.db["placement_requests_ext"]
    self.db_collection_external.create_index("ReqId", unique=True)


  def start_server(self):
    """Start the server.

    A call to this function is necessary to start listening to requests. The API endpoints are registered
    here. The following functions are currently supported:
    - [POST] /PAComp: Receives a placement request and starts an instance of the algorithm to handle it.
    - [GET] /PAComp/ReqId: Retrieves information about the request identified by ReqId.
    - [GET] /PaComp: List all past and pending requests.
    """
    app = Flask(__name__)
    app.add_url_rule(self.base_url + 'PAComp', 'receive_request', self.receive_request, methods=['POST'])
    app.add_url_rule(self.base_url + 'PAComp/<string:id>', 'get_request', self.get_request, methods=['GET'])
    app.add_url_rule(self.base_url + 'PAComp', 'list_requests', self.list_requests, methods=['GET'])
    app.run(host="0.0.0.0", port=self.port, debug=True, threaded=True)


  #############################################################################
  #                              API handlers                                 #
  #############################################################################

  def get_request(self, id):
    """API handler for retrieving information about a request identified by id.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    req = self.db_collection.find_one_and_update({"ReqId": id}, {'$set': {"checked": timestamp}}, projection={"_id": False})
    req_ext = self.db_collection_external.find_one_and_update({"ReqId": id}, {'$set': {"checked": timestamp}}, projection={"_id": False})
    return jsonify(req_ext), 200


  def list_requests(self):
    """API handler for retrieving the list of requests.
    """
    retval = []
    reqs = self.db_collection_external.find(projection={"_id": False})
    for r in reqs:
      retval.append(r)
    return jsonify(retval), 200


  def receive_request(self):
    """API handler for launching the placement algorithm.
    """
    # add stuff to database
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    
    req_ext = {
      "status": "INPROGRESS",
      "info": None,
      "created": timestamp,
      "checked": timestamp,
      "finished": None,
      "solution": None
    }
    # add the request as it was submitted in the above structure
    req_ext.update(request.json)    
    self.db_collection_external.insert_one(req_ext)

    # now do the necessary translation to the internal representation
    req_internal = translator.translate_request(request.json)
    req = {
      "ReqId": req_internal["ReqId"],
      "status": "INPROGRESS",
      "info": None,
      "scenario": None,
      "callback": req_internal["callback"],
      "created": timestamp,
      "checked": timestamp,
      "finished": None,
      "solution": None
    }
    self.db_collection.insert_one(req)

    scenario = {}
    scenario.update(req_internal["nfvi"])
    scenario.update(req_internal["nsd"])

    self.db_collection.find_one_and_update(
      {"ReqId": req["ReqId"]}, 
      {'$set': {"scenario": scenario}},
      projection={"_id": False},
      return_document=pymongo.collection.ReturnDocument.AFTER)

    # start thread
    t = threading.Thread(target=self._placement_algorithm_execute, kwargs=dict(scenario=scenario, callback=req_internal["callback"], reqid=req_internal["ReqId"]))
    t.start()

    return jsonify({"status": "created"}), 201


  #############################################################################
  #                          Internal methods                                 #
  #############################################################################

  def _execute_callback(self, callback, data, reqid):
    """For the given request ID, POST the data (JSON) to the callback URL which should have been
    provided by the caller when sending a placement request. This function is called by the
    thread that runs the placement algorithm, as soon as the latter has terminated.
    """
    r = requests.post(callback, data=json.dumps(data), headers={"Content-Type":"application/json"})
    print r.text
 

  def _placement_algorithm_execute(self, scenario, callback, reqid):
    """Thread function which executes the placement algorithm for the given scenario.
    The thread is started inside the receive_request method. At the end of the execution,
    the solution is posted to the callback URL. If for some reason the algorithm fails
    to produce a valid placement (e.g., some constraint is violated), the function still 
    posts the placement, but specific error information are included inside the JSON object
    which represents the solution. 
    """

    cfg = copy.deepcopy(self.configuration)
    cfg["scenario"] = scenario
    g = GA(cfg)
    solution = g.execute()

    # Check for errors/constrain violations
    err = None
    if not solution["solution_performance"]["link_capacity_constraints_ok"]:
      err = "Link capacity exceeded."
    if not solution["solution_performance"]["delay_constraints_ok"]:
      err = "Delay constraints violated."
    if not solution["solution_performance"]["host_capacity_constraints_ok"]:
      err = "Host capacity constraints violated."
    if not solution["solution_performance"]["legal_placement"]:
      err = "Illegal placement."

    self._output_solution(solution)

    # update the record in the database with the new status and the derived solution
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    if err is not None:
      status = "FAIL"
    else:
      status = "SUCCESS"
    req = self.db_collection.find_one_and_update(
      {"ReqId": reqid}, 
      {'$set': {"finished": timestamp, "solution": solution, "status": status, "info": err}},
      projection={"_id": False},
      return_document=pymongo.collection.ReturnDocument.AFTER)

    # translate solution to the external format
    translated_solution = translator.translate_solution(solution)

    req_ext = self.db_collection_external.find_one_and_update(
      {"ReqId": reqid}, 
      {'$set': {"finished": timestamp, "solution": translated_solution, "status": status, "info": err}},
      projection={"_id": False},
      return_document=pymongo.collection.ReturnDocument.AFTER)

    # execute callback
    self._execute_callback(callback, translated_solution, reqid)


  def _output_solution(self, solution):
    """Save the solution to a file (path supplied as part of the configuration) or print
    it to stdout (JSON format).
    """
    tostdout = False
    try:
      outf = open(self.configuration["solution_file"], "w")
    except:
      print "Could not open solution output file. Using stdout instead.\n"
      tostdout = True

    if tostdout:
      print helpers.to_chromosome(solution)
    else:
      json.dump(solution, outf, indent=2)

    # show solution performance
    info = solution["solution_performance"]
    if self.configuration["loglevel"].upper() != "NONE":
      print "-------------------------------"
      print "Finished after " + str(info["generations"]) + " generations [" + str(info["execution_time"]) + " seconds]"
      print "Selected solution information: Cost: " + str(info["cost"]) + ", service availability: " + str(info["availability"]) + ", latency (nwk/proc/total): " + str(info["latency"]["network"]) + "/" + str(info["latency"]["processing"]) + "/" + str(info["latency"]["total"])

    print str(info["cost"]) + "\t" + str(info["availability"]) + "\t" + str(info["latency"]["network"]) + "\t" + str(info["latency"]["processing"]) + "\t" + str(info["latency"]["total"]) +"\t" + str(info["generations"]) + "\t" + str(info["execution_time"])


#############################################################################
#############################################################################

def _load_configuration(configfile):
  """Loads configuration options from the configfile path (yaml-formatted).
  """

  try:
      f = open(configfile)
  except:
      print "Could not open configuration file " + configfile
      exit(2)
      
  try:
      configuration = yaml.load(f)
  except:
      print "Error loading configuration file. Possibly malformed..."
      exit(3)
  return configuration


if __name__ == '__main__':    
  # open configuration file
  myopts, args = getopt.getopt(sys.argv[1:], "c:")
  configfile = None
  for o, a in myopts:
    if o == "-c":
      configfile = a

  if configfile == None:
    print "Missing configuration file. Usage: python GA.py -c /path/to/configfile"
    exit(1)

  # load algorithm-specific configuration/settings
  configuration = _load_configuration(configfile)

  # initialize API server (version == 1)
  GAFE = GAFrontEnd(configuration, 1)

  # start listening for requests
  GAFE.start_server()

