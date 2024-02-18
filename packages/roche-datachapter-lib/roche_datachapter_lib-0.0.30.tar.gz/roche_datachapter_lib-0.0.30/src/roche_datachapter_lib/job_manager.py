"""SQL Server Agent Job Manager Module"""
from .db_config import DB_CONFIG
from .__domain__ import app, db, Job
from .result_type import ResultType


class JobManager():
    """Manager for SQL Server Agent Jobs"""
    __DEFAULT_BIND__ = 'sqlserver_msdb'
    __SP_CREATE_JOB__ = 'msdb.dbo.sp_add_job'
    __SP_UPDATE_JOB__ = 'msdb.dbo.sp_update_job'
    __SP_CREATE_JOB_STEP__ = 'msdb.dbo.sp_add_jobstep'
    __SP_UPDATE_JOB_STEP__ = 'msdb.dbo.sp_update_jobstep'
    __SP_ADD_JOB_SERVER__ = 'msdb.dbo.sp_add_jobserver'
    __DEFAULT_JOB_PARAMS__ = {
        'description': 'Job created by python setup_deploy script. No description available.',
        'category_name': 'Data Collector',
        'enabled': 1,
        'notify_level_eventlog': 0,
        'notify_level_email': 2,
        'notify_level_netsend': 0,
        'notify_level_page': 0,
        'delete_level': 0}
    __DEFAULT_JOB_FIRST_PARAMS__ = {
        'step_id': 1,
        'step_name': 'Execute run_app.bat',
        'cmdexec_success_code': 0,
        'on_success_action': 1,
        'on_success_step_id': 0,
        'on_fail_action': 2,
        'on_fail_step_id': 0,
        'retry_attempts': 0,
        'retry_interval': 0,
        'os_run_priority': 0,
        'subsystem': 'CmdExec',
        'flags': 0,
        'proxy_name': 'proxySISS_digitaa2'}
    __DEFAULT_JOB_SERVER_NAME = '(local)'

    @classmethod
    def __execute_sp_on_default_bind__(cls, sp_name: str, sp_params: dict = None):
        return DB_CONFIG.execute_stored_procedure(sp_name, sp_params, cls.__DEFAULT_BIND__)

    @classmethod
    def __job_has_step_one__(cls, p_job_id: str = '') -> bool:
        """Return True if the given job already has step 1, else False"""
        q = f"SELECT step_id FROM msdb.dbo.sysjobsteps WHERE job_id = '{
            p_job_id}' and step_id=1"
        existing_job_step = DB_CONFIG.execute_custom_select_query(
            q, cls.__DEFAULT_BIND__, ResultType.JSON_LIST)
        if existing_job_step and isinstance(existing_job_step[0], dict):
            return existing_job_step[0].get('step_id') is not None
        return False

    @classmethod
    def get_job_id_by_job_name(cls, p_job_name: str = '') -> str:
        """Return the job id for a given job name if exists or None if no match"""
        with app.app_context():
            existing_job = db.session.query(
                Job).filter_by(name=p_job_name).first()
            if existing_job:
                return str(existing_job.job_id)
        return None

    @classmethod
    def create_python_job(cls, p_job_name: str = '', p_owner: str = '', p_path_to_bat_file: str = ''):
        """Create a job with first step configurations"""
        step_params = cls.__DEFAULT_JOB_FIRST_PARAMS__.copy()
        step_params['command'] = f'cmd.exe /c "{p_path_to_bat_file}"'
        job_params = cls.__DEFAULT_JOB_PARAMS__.copy()
        job_params['job_name'] = p_job_name
        job_params['owner_login_name'] = p_owner
        cls.__execute_sp_on_default_bind__(
            cls.__SP_CREATE_JOB__, job_params)
        just_created_job_id = cls.get_job_id_by_job_name(p_job_name)
        if just_created_job_id:
            step_params['job_id'] = just_created_job_id
            cls.__execute_sp_on_default_bind__(
                cls.__SP_CREATE_JOB_STEP__, step_params)
            cls.__execute_sp_on_default_bind__(
                cls.__SP_ADD_JOB_SERVER__, {'job_id': just_created_job_id, 'server_name': cls.__DEFAULT_JOB_SERVER_NAME})

    @classmethod
    def update_python_job(cls, p_job_id: str = '', p_owner: str = '', p_path_to_bat_file: str = ''):
        """Update a job and first step configurations"""
        step_params = cls.__DEFAULT_JOB_FIRST_PARAMS__.copy()
        step_params['command'] = f'cmd.exe /c "{p_path_to_bat_file}"'
        if p_job_id:
            cls.__execute_sp_on_default_bind__(
                cls.__SP_UPDATE_JOB__, {'job_id': p_job_id, 'owner_login_name': p_owner})
            step_params['job_id'] = p_job_id
            if cls.__job_has_step_one__(p_job_id):
                cls.__execute_sp_on_default_bind__(
                    cls.__SP_UPDATE_JOB_STEP__, step_params)
            else:
                cls.__execute_sp_on_default_bind__(
                    cls.__SP_CREATE_JOB_STEP__, step_params)
