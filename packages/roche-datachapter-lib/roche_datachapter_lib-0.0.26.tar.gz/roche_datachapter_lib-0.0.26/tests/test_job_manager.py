"""Tests for job manager module"""
from roche_datachapter_lib.job_manager import JobManager

JOBNAME = 'AA_TEST_JOB_CREATION_WITH_PYTHON'
USER = 'RNUMDMAS\\osirisl'
PATH = 'C:\\Users\\Lucas\\run_app.bat'
existing_job_id = JobManager.get_job_id_by_job_name(JOBNAME)
if not existing_job_id:
    print(f"creating job {JOBNAME}")
    JobManager.create_python_job(JOBNAME, USER, PATH)
else:
    print(f"updating job {JOBNAME}")
    JobManager.update_python_job(existing_job_id, USER, PATH)

JobManager.create_python_job(JOBNAME, USER, PATH)