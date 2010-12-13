from basesettings import *

ROOT_URLCONF = 'irgsh_web.xmlrpcurls'

XMLRPC_METHODS = (
    ('jobs.xmlrpc.get_new_tasks', 'get_new_tasks'),
    ('jobs.xmlrpc.get_task_info', 'get_task_info'),
    ('jobs.xmlrpc.populate_debian_info', 'populate_debian_info'),
    ('jobs.xmlrpc.set_debian_copy', 'set_debian_copy'),
    ('jobs.xmlrpc.set_orig_copy', 'set_orig_copy'),
    ('jobs.xmlrpc.xstart_assigning', 'start_assigning'),
    ('jobs.xmlrpc.set_orig_copy', 'set_orig_copy'),
    ('jobs.xmlrpc.task_init_failed', 'task_init_failed'),
    ('jobs.xmlrpc.xstart_running', 'start_running'),
    ('jobs.xmlrpc.assign_task', 'assign_task'),
    ('jobs.xmlrpc.assignment_download', 'assignment_download'),
    ('jobs.xmlrpc.assignment_environment', 'assignment_environment'),
    ('jobs.xmlrpc.assignment_building', 'assignment_building'),
    ('jobs.xmlrpc.assignment_upload', 'assignment_upload'),
    ('jobs.xmlrpc.assignment_complete', 'assignment_complete'),
    ('jobs.xmlrpc.assignment_fail', 'assignment_fail'),
    ('jobs.xmlrpc.assignment_cancel', 'assignment_cancel'),
    ('jobs.xmlrpc.assignment_wait_for_upload', 'assignment_wait_for_upload'),
    ('jobs.xmlrpc.assignment_wait_for_installing', 'assignment_wait_for_installing'),
    ('jobs.xmlrpc.assignment_upload_log', 'assignment_upload_log'),
    ('jobs.xmlrpc.get_unassigned_task', 'get_unassigned_task'),
    ('jobs.xmlrpc.get_assignment_for_builder', 'get_assignment_for_builder'),
    ('jobs.xmlrpc.builder_ping', 'builder_ping'),
    ('jobs.xmlrpc.get_assignment_info', 'get_assignment_info'),
    ('jobs.xmlrpc.get_assignments_to_upload', 'get_assignments_to_upload'),
    ('jobs.xmlrpc.get_assignments_to_install', 'get_assignments_to_install'),
)
