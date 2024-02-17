"""Logger"""
from os.path import (isdir, join as path_join)
import logging
from datetime import datetime, UTC
from .__domain__ import db, app, JobExecution, JobExecutionLog
from .job_manager import JobManager


class Logger():
    """This Logger persists the logs in a specific file for each execution of the process.
     If enable_db_logging is True it also persists in the Database.
     Please note that each log is persisted individually, use with caution to avoid slowing down the process"""

    def __init__(self, logs_dir: str, job_name: str, enable_db_logging: bool):
        if isdir(logs_dir):
            self.start_time = datetime.now(UTC)
            self.file_logger = logging
            self.job_name = job_name
            logs_path = path_join(
                logs_dir,
                f'process_{self.start_time.strftime("%Y%m%d_%H.%M.%S")}.log',
            )
            self.file_logger.basicConfig(
                level=logging.INFO,
                filename=logs_path,
                filemode="w",
                format="%(name)s - %(levelname)s - %(message)s",
                encoding="utf-8",
            )
            if isinstance(enable_db_logging, bool) and enable_db_logging:
                try:
                    self.enable_db_logging = bool(enable_db_logging)
                    self.job_id = JobManager.get_job_id_by_job_name(job_name)
                    if self.job_id:
                        with app.app_context():
                            execution = JobExecution(self.job_id)
                            db.session.add(execution)
                            db.session.commit()
                            self.execution_id = execution.id
                    else:
                        self.file_logger.warning(
                            f"NO se encontró el job '{job_name}'. Los logs de esta ejecución NO se persistirán en la Base de Datos.")
                except Exception as e:
                    raise ValueError(
                        f"Error al inicializar ejecución del job '{job_name}'") from e
            else:
                self.file_logger.warning(
                            f"Los logs a la Base de Datos están desactivados: enable_db_logging={enable_db_logging}")
                self.enable_db_logging = False
                self.job_id = None
        else:
            raise ValueError(
                "El parámetro logs_dir debe ser la ruta a un directorio/carpeta.")

    def __enter__(self):
        return self

    def _log_to_db(self, level, message):
        if self.enable_db_logging and self.job_id:
            with app.app_context():
                level_name = self.file_logger.getLevelName(level)
                log_dict = {'level': level_name, 'msg': message}
                job_execution_log = JobExecutionLog(
                    self.execution_id, log_dict)
                db.session.add(job_execution_log)
                db.session.commit()

    def log(self, level, message):
        self.file_logger.log(level, message)
        self._log_to_db(level, message)

    def debug(self, message):
        self.log(logging.DEBUG, message=message)

    def info(self, message):
        self.log(logging.INFO, message=message)

    def warning(self, message):
        self.log(logging.WARNING, message=message)

    def error(self, message):
        self.log(logging.ERROR, message=message)

    def critical(self, message):
        self.log(logging.CRITICAL, message=message)

    def __exit__(self, exc_type, exc_value, traceback):
        if self.job_id:
            with app.app_context():
                execution = db.session.query(JobExecution).filter_by(
                    id=self.execution_id).first()
                if execution:
                    if traceback:
                        execution.finish(f"Exception: {str(exc_type)}")
                    else:
                        execution.finish()
                db.session.commit()
