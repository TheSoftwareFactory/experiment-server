"This module contains all route-related functions"


def includeme(config):
    """Routes for every HTTP-endpoints"""
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('users', '/users')
    config.add_route('user', '/users/{id}')
    config.add_route('experiments_for_user', '/users/{id}/experiments')
    config.add_route('configurations', 'users/{id}/configurations')

    config.add_route('operators', '/operators')

    config.add_route('experiments', '/experiments')
    config.add_route('experiment_metadata', '/experiments/{id}/metadata')
    config.add_route('experiment', '/experiments/{id}')
    config.add_route('experimentgroup', '/experiments/{expid}/experimentgroups/{expgroupid}')
    config.add_route('users_for_experiment', '/experiments/{id}/users')
    config.add_route('user_for_experiment', '/experiments/{expid}/users/{userid}')
    config.add_route('events', '/events')
    config.add_route('experiment_data', '/experiments/{id}/data')
    config.add_route('applications', '/applications')
    config.add_route('application', '/applications/{id}')
    config.add_route('app_data', '/applications/{id}/data')
    config.add_route('configurationkeys', '/configurationkeys')
    config.add_route('configurationkeys_for_app', '/applications/{id}/configurationkeys')
    config.add_route('rangeconstraints_for_configurationkey', '/configurationkeys/{id}/rangeconstraints')
    config.add_route('exconstraints_for_configurationkey', '/configurationkeys/{id}/exclusionconstraints')
    config.add_route('configurationkey', '/configurationkeys/{id}')
    config.add_route('rangeconstraint', '/rangeconstraints/{id}')
    config.add_route('rangeconstraints', '/rangeconstraints')
    config.add_route('exclusionconstraints', '/exclusionconstraints')
    config.add_route('exclusionconstraint', '/exclusionconstraints/{id}')