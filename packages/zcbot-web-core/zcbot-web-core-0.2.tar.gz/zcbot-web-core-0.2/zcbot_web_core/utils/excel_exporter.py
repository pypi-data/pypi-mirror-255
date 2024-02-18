# encoding:utf-8
import os.path
import re
import uuid
import pandas as pd
from math import isnan
from openpyxl import Workbook
from pandas import Index
from starlette.responses import FileResponse
from ..exception.exceptions import BizException
from ..lib import cfg, logger
from ..lib import time as time_lib

LOGGER = logger.get('导出')


def export_excel(data_list, schema_list, file_id=None):
    if not file_id:
        file_id = str(uuid.uuid4())
    if not data_list:
        LOGGER.info(f'导出失败: 数据为空 file_id={file_id}')
        raise BizException('无结果数据导出')

    # 结构组装
    columns = list()
    headers = list()
    configs = list()
    for meta in schema_list:
        columns.append(meta.get('col'))
        headers.append(meta.get('title'))
        if 'type' in meta:
            configs.append(meta)

    if not len(columns) or not len(headers):
        LOGGER.info(f'导出失败: 表格列配置异常 file_id={file_id}')
        raise BizException('表格列配置异常')

    # 基础目录
    base_path = f'{cfg.get("DOWNLOAD_FILE_DIR", "/data/work/files/export")}'
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    # 文件路径
    file = f'{base_path}/{file_id}.xlsx'
    # 文件写入本地(两种写入方式)
    _write_with_pandas(file, data_list, columns, headers, configs)
    # _write_with_openpyxl(file, data_list, columns, headers)
    LOGGER.info(f'导出成功: file_id={file_id}, rows={len(data_list)}, file={file}')

    # 构建导出响应
    headers = {'content-type': 'application/vnd.ms-excel', 'content-disposition': f'attachment;filename={file_id}.xlsx'}
    return FileResponse(file, media_type='xls/xlsx', headers=headers)


# 通过pandas写excel
def _write_with_pandas(file, data_list, columns, headers, configs):
    # 本地写入Excel
    write = pd.ExcelWriter(file, engine='xlsxwriter', options={'strings_to_urls': False})
    df = pd.DataFrame(data_list)

    # 验证列与数据字段是否匹配，有无缺少
    if not len(Index(columns) & df.columns) or len(Index(columns) & df.columns) != len(columns):
        # 数据中不存在的列（常见于某字段在数据集中不存在）
        miss_columns = list(set(columns) - set((Index(columns) & df.columns).tolist()))
        if miss_columns:
            for field in miss_columns:
                # 补充字段，设置默认值为空字符串
                df.insert(loc=0, column=field, value='')
        df = df.reindex(columns=columns)

    if configs:
        _add_config(df, configs)

    df.to_excel(write, sheet_name='数据', columns=columns, header=headers, index=False)
    write.save()


# 特定列数据转换
def _add_config(df, configs):
    for row in configs:
        col = row.get('col')
        type = row.get('type')
        config = row.get('excel', {})
        if type == 'timestamp':
            _process_timestamp_column(df, col, config)
        elif type == 'mapper':
            _process_mapper_column(df, col, config)


# 处理时间戳格式
def _process_timestamp_column(df, col, config={}):
    format_str = config.get('format', '%Y-%m-%d %H:%M:%S')
    df[col] = df[col].apply(lambda t: time_lib.format_timestamp10(t, fmt=format_str) if t and not isnan(t) else '')


# 处理boolean格式
def _process_mapper_column(df, col, config={}):
    bool_map = config.get('mapper', {True: '是', False: '否'})
    df[col] = df[col].apply(lambda x: bool_map.get(x) or '')


# 通过openpyxl写excel
def _write_with_openpyxl(file, data_list, columns, headers):
    wb = Workbook()
    ws = wb.active
    # 表头
    for col in range(len(headers)):
        c = col + 1
        ws.cell(row=1, column=c).value = headers[col]
    # 插入数据
    row_idx = 1
    for item in data_list:
        row = []
        for col in range(len(headers)):
            cell_val = _remove_special(item.get(columns[col], ''))
            row.append(cell_val)
        ws.append(row)
        row_idx += 1
    wb.save(filename=file)


def _remove_special(value):
    sub_str = re.sub(u'([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])', '', str(value))
    return sub_str
