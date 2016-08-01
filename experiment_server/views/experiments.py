from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface
from pyramid.httpexceptions import HTTPFound
import json
import datetime


@view_defaults(renderer='json')
class Experiments:
	def __init__(self, request):
		self.request = request
		self.DB = DatabaseInterface(self.request.dbsession)

	@view_config(route_name='experiments', request_method="OPTIONS")
	def experiments_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS')
		return res

	#1 Create new experiment
	@view_config(route_name='experiments', request_method="POST")
	def experiments_POST(self):
		data = self.request.json_body
		name = data['name']
		experimentgroups = data['experimentgroups']
		startDatetime = data['startDatetime']
		endDatetime = data['endDatetime']
		size = int(data['size'])
		expgroups = []
		for i in range(len(experimentgroups)):
			expgroup = self.DB.createExperimentgroup({'name': experimentgroups[i]['name']})
			expgroups.append(expgroup)
			confs = experimentgroups[i]['configurations']
			for j in range(len(confs)):
				key = confs[j]['key']
				value = confs[j]['value']
				self.DB.createConfiguration({'key':key, 'value':value, 'experimentgroup':expgroup})
		experiment = self.DB.createExperiment(
			{'name': name, 
			'startDatetime': startDatetime,
			'endDatetime': endDatetime,
			'experimentgroups': expgroups,
			'size': size
			});
		result = json.dump({'data': experiment})
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		#Experimenter sends double request
		print("%s REST method=POST, url=/experiments, action=Create new experiment, result=%s" % (datetime.datetime.now(), result))
		return res

	#2 List all experiments
	@view_config(route_name='experiments', request_method="GET")
	def experiments_GET(self):
		experiments = self.DB.getAllExperiments()
		experimentsJSON = []
		for i in range(len(experiments)):
			experiment = experiments[i].as_dict()
			experiment['status'] = self.DB.getStatusForExperiment(experiments[i].id)
			experimentsJSON.append(experiment)
		result = json.dumps({'data': experimentsJSON})
		headers = ()
		res = Response(result)
		res.headers.add('Access-Control-Allow-Origin', '*')
		print("%s REST method=GET, url=/experiments, action=List all experiments, result=%s" % (datetime.datetime.now(), result))
		return res

	@view_config(route_name='experiment_metadata', request_method="OPTIONS")
	def experiment_metadata_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
		return res

	#3 Show specific experiment metadata
	@view_config(route_name='experiment_metadata', request_method="GET")
	def experiment_metadata_GET(self):
		id = int(self.request.matchdict['id'])
		experiment = self.DB.getExperiment(id)
		if experiment is None:
			result = None
			headers = ()
			res = Response(result)
			res.status_code = 400
			res.headers.add('Access-Control-Allow-Origin', '*')
			print("%s REST method=GET, url=/experiments/%d/metadata, action=Show specific experiment metadata, result=%s" % (datetime.datetime.now(), id, result))
			return res
		experimentAsJSON = experiment.as_dict()
		totalDataitems = self.DB.getTotalDataitemsForExperiment(id)
		experimentgroups = []
		for i in range(len(experiment.experimentgroups)):
			expgroup = experiment.experimentgroups[i]
			expgroupAsJSON = expgroup.as_dict()
			totalDataitemsForExpgroup = self.DB.getTotalDataitemsForExpgroup(expgroup.id)
			confs = expgroup.configurations
			users = []
			for i in range(len(expgroup.users)):
				users.append(expgroup.users[i].as_dict())
			configurations = []
			for i in range(len(confs)):
				configurations.append(confs[i].as_dict())
			expgroupAsJSON['configurations'] = configurations
			expgroupAsJSON['users'] = users
			experimentgroups.append(expgroupAsJSON)
		experimentAsJSON['experimentgroups'] = experimentgroups
		experimentAsJSON['totalDataitems'] = totalDataitems
		experimentAsJSON['status'] = self.DB.getStatusForExperiment(experiment.id)
		result = json.dumps({'data': experimentAsJSON})
		headers = ()
		res = Response(result)
		res.headers.add('Access-Control-Allow-Origin', '*')
		print("%s REST method=GET, url=/experiments/%d/metadata, action=Show specific experiment metadata, result=%s" % (datetime.datetime.now(), id, result))
		return res

	@view_config(route_name='experiment', request_method="OPTIONS")
	def experiment_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'DELETE,OPTIONS')
		return res

	#4 Delete experiment
	@view_config(route_name='experiment', request_method="DELETE")
	def experiment_DELETE(self):
		id = int(self.request.matchdict['id'])
		result = self.DB.deleteExperiment(id)
		headers = ()
		res = Response()
		if result:
			result = 'Succeeded'
			res.status_code = 200
		else:
			result = 'Failed'
			res.status_code = 400
		res.headers.add('Access-Control-Allow-Origin', '*')
		print("%s REST method=DELETE, url=/experiments/%d, action=Delete experiment, result=%s" % (datetime.datetime.now(), id, result))
		return res

	@view_config(route_name='users_for_experiment', request_method="OPTIONS")
	def users_for_experiment_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
		return res

	#7 List all users for specific experiment
	@view_config(route_name='users_for_experiment', request_method="GET")
	def users_for_experiment_GET(self):
		id = int(self.request.matchdict['id'])
		users = self.DB.getUsersForExperiment(id)
		usersJSON = []
		for i in range(len(users)):
			user = users[i].as_dict()
			experimentgroup = self.DB.getExperimentgroupForUserInExperiment(users[i].id, id)
			user['experimentgroup'] = experimentgroup.as_dict()
			user['totalDataitems'] = self.DB.getTotalDataitemsForUserInExperiment(users[i].id, id)
			usersJSON.append(user)
		result = json.dumps({'data': usersJSON})
		headers = ()
		res = Response(result)
		res.headers.add('Access-Control-Allow-Origin', '*')
		print("%s REST method=GET, url=/experiments/%d/users, action=List all users for specific experiment, result=%s" % (datetime.datetime.now(), id, result))
		return res

	@view_config(route_name='experiment_data', request_method="OPTIONS")
	def experiment_data_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
		return res

	#11 Show specific experiment data
	@view_config(route_name='experiment_data', request_method="GET")
	def experiment_data_GET(self):
		expId = int(self.request.matchdict['id'])
		experiment = self.DB.getExperiment(expId)
		expgroups = experiment.experimentgroups
		experimentAsJSON = experiment.as_dict()
		experimentgroups = []
		for expgroup in expgroups:

			experimentgroup = expgroup.as_dict()
			dataitemsForExpgroup = []
			for dataitem in self.DB.getDataitemsForExperimentgroup(expgroup.id):
				dataitemsForExpgroup.append(dataitem.as_dict())
			experimentgroup['dataitems'] = dataitemsForExpgroup

			users = []
			for user in expgroup.users:
				userAsJSON = user.as_dict()
				dataitemsForUser = []
				for dataitem in self.DB.getDataitemsForUserInExperiment(user.id, expId):
					dataitemsForUser.append(dataitem.as_dict())
				userAsJSON['dataitems'] = dataitemsForUser
				users.append(userAsJSON)

			experimentgroup['users'] = users
			experimentgroups.append(experimentgroup)
		dataitemsForExperiment = []
		for dataitem in self.DB.getDataitemsForExperiment(expId):
			dataitemsForExperiment.append(dataitem.as_dict())
		result = {'data': {'experiment': experimentAsJSON, 'dataitems': dataitemsForExperiment,
		'experimentgroups': experimentgroups}}
		print("%s REST method=GET, url=/experiments/{id}/data, action=Show specific experiment data, result=%s" % (datetime.datetime.now(), result))
		return result

	@view_config(route_name='experimentgroup', request_method="OPTIONS")
	def experimentgroup_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'GET,DELETE,OPTIONS')
		return res

	#13 Show specific experimentgroup metadata
	@view_config(route_name='experimentgroup', request_method="GET")
	def experimentgroup_GET(self):
		id = int(self.request.matchdict['expgroupid'])
		expgroup = self.DB.getExperimentgroup(id)
		confs = expgroup.configurations
		configurations = []
		for i in range(len(confs)):
				configurations.append(confs[i].as_dict())
		users = []
		for i in range(len(expgroup.users)):
			users.append(expgroup.users[i].as_dict())
		experimentgroup = expgroup.as_dict()
		experimentgroup['configurations'] = configurations
		experimentgroup['users'] = users
		experimentgroup['totalDataitems'] = self.DB.getTotalDataitemsForExpgroup(expgroup.id)
		result = json.dumps({'data': experimentgroup})
		headers = ()
		res = Response(result)
		res.headers.add('Access-Control-Allow-Origin', '*')
		print("%s REST method=GET, url=/experimentgroups/{id}, action=Show specific experimentgroup metadata, result=%s" % (datetime.datetime.now(), result))
		return res

	#12 Delete experimentgroup
	@view_config(route_name='experimentgroup', request_method="DELETE")
	def experimentgroup_DELETE(self):
		id = int(self.request.matchdict['expgroupid'])
		result = self.DB.deleteExperimentgroup(id)
		if result:
			result = 'Succeeded'
		else:
			result = 'Failed'
		headers = ()
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		print("%s REST method=GET, url=/experiments/{expid}/experimentgroups/{expgroupid}, action=Delete experimentgroup, result=%s" % (datetime.datetime.now(), result))
		return res

	@view_config(route_name='user_for_experiment', request_method="OPTIONS")
	def user_for_experiment_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'DELETE,OPTIONS')
		return res

	#14 Delete user from specific experiment
	@view_config(route_name='user_for_experiment', request_method="DELETE")
	def user_for_experiment_DELETE(self):
		experimentId = int(self.request.matchdict['expid'])
		userId = int(self.request.matchdict['userid'])
		result = self.DB.deleteUserFromExperiment(userId, experimentId)
		if result:
			result = 'Succeeded'
		else:
			result = 'Failed'
		headers = ()
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		print("%s REST method=GET, url=/experiments/{expid}/users/{userid}', action=Delete user from specific experiment, result=%s" % (datetime.datetime.now(), result))
		return res

