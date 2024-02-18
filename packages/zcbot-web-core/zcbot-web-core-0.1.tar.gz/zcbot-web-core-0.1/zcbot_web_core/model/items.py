from pydantic import BaseModel, Field
from ..model.enums import UserStatus, UserGender
from ..lib import time as time_lib


class BaseData(BaseModel):
    """
    通用基础数据模型
    """
    # mongodb主键
    _id: str = None
    # 插入时间
    genTime: int = Field(
        default_factory=time_lib.current_timestamp10
    )


class AuthUser(BaseData):
    """
    task item model
    """
    # 用户编号
    id: str
    # 租户编码
    tenantCode: str = None
    # 用户名
    userName: str = None
    # 用户姓名
    realName: str = None
    # 性别
    gender: int = UserGender.MALE
    # 电话
    mobile: str = None
    # 邮箱
    email: str = None
    # 是否超级管理员
    superAdmin: str = None
    # 是否超级租户
    superTenant: int = 1
    # 启用停用
    isEnabled: bool = True
    # 批次状态
    status: str = UserStatus.NORMAL

    def to_log(self):
        return f'{self.realName}({self.id})'

    def is_super_admin(self):
        return '1' == self.superAdmin
