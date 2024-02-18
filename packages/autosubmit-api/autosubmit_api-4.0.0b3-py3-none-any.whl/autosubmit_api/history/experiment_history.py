#!/usr/bin/python

# Copyright 2015-2020 Earth Sciences Department, BSC-CNS
# This file is part of Autosubmit.

# Autosubmit is free software: you can redistribute it and/or modify
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# it under the terms of the GNU General Public License as published by
# Autosubmit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of

# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Autosubmit.  If not, see <http://www.gnu.org/licenses/>.
import os
import traceback
from .database_managers import database_models as Models
from ..history import utils as HUtils
from ..performance import utils as PUtils
from time import time, sleep
from ..history.database_managers.experiment_history_db_manager import ExperimentHistoryDbManager
from ..history.database_managers.database_manager import DEFAULT_JOBDATA_DIR, DEFAULT_HISTORICAL_LOGS_DIR
from ..history.strategies import PlatformInformationHandler, SingleAssociationStrategy, StraightWrapperAssociationStrategy, TwoDimWrapperDistributionStrategy, GeneralizedWrapperDistributionStrategy
from ..history.data_classes.job_data import JobData
from ..history.data_classes.experiment_run import ExperimentRun
from ..history.platform_monitor.slurm_monitor import SlurmMonitor
from ..history.internal_logging import Logging
from ..config.basicConfig import APIBasicConfig
from typing import List, Dict, Tuple, Any

SECONDS_WAIT_PLATFORM = 60

class ExperimentHistory():
  def __init__(self, expid, basic_config, experiment_history_db_manager, logger):
    # type: (str, APIBasicConfig, ExperimentHistoryDbManager, Logging) -> None
    self.expid = expid
    self._log = logger
    self.basic_config = basic_config
    self._job_data_dir_path = basic_config.JOBDATA_DIR
    self._historiclog_dir_path = basic_config.HISTORICAL_LOG_DIR
    try:
      self.manager = experiment_history_db_manager
    except Exception as exp:
      self._log.log(str(exp), traceback.format_exc())
      self.manager = None

  def initialize_database(self):
    try:
      self.manager.initialize()
    except Exception as exp:
      self._log.log(str(exp), traceback.format_exc())
      self.manager = None

  def is_header_ready(self):
    if self.manager:
      return self.manager.is_header_ready_db_version()
    return False


  def write_submit_time(self, job_name, submit=0, status="UNKNOWN", ncpus=0, wallclock="00:00", qos="debug", date="",
                        member="", section="", chunk=0, platform="NA", job_id=0, wrapper_queue=None, wrapper_code=None, children=""):
    try:
      next_counter = self._get_next_counter_by_job_name(job_name)
      current_experiment_run = self.manager.get_experiment_run_dc_with_max_id()
      job_data_dc = JobData(_id=0,
                    counter=next_counter,
                    job_name=job_name,
                    submit=submit,
                    status=status,
                    rowtype=self._get_defined_rowtype(wrapper_code),
                    ncpus=ncpus,
                    wallclock=wallclock,
                    qos=self._get_defined_queue_name(wrapper_queue, wrapper_code, qos),
                    date=date,
                    member=member,
                    section=section,
                    chunk=chunk,
                    platform=platform,
                    job_id=job_id,
                    children=children,
                    run_id=current_experiment_run.run_id)
      return self.manager.register_submitted_job_data_dc(job_data_dc)
    except Exception as exp:
      self._log.log(str(exp), traceback.format_exc())
      return None

  def write_start_time(self, job_name, start=0, status="UNKWOWN", ncpus=0, wallclock="00:00", qos="debug", date="",
                      member="", section="", chunk=0, platform="NA", job_id=0, wrapper_queue=None, wrapper_code=None, children=""):
    try:
      job_data_dc_last = self.manager.get_job_data_dc_unique_latest_by_job_name(job_name)
      if not job_data_dc_last:
        job_data_dc_last = self.write_submit_time(job_name=job_name,
                                                  status=status,
                                                  ncpus=ncpus,
                                                  wallclock=wallclock,
                                                  qos=qos,
                                                  date=date,
                                                  member=member,
                                                  section=section,
                                                  chunk=chunk,
                                                  platform=platform,
                                                  job_id=job_id,
                                                  wrapper_queue=wrapper_queue,
                                                  wrapper_code=wrapper_code)
        self._log.log("write_start_time {0} start not found.".format(job_name))
      job_data_dc_last.start = start
      job_data_dc_last.qos = self._get_defined_queue_name(wrapper_queue, wrapper_code, qos)
      job_data_dc_last.status = status
      job_data_dc_last.rowtype = self._get_defined_rowtype(wrapper_code)
      job_data_dc_last.job_id = job_id
      job_data_dc_last.children = children
      return self.manager.update_job_data_dc_by_id(job_data_dc_last)
    except Exception as exp:
      self._log.log(str(exp), traceback.format_exc())

  def write_finish_time(self, job_name, finish=0, status="UNKNOWN", ncpus=0, wallclock="00:00", qos="debug", date="",
                        member="", section="", chunk=0, platform="NA", job_id=0, out_file=None, err_file=None,
                        wrapper_queue=None, wrapper_code=None, children=""):
    try:
      job_data_dc_last = self.manager.get_job_data_dc_unique_latest_by_job_name(job_name)
      if not job_data_dc_last:
        job_data_dc_last = self.write_submit_time(job_name=job_name,
                                                  status=status,
                                                  ncpus=ncpus,
                                                  wallclock=wallclock,
                                                  qos=qos,
                                                  date=date,
                                                  member=member,
                                                  section=section,
                                                  chunk=chunk,
                                                  platform=platform,
                                                  job_id=job_id,
                                                  wrapper_queue=wrapper_queue,
                                                  wrapper_code=wrapper_code,
                                                  children=children)
        self._log.log("write_finish_time {0} submit not found.".format(job_name))
      job_data_dc_last.finish = finish if finish > 0 else int(time())
      job_data_dc_last.status = status
      job_data_dc_last.job_id = job_id
      job_data_dc_last.rowstatus = Models.RowStatus.PENDING_PROCESS
      job_data_dc_last.out = out_file if out_file else ""
      job_data_dc_last.err = err_file if err_file else ""
      return self.manager.update_job_data_dc_by_id(job_data_dc_last)
    except Exception as exp:
      self._log.log(str(exp), traceback.format_exc())

  def write_platform_data_after_finish(self, job_data_dc, platform_obj):
    """
    Call it in a thread.
    """
    try:
      sleep(SECONDS_WAIT_PLATFORM)
      ssh_output = platform_obj.check_job_energy(job_data_dc.job_id)
      slurm_monitor = SlurmMonitor(ssh_output)
      self._verify_slurm_monitor(slurm_monitor, job_data_dc)
      job_data_dcs_in_wrapper = self.manager.get_job_data_dcs_last_by_wrapper_code(job_data_dc.wrapper_code)
      job_data_dcs_to_update = []
      if len(job_data_dcs_in_wrapper) > 0:
        info_handler = PlatformInformationHandler(StraightWrapperAssociationStrategy(self._historiclog_dir_path))
        job_data_dcs_to_update = info_handler.execute_distribution(job_data_dc, job_data_dcs_in_wrapper, slurm_monitor)
        if len(job_data_dcs_to_update) == 0:
          info_handler.strategy = TwoDimWrapperDistributionStrategy(self._historiclog_dir_path)
          job_data_dcs_to_update = info_handler.execute_distribution(job_data_dc, job_data_dcs_in_wrapper, slurm_monitor)
        if len(job_data_dcs_to_update) == 0:
          info_handler.strategy = GeneralizedWrapperDistributionStrategy(self._historiclog_dir_path)
          job_data_dcs_to_update = info_handler.execute_distribution(job_data_dc, job_data_dcs_in_wrapper, slurm_monitor)
      else:
        info_handler = PlatformInformationHandler(SingleAssociationStrategy(self._historiclog_dir_path))
        job_data_dcs_to_update = info_handler.execute_distribution(job_data_dc, job_data_dcs_in_wrapper, slurm_monitor)
      return self.manager.update_list_job_data_dc_by_each_id(job_data_dcs_to_update)
    except Exception as exp:
      self._log.log(str(exp), traceback.format_exc())

  def get_historic_job_data(self, job_name):
    # type: (str) -> List[Dict[str, Any]]
    result = []
    all_job_data_dcs = self.manager.get_job_data_dcs_by_name(job_name)
    post_job_data_dcs = self.manager.get_job_data_dcs_COMPLETED_by_section("POST")

    run_id_to_POST_job_data_dcs = {} # type: Dict[int, List[JobData]]
    run_id_wrapper_code_to_job_data_dcs = {} # type: Dict[Tuple[int, int], List[JobData]]
    for job_data_dc in post_job_data_dcs:
      run_id_to_POST_job_data_dcs.setdefault(job_data_dc.run_id, []).append(job_data_dc)
      if (job_data_dc.run_id, job_data_dc.rowtype) not in run_id_wrapper_code_to_job_data_dcs:
        run_id_wrapper_code_to_job_data_dcs[(job_data_dc.run_id, job_data_dc.rowtype)] = self.manager.get_job_data_dc_COMPLETED_by_wrapper_run_id(job_data_dc.rowtype, job_data_dc.run_id)

    run_id_to_experiment_run_involved = {} # type: Dict[int, ExperimentRun]
    for job_data_dc in all_job_data_dcs:
      if job_data_dc.run_id not in run_id_to_experiment_run_involved:
        run_id_to_experiment_run_involved[job_data_dc.run_id] = self.manager.get_experiment_run_by_id(job_data_dc.run_id)
      if (job_data_dc.run_id, job_data_dc.rowtype) not in run_id_wrapper_code_to_job_data_dcs:
        run_id_wrapper_code_to_job_data_dcs[(job_data_dc.run_id, job_data_dc.rowtype)] = self.manager.get_job_data_dc_COMPLETED_by_wrapper_run_id(job_data_dc.rowtype, job_data_dc.run_id)

    for job_data_dc in all_job_data_dcs:
      experiment_run = run_id_to_experiment_run_involved.get(job_data_dc.run_id, None)
      jobs_in_package = run_id_wrapper_code_to_job_data_dcs.get((job_data_dc.run_id, job_data_dc.rowtype), [])
      if experiment_run:
        average_post_time = 0.0
        post_job_data_dcs_in_run = run_id_to_POST_job_data_dcs.get(job_data_dc.run_id, [])
        if len(post_job_data_dcs_in_run) > 0:
          for post_job_data_dc in post_job_data_dcs_in_run:
            if post_job_data_dc.rowtype > Models.RowType.NORMAL:
              jobs_in_package_for_post_job = run_id_wrapper_code_to_job_data_dcs.get((post_job_data_dc.run_id, post_job_data_dc.rowtype), [])
              average_post_time += post_job_data_dc.queuing_time_considering_package(jobs_in_package_for_post_job)
            else:
              average_post_time += (post_job_data_dc.queuing_time + post_job_data_dc.running_time)
          average_post_time = average_post_time/len(post_job_data_dcs_in_run)
      result.append({"counter": job_data_dc.counter,
                      "created": job_data_dc.created,
                      "submit": job_data_dc.submit_datetime_str,
                      "start": job_data_dc.start_datetime_str,
                      "finish": job_data_dc.finish_datetime_str,
                      "queue_time": job_data_dc.delta_queueing_time_considering_package(jobs_in_package),
                      "run_time": job_data_dc.delta_running_time,
                      "ncpus": job_data_dc.ncpus,
                      "wallclock": job_data_dc.wallclock,
                      "qos": job_data_dc.qos,
                      "platform": job_data_dc.platform,
                      "job_id": job_data_dc.job_id,
                      "nodes": job_data_dc.nnodes,
                      "energy": job_data_dc.energy,
                      "status": job_data_dc.status,
                      "ASYPD": PUtils.calculate_ASYPD_perjob(experiment_run.chunk_unit, experiment_run.chunk_size, job_data_dc.chunk, job_data_dc.queuing_time_considering_package(jobs_in_package) + job_data_dc.running_time, average_post_time, job_data_dc.status_code) if experiment_run else "NA",
                      "SYPD": PUtils.calculate_SYPD_perjob(experiment_run.chunk_unit, experiment_run.chunk_size, job_data_dc.chunk, job_data_dc.running_time, job_data_dc.status_code) if experiment_run else "NA",
                      "run_id": job_data_dc.run_id,
                      "run_created": experiment_run.created if experiment_run else "NA",
                      "out": job_data_dc.out,
                      "err": job_data_dc.err
                      })
    return result


  def update_job_finish_time_if_zero(self, job_name, finish_ts):
    # type: (str, int) -> JobData
    try:
      job_data_dc = self.manager.get_job_data_dc_unique_latest_by_job_name(job_name)
      if job_data_dc and job_data_dc.finish == 0:
        job_data_dc.finish = finish_ts
        return self.manager.update_job_data_dc_by_id(job_data_dc)
    except Exception as exp:
      self._log.log(str(exp), traceback.format_exc())

  def _verify_slurm_monitor(self, slurm_monitor, job_data_dc):
    try:
      if slurm_monitor.header.status not in ["COMPLETED", "FAILED"]:
        self._log.log("Assertion Error on job {0} with ssh_output {1}".format(job_data_dc.job_name, slurm_monitor.original_input),
                      "Slurm status {0} is not COMPLETED nor FAILED for ID {1}.\n".format(slurm_monitor.header.status, slurm_monitor.header.name))
      if not slurm_monitor.steps_plus_extern_approximate_header_energy():
        self._log.log("Assertion Error on job {0} with ssh_output {1}".format(job_data_dc.job_name, slurm_monitor.original_input),
                      "Steps + extern != total energy for ID {0}. Number of steps {1}.\n".format(slurm_monitor.header.name, slurm_monitor.step_count))
    except Exception as exp:
      self._log.log(str(exp), traceback.format_exc())

  def process_status_changes(self, job_list=None, chunk_unit="NA", chunk_size=0, current_config=""):
    """ Detect status differences between job_list and current job_data rows, and update. Creates a new run if necessary. """
    try:
      current_experiment_run_dc = self.manager.get_experiment_run_dc_with_max_id()
      update_these_changes = self._get_built_list_of_changes(job_list)
      should_create_new_run = self.should_we_create_a_new_run(job_list, len(update_these_changes), current_experiment_run_dc, chunk_unit, chunk_size)
      if len(update_these_changes) > 0 and should_create_new_run == False:
        self.manager.update_many_job_data_change_status(update_these_changes)
      if should_create_new_run:
        return self.create_new_experiment_run(chunk_unit, chunk_size, current_config, job_list)
      return self.update_counts_on_experiment_run_dc(current_experiment_run_dc, job_list)
    except Exception as exp:
      self._log.log(str(exp), traceback.format_exc())

  def _get_built_list_of_changes(self, job_list):
    """ Return: List of (current timestamp, current datetime str, status, rowstatus, id in job_data). One tuple per change. """
    job_data_dcs = self.detect_changes_in_job_list(job_list)
    return [(HUtils.get_current_datetime(), job.status, Models.RowStatus.CHANGED, job._id) for job in job_data_dcs]

  def process_job_list_changes_to_experiment_totals(self, job_list=None):
    """ Updates current experiment_run row with totals calculated from job_list. """
    try:
      current_experiment_run_dc = self.manager.get_experiment_run_dc_with_max_id()
      return self.update_counts_on_experiment_run_dc(current_experiment_run_dc, job_list)
    except Exception as exp:
      self._log.log(str(exp), traceback.format_exc())

  def should_we_create_a_new_run(self, job_list, changes_count, current_experiment_run_dc, new_chunk_unit, new_chunk_size):
    if len(job_list) != current_experiment_run_dc.total:
      return True
    if changes_count > int(self._get_date_member_completed_count(job_list)):
      return True
    return self._chunk_config_has_changed(current_experiment_run_dc, new_chunk_unit, new_chunk_size)

  def _chunk_config_has_changed(self, current_exp_run_dc, new_chunk_unit, new_chunk_size):
    if not current_exp_run_dc:
      return True
    if current_exp_run_dc.chunk_unit != new_chunk_unit or current_exp_run_dc.chunk_size != new_chunk_size:
      return True
    return False

  def update_counts_on_experiment_run_dc(self, experiment_run_dc, job_list=None):
    """ Return updated row as Models.ExperimentRun. """
    status_counts = self.get_status_counts_from_job_list(job_list)
    experiment_run_dc.completed = status_counts[HUtils.SupportedStatus.COMPLETED]
    experiment_run_dc.failed = status_counts[HUtils.SupportedStatus.FAILED]
    experiment_run_dc.queuing = status_counts[HUtils.SupportedStatus.QUEUING]
    experiment_run_dc.submitted = status_counts[HUtils.SupportedStatus.SUBMITTED]
    experiment_run_dc.running = status_counts[HUtils.SupportedStatus.RUNNING]
    experiment_run_dc.suspended = status_counts[HUtils.SupportedStatus.SUSPENDED]
    experiment_run_dc.total = status_counts["TOTAL"]
    return self.manager.update_experiment_run_dc_by_id(experiment_run_dc)

  def finish_current_experiment_run(self):
    if self.manager.is_there_a_last_experiment_run():
      current_experiment_run_dc = self.manager.get_experiment_run_dc_with_max_id()
      current_experiment_run_dc.finish = int(time())
      return self.manager.update_experiment_run_dc_by_id(current_experiment_run_dc)
    return None

  def create_new_experiment_run(self, chunk_unit="NA", chunk_size=0, current_config="", job_list=None):
    """ Also writes the finish timestamp of the previous run.  """
    self.finish_current_experiment_run()
    return self._create_new_experiment_run_dc_with_counts(chunk_unit=chunk_unit, chunk_size=chunk_size, current_config=current_config, job_list=job_list)

  def _create_new_experiment_run_dc_with_counts(self, chunk_unit, chunk_size, current_config="", job_list=None):
    """ Create new experiment_run row and return the new Models.ExperimentRun data class from database. """
    status_counts = self.get_status_counts_from_job_list(job_list)
    experiment_run_dc = ExperimentRun(0,
                        chunk_unit=chunk_unit,
                        chunk_size=chunk_size,
                        metadata=current_config,
                        start=int(time()),
                        completed=status_counts[HUtils.SupportedStatus.COMPLETED],
                        total=status_counts["TOTAL"],
                        failed=status_counts[HUtils.SupportedStatus.FAILED],
                        queuing=status_counts[HUtils.SupportedStatus.QUEUING],
                        running=status_counts[HUtils.SupportedStatus.RUNNING],
                        submitted=status_counts[HUtils.SupportedStatus.SUBMITTED],
                        suspended=status_counts[HUtils.SupportedStatus.SUSPENDED])
    return self.manager.register_experiment_run_dc(experiment_run_dc)

  def detect_changes_in_job_list(self, job_list):
    """ Detect changes in job_list compared to the current contents of job_data table. Returns a list of JobData data classes where the status of each item is the new status."""
    job_name_to_job = {job.name: job for job in job_list}
    current_job_data_dcs = self.manager.get_all_last_job_data_dcs()
    differences = []
    for job_dc in current_job_data_dcs:
      if job_dc.job_name in job_name_to_job and job_dc.status != job_name_to_job[job_dc.job_name].status_str:
        job_dc.status = job_name_to_job[job_dc.job_name].status_str
        differences.append(job_dc)
    return differences

  def _get_defined_rowtype(self, code):
    if code:
        return code
    else:
        return Models.RowType.NORMAL

  def _get_defined_queue_name(self, wrapper_queue, wrapper_code, qos):
    if wrapper_code and wrapper_code > 2 and wrapper_queue is not None:
      return wrapper_queue
    return qos

  def _get_next_counter_by_job_name(self, job_name):
    """ Return the counter attribute from the latest job data row by job_name. """
    job_data_dc = self.manager.get_job_data_dc_unique_latest_by_job_name(job_name)
    max_counter = self.manager.get_job_data_max_counter()
    if job_data_dc:
      return max(max_counter, job_data_dc.counter + 1)
    else:
      return max_counter

  def _get_date_member_completed_count(self, job_list):
    """ Each item in the job_list must have attributes: date, member, status_str. """
    job_list = job_list if job_list else []
    return sum(1 for job in job_list if job.date is not None and job.member is not None and job.status_str == HUtils.SupportedStatus.COMPLETED)

  def get_status_counts_from_job_list(self, job_list):
    """
    Return dict with keys COMPLETED, FAILED, QUEUING, SUBMITTED, RUNNING, SUSPENDED, TOTAL.
    """
    result = {
      HUtils.SupportedStatus.COMPLETED: 0,
      HUtils.SupportedStatus.FAILED: 0,
      HUtils.SupportedStatus.QUEUING: 0,
      HUtils.SupportedStatus.SUBMITTED: 0,
      HUtils.SupportedStatus.RUNNING: 0,
      HUtils.SupportedStatus.SUSPENDED: 0,
      "TOTAL": 0
    }

    if not job_list:
      job_list = []

    for job in job_list:
      if job.status_str in result:
        result[job.status_str] += 1
    result["TOTAL"] = len(job_list)
    return result
