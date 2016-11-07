from pyramid.response import Response
from pyramid.view import view_config, view_defaults

import datetime
from experiment_server.utils.log import print_log
from .webutils import WebUtils
from experiment_server.models.users import User
from experiment_server.models.dataitems import DataItem

from fn import _
from toolz import *

@view_defaults(renderer='json')
class Users(WebUtils):
    def __init__(self, request):
        self.request = request
        self.DB = DatabaseInterface(self.request.dbsession)


    """
        CORS-options
    """
    @view_config(route_name='users', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    @view_config(route_name='user', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    # List all users
    @view_config(route_name='users', request_method="GET", renderer='json')
    def users_GET(self):
        """
            Explanation: maps as_dict() -function to every User-object (this is returned by User.all())
            Creates a list and returns it. In future we might would like general json-serialization to make this even
            more simpler.
        """
        return list(map(lambda _: _.as_dict(), User.all()))

    # Create new user
    @view_config(route_name='users', request_method="POST", renderer='json')
    def create_user(self):
        req_user = self.request.swagger_data['user']
        user = User(
            username=req_user.username
        )
        User.save(user)
        return user.as_dict()

    # Get one user
    @view_config(route_name='user', request_method="GET", renderer='json')
    def user_GET(self):
        id = self.request.swagger_data['id']
        result = User.get(id)
        if not result:
            print_log('/users/%s failed' % id)
            return self.createResponse(None, 400)
        return result.as_dict()

    # Delete user
    @view_config(route_name='user', request_method="DELETE")
    def user_DELETE(self):
        id = self.request.swagger_data['id']
        result = User.get(id)
        if not result:
            print_log(datetime.datetime.now(), 'DELETE', '/users/' + str(id), 'Delete user', 'Failed')
            return self.createResponse(None, 400)
        User.destroy(result)
        print_log(datetime.datetime.now(), 'DELETE', '/users/' + str(id), 'Delete user', 'Succeeded')
        return {}

    # List configurations for specific user
    @view_config(route_name='configurations', request_method="GET")
    def configurations_GET(self):
        id = self.request.swagger_data['id']
        user = User.get(id)
        if user is None:
            print_log(datetime.datetime.now(), 'GET', '/configurations', 'List configurations for specific user', None)
            return self.createResponse(None, 400)

        current_groups = user.experimentgroups
        configs = list(map(lambda _: _.configurations, current_groups))
        result = list(map(lambda _: _.as_dict(), list(concat(configs))))
        return result

    # List all experiments for specific user
    @view_config(route_name='experiments_for_user', request_method="GET")
    def experiments_for_user_GET(self):
        id = self.request.swagger_data['id']
        user = User.get(id)
        if not user:
            return self.createResponse(None, 400)
        users_experimentgroups = user.experimentgroups
        experiments = map(lambda _: _.experiment, users_experimentgroups)
        # TODO: Add experimentgroups (= user's experimentgroups of that experiment) to experiment
        result = map(lambda _: _.as_dict(), experiments)
        return list(result)

    # Save experiment data
    @view_config(route_name='events', request_method="POST")
    def events_POST(self):
        json = self.request.json_body
        value = json['value']
        key = json['key']
        startDatetime = json['startDatetime']
        endDatetime = json['endDatetime']
        username = self.request.headers['username']
        user = User.get_by('username', username)
        if user is None:
            print_log(datetime.datetime.now(), 'POST', '/events', 'Save experiment data', None)
            return self.createResponse(None, 400)
        result = DataItem(
            user=user,
            value=value,
            key=key,
            startDatetime=startDatetime,
            endDatetime=endDatetime
        )
        DataItem.save(result)
        print_log(datetime.datetime.now(), 'POST', '/events', 'Save experiment data', result)
        return result.as_dict()
