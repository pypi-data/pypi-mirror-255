"""DD Domain Module
Internal Module:
This module is intended for internal use only. It contains utilities and functions
used internally within the library. External use is not recommended.
"""
from __future__ import annotations
import dataclasses
from datetime import datetime, UTC
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.event import listens_for
from .db_config import DbConfig

try:
    app = Flask(__name__)
    app.config.from_object(DbConfig())
    db = SQLAlchemy(app)

    class StrRepresentable():
        """Abstract class for string representation"""

        def __repr__(self):
            """String representation"""
            public_attributes = {
                key: value for key, value in self.__dict__.items() if not key.startswith('_')}
            attributes = ', '.join(
                f"{key}: {value}" for key, value in public_attributes.items()
            )
            return f"{self.__class__.__name__} -> {attributes}"

    @dataclasses.dataclass
    class Job(db.Model, StrRepresentable):
        """Job entity class
        Internal Utility Class:
        This class is intended for internal use only. It provides utility functionality
        used internally within the library. External use is not recommended."""
        __bind_key__ = DbConfig.validate_bind('sqlserver_msdb')
        __table_args__ = {"schema": 'dbo'}
        __tablename__ = 'sysjobs'
        job_id = db.Column(UNIQUEIDENTIFIER, primary_key=True)
        originating_server_id = db.Column(db.Integer)
        name = db.Column(db.String(128))
        enabled = db.Column(db.Boolean)
        description = db.Column(db.String(512))
        start_step_id = db.Column(db.Integer)
        category_id = db.Column(db.Integer)
        owner_sid = db.Column(db.String(85))
        notify_level_eventlog = db.Column(db.Integer)
        notify_level_email = db.Column(db.Integer)
        notify_level_netsend = db.Column(db.Integer)
        notify_level_page = db.Column(db.Integer)
        notify_email_operator_id = db.Column(db.Integer)
        notify_netsend_operator_id = db.Column(db.Integer)
        notify_page_operator_id = db.Column(db.Integer)
        delete_level = db.Column(db.Integer)
        date_created = db.Column(db.DateTime)
        date_modified = db.Column(db.DateTime)
        version_number = db.Column(db.Integer)

    @dataclasses.dataclass
    class JobExecution(db.Model, StrRepresentable):
        """JobExecution entity class
        Internal Utility Class:
        This class is intended for internal use only. It provides utility functionality
        used internally within the library. External use is not recommended."""
        __bind_key__ = DbConfig.validate_bind('sqlserver_msdb')
        __table_args__ = {"schema": 'dbo'}
        __tablename__ = 'sysjob_execution'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        job_id = db.Column(UNIQUEIDENTIFIER, db.ForeignKey(Job.job_id))
        status = db.Column(db.Integer)
        utc_start_time = db.Column(db.DateTime)
        utc_end_time = db.Column(db.DateTime)
        observations = db.Column(db.String(255))

        def __init__(self, job_id: str):
            self.job_id = job_id
            # 0:No Iniciado, 1:En progreso, 2:Finalizado con Éxito, 3:Fallo en Tarea
            self.status = 1
            self.utc_start_time = datetime.now(UTC)

        def finish(self, observations: str = "Sin observaciones"):
            """Finish this job execution"""
            # 0:No Iniciado, 1:En progreso, 2:Finalizado con Éxito, 3:Fallo en Tarea
            self.status = 2
            self.utc_end_time = datetime.now(UTC)
            self.observations = observations

    @dataclasses.dataclass
    class JobExecutionLog(db.Model, StrRepresentable):
        """Log entity class"""
        __bind_key__ = DbConfig.validate_bind('sqlserver_msdb')
        __table_args__ = {"schema": 'dbo'}
        __tablename__ = 'sysjob_execution_logs'
        id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
        job_execution_id = db.Column(db.BigInteger)
        utc_created_time = db.Column(db.DateTime)
        level = db.Column(db.String(20))
        message = db.Column(db.String(1000))
        #script_pathname = db.Column(db.String(255))
        #so_process_id = db.Column(db.Integer)

        def __init__(self, job_execution_id: int, log_record: dict):
            self.job_execution_id = job_execution_id
            self.utc_created_time = datetime.now(UTC)
            try:
                self.level = log_record['level']
                self.message = log_record['msg']
                #self.script_pathname = log_record['pathname']
                #self.so_process_id = log_record['process']
            except KeyError as err:
                raise ValueError(
                    f"No se pudo inicializar {self.__class__}: Clave faltante - {err}") from err

    @dataclasses.dataclass
    class JobHistory(db.Model, StrRepresentable):
        """JobExecution entity class
        Internal Utility Class:
        This class is intended for internal use only. It provides utility functionality
        used internally within the library. External use is not recommended."""
        __bind_key__ = DbConfig.validate_bind('sqlserver_msdb')
        __table_args__ = {"schema": 'dbo'}
        __tablename__ = 'sysjobhistory'
        instance_id = db.Column(db.Integer, primary_key=True)
        job_id = db.Column(UNIQUEIDENTIFIER, db.ForeignKey(Job.job_id))
        step_id = db.Column(db.Integer)
        step_name = db.Column(db.String(128))
        sql_message_id = db.Column(db.Integer)
        sql_severity = db.Column(db.Integer)
        message = db.Column(db.String(1000))
        run_status = db.Column(db.Integer)
        run_date = db.Column(db.Integer)
        run_time = db.Column(db.Integer)
        run_duration = db.Column(db.Integer)
        operator_id_emailed = db.Column(db.Integer)
        operator_id_netsent = db.Column(db.Integer)
        operator_id_paged = db.Column(db.Integer)
        retries_attempted = db.Column(db.Integer)
        server = db.Column(db.String(128))

except Exception as e:
    raise ConnectionError(f"Error en definición de dominio. {e}") from e


@listens_for(Job, 'before_insert')
@listens_for(Job, 'before_update')
@listens_for(Job, 'before_delete')
@listens_for(JobHistory, 'before_insert')
@listens_for(JobHistory, 'before_update')
@listens_for(JobHistory, 'before_delete')
def prevent_write_operations(mapper, connection, target):
    """Prevent write operations"""
    raise NotImplementedError(
        "Write operations are not allowed on this entity.")
