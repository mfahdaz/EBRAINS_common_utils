# ------------------------------------------------------------------------------
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements; and to You under the Apache License,
# Version 2.0. "
#
# Forschungszentrum Jülich
# Institute: Institute for Advanced Simulation (IAS)
# Section: Jülich Supercomputing Centre (JSC)
# Division: High Performance Computing in Neuroscience
# Laboratory: Simulation Laboratory Neuroscience
# Team: Multi-scale Simulation and Design
# ------------------------------------------------------------------------------
import os
from cpu_usage import CPUUsage
from memory_usage import MemoryUsage
from resource_usage_summary import ResourceUsageSummary


class Process:
    '''
    Represents the meta-data for the process executing the application.
    This is particulalry useful for later Object Relational Mapping (ORM)
    with Knowledge Grapgh (KG).
    '''
    def __init__(self, log_settings, configurations_manager,
                 pid=None, path_to_read_stats=" "
                 ):
        self._log_settings = log_settings
        self._configurations_manager = configurations_manager
        self.__logger = self._configurations_manager.load_log_configurations(
                                        name=__name__,
                                        log_configurations=self._log_settings,
                                        directory='logs',
                                        directory_path='AC results')
        self.__logger.debug("logger is configured.")
        self.__process_id = pid
        if not path_to_read_stats:
            self._path_to_read_stats = path_to_read_stats
        else:
            self._path_to_read_stats = os.path.join(
                '/proc/', str(self.__process_id), 'stat')
        self.__process_name, self.__process_starting_time =\
            self.__get_process_meta_information(
                self._path_to_read_stats)
        self.__process_execution_time = 0
        self.__cpu_usage = CPUUsage(
                        process_id=pid,
                        log_settings=self._log_settings,
                        configurations_manager=self._configurations_manager)
        self.__memory_usage = MemoryUsage(
                        process_id=pid,
                        log_settings=self._log_settings,
                        configurations_manager=self._configurations_manager)
        self.__resource_usage_summary = ResourceUsageSummary()

    @property
    def process_name(self):
        return self.__process_name

    @property
    def process_starting_time(self):
        return self.__process_starting_time

    @property
    def process_execution_time(self):
        return self.__process_execution_time

    @process_execution_time.setter
    # set by CPU usage monitor after completing execution
    def process_execution_time(self, execution_time):
        self.__process_execution_time = execution_time

    @property
    def cpu_usage_stats(self):
        return self.__resource_usage_summary.cpu_usage_stats

    @cpu_usage_stats.setter
    def cpu_usage_stats(self, cpu_usage):
        self.__resource_usage_summary.cpu_usage_stats.append(cpu_usage)

    @property
    def memory_usage_stats(self):
        return self.__resource_usage_summary.memory_usage_stats

    @memory_usage_stats.setter
    def memory_usage_stats(self, memory_usage):
        self.__resource_usage_summary.memory_usage_stats.append(memory_usage)

    def get_cpu_stats(self):
        current_cpu_usage_stats, process_running_time = \
            self.__cpu_usage.get_usage_stats()
        self.__process_execution_time = process_running_time
        return current_cpu_usage_stats, process_running_time

    def get_memory_stats(self):
        return self.__memory_usage.get_usage_stats()

    def __get_process_meta_information(self, proc_stat_file):
        return self.__parse(self.__read(proc_stat_file))

    def __read(self, proc_stat_file):
        with open(proc_stat_file) as stat_file:
            return next(stat_file)

    def __parse(self, stat_line):
        self.__logger.debug(f'stat_line: {stat_line}')
        proc_pid_stats = stat_line.split(' ')
        process_name = proc_pid_stats[1].strip('()')  # remove sorrounding parentehses
        process_starting_time = int(proc_pid_stats[21])
        self.__logger.debug(f"process_name:{process_name}, "
                            f"fprocess start time: {process_starting_time}")
        return (process_name, process_starting_time)
