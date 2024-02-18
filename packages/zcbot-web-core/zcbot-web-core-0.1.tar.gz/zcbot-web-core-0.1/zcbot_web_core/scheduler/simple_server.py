import pytz
import traceback
from pymongo import MongoClient
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError, ConflictingIdError
from ..exception.exceptions import BizException
from ..lib import logger, cfg

LOGGER = logger.for_job('scheduler_server')


def init_scheduler():
    global scheduler

    try:
        enable_scheduler = cfg.get_bool('ENABLE_SCHEDULER')
        if not enable_scheduler:
            LOGGER.info('定时任务框架未启用')
            return
        tzinfo = pytz.timezone('Asia/Shanghai')
        default_mongo_jobstore = MongoDBJobStore(
            client=MongoClient(cfg.get('MONGO_URL'), tz_aware=True, tzinfo=tzinfo),
            database=cfg.get('MONGO_DB'),
            collection=cfg.get('SCHEDULER_JOB_STORE_NAME', 'sys_jobs')
        )
        job_stores = {
            'default': default_mongo_jobstore
        }
        executors = {
            'default': {'type': 'threadpool', 'max_workers': 1000},
        }
        scheduler = AsyncIOScheduler()
        scheduler.configure(
            jobstores=job_stores,
            executors=executors,
        )
        scheduler.start()
        LOGGER.info('定时任务框架初始化成功')

    except Exception as e:
        LOGGER.error(f'定时任务框架初始化异常： {traceback.format_exc()}')


def _env_check():
    enable_scheduler = cfg.get_bool('ENABLE_SCHEDULER')
    if not enable_scheduler:
        return False
    if not scheduler:
        raise BizException('定时任务功能未开启或框架初始化失败')
    return True


def get_scheduler():
    if _env_check():
        return scheduler


def add_fix_date_job(job_id, func, replace_existing=True, **options):
    """
    特定时间定时调度（作业只会执行一次）
    https://www.cnblogs.com/luxiaojun/p/6567132.html
    :param job_id: 定时任务编号
    :param func: 执行的函数
    :param options: 可选参数
        run_date (datetime|str) – the date/time to run the job at  -（任务开始的时间）
        timezone (datetime.tzinfo|str) – time zone for run_date if it doesn’t have one already
    :return:
    """
    try:
        if _env_check():
            LOGGER.info(f'add fix date job: job_id={job_id}, func={func}')
            scheduler.add_job(func, 'date', id=job_id, replace_existing=replace_existing, **options)
    except ConflictingIdError as err:
        raise BizException('任务已存在')


def add_interval_job(job_id, func, replace_existing=True, **options):
    """
    间隔调度任务（每隔多久执行）
    https://www.cnblogs.com/luxiaojun/p/6567132.html
    :param job_id: 定时任务编号
    :param func: 执行的函数
    :param options: 可选参数
        weeks (int) – number of weeks to wait
        days (int) – number of days to wait
        hours (int) – number of hours to wait
        minutes (int) – number of minutes to wait
        seconds (int) – number of seconds to wait
        start_date (datetime|str) – starting point for the interval calculation
        end_date (datetime|str) – latest possible date/time to trigger on
        timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations
    :return:
    """
    try:
        if _env_check():
            LOGGER.info(f'add interval job: job_id={job_id}, func={func}')
            scheduler.add_job(func, 'interval', id=job_id, replace_existing=replace_existing, **options)
    except ConflictingIdError as err:
        raise BizException('任务已存在')


def add_cron_job(job_id, func, replace_existing=True, **options):
    """
    cron定时调度（某一定时时刻执行）
    https://www.cnblogs.com/luxiaojun/p/6567132.html
    :param job_id: 定时任务编号
    :param func: 执行的函数
    :param options: 任务时间配置可选参数
        year (int|str) – 4-digit year -（表示四位数的年份，如2008年）
        month (int|str) – month (1-12) -（表示取值范围为1-12月）
        day (int|str) – day of the (1-31) -（表示取值范围为1-31日）
        week (int|str) – ISO week (1-53) -（格里历2006年12月31日可以写成2006年-W52-7（扩展形式）或2006W527（紧凑形式））
        day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun) - （表示一周中的第几天，既可以用0-6表示也可以用其英语缩写表示）
        hour (int|str) – hour (0-23) - （表示取值范围为0-23时）
        minute (int|str) – minute (0-59) - （表示取值范围为0-59分）
        second (int|str) – second (0-59) - （表示取值范围为0-59秒）
        start_date (datetime|str) – earliest possible date/time to trigger on (inclusive) - （表示开始时间）
        end_date (datetime|str) – latest possible date/time to trigger on (inclusive) - （表示结束时间）
        timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations (defaults to scheduler timezone) -（表示时区取值）
    :return:
    """
    try:
        if _env_check():
            LOGGER.info(f'add cron job: job_id={job_id}, func={func}')
            scheduler.add_job(func, 'cron', id=job_id, replace_existing=replace_existing, **options)
    except ConflictingIdError as err:
        raise BizException('任务已存在')


def remove_job(job_id, ignore_error=True):
    try:
        if _env_check():
            LOGGER.info(f'remove job: job_id={job_id}, ignore_error={ignore_error}')
            scheduler.remove_job(job_id=job_id)
    except JobLookupError as err:
        if not ignore_error:
            raise BizException('任务不存在或已删除')
        else:
            LOGGER.error(f'任务不存在或已删除: job_id={job_id}')
