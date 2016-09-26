from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface
import datetime
from experiment_server.utils.log import print_log
from .webutils import WebUtils
from experiment_server.models.applications import Application
import sqlalchemy.orm.exc

@view_defaults(renderer='json')
class Applications(WebUtils):
    def __init__(self, request):
        self.request = request
        self.DB = DatabaseInterface(self.request.dbsession)

    @view_config(route_name='application', request_method="GET")
    def applications_GET_one(self):
        """ Find and return one application by id with GET method """
        app_id = int(self.request.matchdict['id'])
        return Application.get(app_id).as_dict()

    @view_config(route_name='applications', request_method="GET")
    def applications_GET(self):
        """ List all applications with GET method """
        return list(map(lambda _: _.as_dict(), Application.all()))

    @view_config(route_name='applications', request_method="POST")
    def applications_POST(self):
        """ Create new application with POST method """
        data = self.request.json_body
        name = data['name']

        application = self.DB.create_application(
            {
                'name': name
            })

        result = {'data': application.as_dict()}
        print_log(name,'POST','/applications', 'Create new application', result)
        return self.createResponse(result, 200)

    @view_config(route_name='application', request_method="DELETE")
    def applications_DELETE_one(self):
        """ Find and delete one application by id with destroy method """
        app_id = int(self.request.matchdict['id'])
        try:
            if(Application.destroy(Application.get(app_id)) == None):
                return "Delete completed."
        except (sqlalchemy.orm.exc.UnmappedInstanceError):
            pass
            return "Delete failed."

    @view_config(route_name='configurationkeys_for_app', request_method="GET")
    def configurationkeys_for_application_GET(self):
        """ List all configurationkeys of specific application """
        id = int(self.request.matchdict['id'])
        return list(map(lambda _: _.as_dict(), Application.get(id).configurationkeys))

    @view_config(route_name='app_data', request_method="GET")
    def data_for_app_GET(self):
        """ List all configurationkeys and rangeconstraints of specific application.
            Returns application with configurationkeys, rangeconstraints of conf.keys,
            operator of rangeconstraints
        """
        id = int(self.request.matchdict['id'])
        application = Application.get(id)
        if application is None:
            return self.createResponse(None, 400)
        appAsJSON = application.as_dict()
        configurationkeys = []
        for i in range(len(application.configurationkeys)):
            ckey = application.configurationkeys[i]
            ckeyAsJSON = ckey.as_dict()
            rconstraints = ckey.rangeconstraints
            rangeconstraints = []
            for i in range(len(rconstraints)):
                rconstraint = rconstraints[i]
                rconstraintAsJSON = rconstraint.as_dict()
                operator = rconstraint.operator
                operatorAsJSON = operator.as_dict()
                rconstraintAsJSON['operator'] = operatorAsJSON
                rangeconstraints.append(rconstraintAsJSON)
            ckeyAsJSON['rangeconstraints'] = rangeconstraints
            configurationkeys.append(ckeyAsJSON)
        appAsJSON['configurationkeys'] = configurationkeys
        result = {'application': appAsJSON}
        return self.createResponse(result, 200)
