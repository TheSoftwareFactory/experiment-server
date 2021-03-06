
import datetime
from .base_test import BaseTest
from ..models import (Application, Experiment, Client, ExperimentGroup, Configuration)
from experiment_server.views.experiments import Experiments


def strToDatetime(date):
    return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

# ---------------------------------------------------------------------------------
#                                DatabaseInterface
# ---------------------------------------------------------------------------------

class TestExperiments(BaseTest):
    def setUp(self):
        super(TestExperiments, self).setUp()
        self.init_database()
        self.init_databaseData()

    def test_createExperiment(self):
        experimentsFromDB = self.dbsession.query(Experiment).all()
        experimentgroups = self.dbsession.query(ExperimentGroup).all()
        experiment_count_before = Experiment.query().count()
        experiment = Experiment(name='Create Test Experiment',
            experimentgroups=[experimentgroups[0], experimentgroups[1]],
            startDatetime=strToDatetime('2016-01-01 00:00:00'),
            endDatetime=strToDatetime('2017-01-01 00:00:00'))

        Experiment.save(experiment)
        experiment_count_now = Experiment.query().count()

        assert experiment_count_now > experiment_count_before
        assert Experiment.get_by('name', 'Create Test Experiment') is not None

    def test_deleteExperiment(self):
        size_before = Experiment.query().count()
        Experiment.destroy(Experiment.get(1))
        size_now = Experiment.query().count()

        assert size_before > size_now

    def test_deleteExperiment_configurations_are_deleted(self):
        deleting = Experiment.get(1)
        Experiment.destroy(deleting)

        configurations = Configuration.query().join(ExperimentGroup).filter(ExperimentGroup.experiment_id == 1).all()

        assert configurations == []

    def test_deleteExperiment_experimentgroups_are_deleted(self):
        deleting = Experiment.get(1)
        Experiment.destroy(deleting)

        experimentgroups = ExperimentGroup.query()\
            .filter(ExperimentGroup.experiment_id == 1).all()

        assert experimentgroups == []

    def test_getStatusForExperiment(self):
        status = self.DB.get_status_for_experiment(1)
        assert status == 'running'
        newEndDatetime = strToDatetime('2016-06-01 00:00:00')
        self.dbsession.query(Experiment).filter_by(id=1).one().endDatetime = newEndDatetime
        status = self.DB.get_status_for_experiment(1)
        assert status == 'finished'
        newStartDatetime = strToDatetime('2017-01-01 00:00:00')
        newEndDatetime = strToDatetime('2017-06-01 00:00:00')
        self.dbsession.query(Experiment).filter_by(id=1).one().startDatetime = newStartDatetime
        self.dbsession.query(Experiment).filter_by(id=1).one().endDatetime = newEndDatetime
        status = self.DB.get_status_for_experiment(1)
        assert status == 'waiting'

    def test_getAllRunningExperiments(self):
        experiments = self.DB.get_all_running_experiments()
        experimentsFromDB = self.dbsession.query(Experiment).all()

        assert experiments == experimentsFromDB

    def test_getExperimentsclientParticipates(self):
        expForclient1 = self.DB.get_client_experiments_list(1)
        expForclient2 = self.DB.get_client_experiments_list(2)
        experimentsFromDB = self.dbsession.query(Experiment).all()

        assert expForclient1 == [experimentsFromDB[0]]
        assert expForclient2 == [experimentsFromDB[0]]

# ---------------------------------------------------------------------------------
#                                  REST-Inteface
# ---------------------------------------------------------------------------------

class TestExperimentsREST(BaseTest):
    def setUp(self):
        super(TestExperimentsREST, self).setUp()
        self.init_database()
        self.init_databaseData()
        self.req = self.dummy_request()

    def test_experiments_POST(self):
        self.req.swagger_data = {'appid': 1,
            'experiment': Experiment(
                name='Example Experiment',
                startDatetime=datetime.datetime(2016, 1, 1, 0, 0, 0),
                endDatetime=datetime.datetime(2017, 1, 1, 0, 0, 0))}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.experiments_POST()
        experiment = Experiment.get_by('name', 'Example Experiment').as_dict()

        assert response == experiment

    def test_experiments_GET(self):
        httpExperiments = Experiments(self.req)
        self.req.swagger_data = {'appid': 1}
        response = httpExperiments.experiments_GET()
        experiment = response[0]

        assert len(response) == 1
        assert experiment['id'] == 1
        assert experiment['name'] == 'Test experiment'
        assert experiment['startDatetime'] == '2016-01-01 00:00:00'
        assert experiment['endDatetime'] == '2017-01-01 00:00:00'
        assert experiment['status'] == 'running'

    def test_experiments_GET_one(self):
        httpExperiments = Experiments(self.req)
        self.req.swagger_data = {'appid': 1, 'expid':1}
        response = httpExperiments.experiments_GET_one()
        expected = Experiment.get(1).as_dict()
        expected['status'] = 'running'
        assert response == expected

    def test_experiments_GET_one_nonexistent_experiment(self):
        httpExperiments = Experiments(self.req)
        self.req.swagger_data = {'appid': 1, 'expid':2}
        response = httpExperiments.experiments_GET_one()
        expected = 400
        assert response.status_code == expected

    def test_experiment_DELETE(self):
        self.req.swagger_data = {'appid': 1, 'expid':1}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.experiment_DELETE()
        assert response == {}

    def test_experiment_DELETE_nonexistent_experiment(self):
        self.req.swagger_data = {'appid': 1, 'expid':2}
        print(self.req.matchdict)
        httpExperiments = Experiments(self.req)
        response = httpExperiments.experiment_DELETE()
        assert response.status_code == 400
        assert response.json == None

    def test_clients_for_experiment_GET(self):
        self.req.swagger_data = {'appid': 1, 'expid': 1}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.clients_for_experiment_GET()
        clients = [{'id': 1,
                  'clientname': 'First client'},
                 {'id': 2,
                  'clientname': 'Second client'}]
        assert response == clients

    def test_clients_for_experiment_GET_nonexistent_experiment(self):
        self.req.swagger_data = {'appid': 1, 'expid': 2}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.clients_for_experiment_GET()
        assert response.status_code == 400
        assert response.json == None

    def test_experimentgroup_GET(self):
        self.req.swagger_data = {'appid': 1, 'expid': 1}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.experimentgroup_GET()
        expected = list(map(lambda _: _.as_dict(), \
                    ExperimentGroup.query().join(Experiment).join(Application)\
                    .filter(Application.id == 1, Experiment.id == 1).all()))

        assert response == expected

    def test_experimentgroup_GET_nonexistent_experiment(self):
        self.req.swagger_data = {'appid': 1, 'expid': 2}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.experimentgroup_GET()
        expected = 400

        assert response.status_code == expected

    def test_experimentgroup_GET_one(self):
        self.req.swagger_data = {'appid': 1,'expgroupid': 1, 'expid': 1}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.experimentgroup_GET_one()
        experimentgroup = {
                            'id': 1,
                            'name': 'Group A',
                            'experiment_id': 1,
                           'configurations': [
                               {'experimentgroup_id': 1, 'key': 'v1', 'id': 1, 'value': 0.5},
                               {'experimentgroup_id': 1, 'key': 'v2', 'id': 2, 'value': True}],
                           'dataitems': [
                               {'id': 1,
                                'client_id': 1,
                                'key': 'key1',
                                'value': 10,
                                'startDatetime': '2016-01-01 00:00:00',
                                'endDatetime': '2016-01-01 01:01:01',
                                'client': {'id': 1, 'clientname': 'First client'}
                                },
                               {'id': 2,
                                'client_id':1,
                                'key': 'key2',
                                'value': 0.5,
                                'startDatetime': '2016-02-02 01:01:02',
                                'endDatetime': '2016-02-02 02:02:02',
                                'client': {'id': 1, 'clientname': 'First client'}
                                }
                           ],
                           'clients': [{'id': 1, 'clientname': 'First client'}]}
        assert response == experimentgroup

    def test_experimentgroup_GET_one_nonexistent_experiment(self):
        self.req.swagger_data = {'appid': 1,'expgroupid': 1, 'expid': 2}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.experimentgroup_GET_one()
        assert response.status_code == 400
        assert response.json == None

    def test_experimentgroup_DELETE(self):
        self.req.swagger_data = {'appid': 1, 'expid': 1, 'expgroupid': 1}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.experimentgroup_DELETE()
        assert response == {}

    def test_experimentgroup_DELETE_nonexistent_experiment_and_experimentgroup(self):
        self.req.swagger_data = {'appid': 1, 'expid': 2, 'expgroupid': 2}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.experimentgroup_DELETE()
        assert response.status_code == 400
