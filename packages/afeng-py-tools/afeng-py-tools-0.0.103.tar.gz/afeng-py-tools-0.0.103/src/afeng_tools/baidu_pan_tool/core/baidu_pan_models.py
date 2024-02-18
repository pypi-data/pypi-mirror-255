"""
- pip install pydantic -i https://pypi.tuna.tsinghua.edu.cn/simple/
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class TokenInfo(BaseModel):
    """Token信息"""
    # 获取到的Access Token
    access_token: str
    # Access Token的有效期，单位为秒。
    expires_in: int
    # 用于刷新 Access Token, 有效期为10年。
    refresh_token: str
    # Access Token 最终的访问权限，即用户的实际授权列表。
    scope: str
    # token获取的时间，用于判断token是否过期
    token_time: datetime


class GrantTokenInfo(BaseModel):
    """简化模式 Token信息"""
    # 获取到的Access Token
    access_token: str
    # Access Token的有效期，单位为秒。
    expires_in: int
    session_secret: str
    session_key: str
    # Access Token 最终的访问权限，即用户的实际授权列表。
    scope: str
    # token获取的时间，用于判断token是否过期
    token_time: datetime


class DeviceCodeInfo(BaseModel):
    """设备码信息"""
    # 设备码，可用于生成单次凭证 Access Token。
    device_code: str
    # 用户码。如果选择让用户输入 user code 方式，来引导用户授权，设备需要展示 user code 给用户。
    user_code: str
    # 用户输入 user code 进行授权的 url。
    verification_url: str
    # 二维码url，用户用手机等智能终端扫描该二维码完成授权。
    qrcode_url: str
    # device_code 的过期时间，单位：秒。到期后 device_code 不能换 Access Token。
    expires_in: int
    # device_code 换 Access Token 轮询间隔时间，单位：秒。 轮询次数限制小于 expire_in/interval。
    interval: int


class PanVolumeInfo(BaseModel):
    """百度网盘容量信息"""
    # 总空间大小，单位B
    total: int
    # 7天内是否有容量到期
    expire: Optional[bool] = None
    # 已使用大小，单位B
    used: int
    # 免费容量，单位B
    free: int


class UserInfo(BaseModel):
    """用户的基本信息"""
    # 百度账号
    baidu_name: str
    # 网盘账号
    net_disk_name: str
    # 头像地址
    avatar_url: str
    # 会员类型，0普通用户、1普通会员、2超级会员
    vip_type: int
    # 用户ID
    uk: int


class FileThumb(BaseModel):
    """文件图片缩略图信息"""
    # 140x90大小的图片路径
    url1: Optional[str] = None
    # 360x270大小的图片路径
    url2: Optional[str] = None
    # 850x580大小的图片路径
    url3: Optional[str] = None


class FileInfo(BaseModel):
    """文件信息"""
    # 文件在云端的唯一标识ID
    fs_id: int
    # 文件的绝对路径
    path: str
    # 文件名称
    server_filename: str
    # 文件大小，单位B
    size: int
    # 文件在服务器创建时间
    server_ctime: Optional[int] = None
    # 文件在服务器修改时间
    server_mtime: Optional[int] = None
    # 文件在客户端修改时间
    local_mtime: Optional[int] = None
    # 文件在客户端创建时间
    local_ctime: Optional[int] = None
    # 是否为目录，0 文件、1 目录
    isdir: Optional[int] = None
    # 文件类型，1 视频、2 音频、3 图片、4 文档、5 应用、6 其他、7 种子
    category: Optional[int] = None
    # 如：pdf
    real_category: Optional[str] = None
    # 云端哈希（非文件真实MD5），只有是文件类型时，该字段才存在
    md5: Optional[str] = None
    # 该目录是否存在子目录，只有请求参数web=1且该条目为目录时，该字段才存在， 0为存在， 1为不存在
    dir_empty: Optional[int] = None
    # 只有请求参数web=1且该条目分类为图片时，该字段才存在，包含三个尺寸的缩略图URL
    thumbs: Optional[FileThumb] = None
    server_atime: Optional[int] = None
    tkbind_id: Optional[int] = None
    unlist: Optional[int] = None
    wpfile: Optional[int] = None
    share: Optional[int] = None
    pl: Optional[int] = None
    docpreview: Optional[str] = None
    owner_id: Optional[int] = None
    owner_type: Optional[int] = None
    lodocpreview: Optional[str] = None
    extent_tinyint7: Optional[int] = None
    from_type: Optional[int] = None
    oper_id: Optional[int] = None


class DocFileInfo(BaseModel):
    """文档文件信息"""
    # 文件在云端的唯一标识ID
    fs_id: int
    # 文件名称
    server_filename: str
    # 文件的绝对路径
    path: str
    # 文件类型，1 视频、2 音频、3 图片、4 文档、5 应用、6 其他、7 种子
    category: int
    # 是否为目录，0 文件、1 目录
    isdir: int
    # 文件大小，单位B
    size: int
    # 图片缩略图，包含三个尺寸
    thumbs: Optional[FileThumb] = None
    # 文档预览地址 （已下线）
    lodocpreview: Optional[str] = None
    # 用户获取文档预览地址。如果接口只下发了docpreview，那么文档预览地址=docpreview + "type=pdf&from=lo"。（已下线）
    docpreview: Optional[str] = None
    # 文件在客户端创建时间
    local_ctime: Optional[int] = None
    # 文件在客户端修改时间
    local_mtime: Optional[int] = None
    # 文件在服务端创建时间
    server_ctime: Optional[int] = None
    # 文件在服务端修改时间
    server_mtime: Optional[int] = None
    from_type: Optional[int] = None
    # 云端哈希（非文件真实MD5）
    md5: Optional[str] = None
    object_key: Optional[str] = None
    share: Optional[int] = None
    owner_id: Optional[int] = None
    wpfile: Optional[int] = None


class FileMetaThumb(BaseModel):
    """文件元数据图片缩略图信息"""
    # 60x60大小的图片路径
    icon: Optional[str] = None
    # 140x90大小的图片路径
    url1: Optional[str] = None
    # 360x270大小的图片路径
    url2: Optional[str] = None
    # 850x580大小的图片路径
    url3: Optional[str] = None
    # 原质量
    url4: Optional[str] = None


class ImageInfo(BaseModel):
    """图片信息"""
    # 文件在云端的唯一标识
    fs_id: int
    # 文件的绝对路径
    path: str
    # 文件名称
    server_filename: str
    # 文件类型，1 视频、2 音频、3 图片、4 文档、5 应用、6 其他、7 种子
    category: int
    # 是否是目录，0为否，1为是
    isdir: int
    # 文件在服务端创建时间
    server_ctime: Optional[int] = None
    # 文件在服务端修改时间
    server_mtime: Optional[int] = None
    # 文件在客户端修改时间
    local_mtime: Optional[int] = None
    # 文件在客户端创建时间
    local_ctime: Optional[int] = None
    # 云端哈希（非文件真实MD5）
    md5: str
    # 文件大小，单位B
    size: int
    # 图片缩略图，包含四个尺寸
    thumbs: Optional[FileMetaThumb] = None
    from_type: Optional[int] = None
    wpfile: Optional[int] = None
    owner_id: Optional[int] = None
    object_key: Optional[str] = None
    share: Optional[int] = None


class VideoInfo(BaseModel):
    """视频信息"""
    # 文件在云端的唯一标识
    fs_id: int
    # 文件的绝对路径
    path: str
    # 文件名称
    server_filename: str
    # 文件类型，1 视频、2 音频、3 图片、4 文档、5 应用、6 其他、7 种子
    category: int
    # 是否是目录，0为否，1为是
    isdir: int
    # 文件在服务端创建时间
    server_ctime: Optional[int] = None
    # 文件在服务端修改时间
    server_mtime: Optional[int] = None
    # 文件在客户端修改时间
    local_mtime: Optional[int] = None
    # 文件在客户端创建时间
    local_ctime: Optional[int] = None
    # 云端哈希（非文件真实MD5）
    md5: str
    # 文件大小，单位B
    size: int
    # 图片缩略图，包含四个尺寸
    thumbs: Optional[FileMetaThumb] = None
    object_key: Optional[str] = None
    share: Optional[int] = None


class BtInfo(BaseModel):
    """bt信息"""
    # 文件在云端的唯一标识
    fs_id: int
    # 文件的绝对路径
    path: str
    # 文件名称
    server_filename: str
    # 文件类型，1 视频、2 音频、3 图片、4 文档、5 应用、6 其他、7 种子
    category: int
    # 是否是目录，0为否，1为是
    isdir: int
    # 文件在服务端创建时间
    server_ctime: Optional[int] = None
    # 文件在服务端修改时间
    server_mtime: Optional[int] = None
    # 文件在客户端修改时间
    local_mtime: Optional[int] = None
    # 文件在客户端创建时间
    local_ctime: Optional[int] = None
    # 云端哈希（非文件真实MD5）
    md5: str
    # 文件大小，单位B
    size: int
    object_key: Optional[str] = None
    share: Optional[int] = None


class MultimediaFileInfo(BaseModel):
    """MultimediafileApi的listall接口返回文件新"""
    errno: Optional[int] = None
    # 是否还有下一页，0表示无，1表示有
    has_more: bool
    # 当还有下一页时，为下一次查询的起点
    cursor: Optional[int] = None
    # 文件列表
    file_list: Optional[List[FileInfo]] = None


class FileMetaInfo(BaseModel):
    """文件元信息"""
    # 文件在云端的唯一标识ID
    fs_id: int
    # 文件类型，含义如下：1 视频， 2 音乐，3 图片，4 文档，5 应用，6 其他，7 种子
    category: Optional[int] = None
    # 文件的绝对路径
    path: Optional[str] = None
    # 文件下载地址
    dlink: Optional[str] = None
    # 文件名称
    filename: Optional[str] = None
    # 是否为目录，0 文件、1 目录
    isdir: Optional[int] = None
    # 文件的服务器创建Unix时间戳，单位秒
    server_ctime: Optional[int] = None
    # 文件的服务器修改Unix时间戳，单位秒
    server_mtime: Optional[int] = None
    # 文件在客户端修改时间
    local_mtime: Optional[int] = None
    # 文件在客户端创建时间
    local_ctime: Optional[int] = None
    # 文件大小，单位B
    size: Optional[int] = None
    # 云端哈希（非文件真实MD5）
    md5: Optional[str] = None
    # 缩略图URL
    thumbs: Optional[FileMetaThumb] = None
    # 图片高度
    height: Optional[int] = None
    # 图片宽度
    width: Optional[int] = None
    # 图片拍摄时间
    date_taken: Optional[int] = None
    # 图片旋转方向信息
    orientation: Optional[str] = None
    oper_id: Optional[int] = None


class SearchFileInfo(BaseModel):
    """搜索文件信息"""
    # 文件在云端的唯一标识ID
    fs_id: int
    # 文件类型，含义如下：1 视频， 2 音乐，3 图片，4 文档，5 应用，6 其他，7 种子
    category: int
    # 文件的绝对路径
    path: Optional[str] = None
    # 文件名称
    server_filename: str
    # 文件大小，单位B
    size: int
    # 文件在服务端创建时间
    server_ctime: Optional[int] = None
    # 文件在服务端修改时间
    server_mtime: Optional[int] = None
    # 文件在客户端修改时间
    local_mtime: Optional[int] = None
    # 文件在客户端创建时间
    local_ctime: Optional[int] = None
    # 是否为目录，0 文件、1 目录
    isdir: int
    # 缩略图URL
    thumbs: Optional[FileMetaThumb] = None
    # 云端哈希（非文件真实MD5）
    md5: Optional[str] = None
    share: Optional[int] = None
    oper_id: Optional[int] = None
    extent_tinyint1: Optional[int] = None


class SearchResultInfo(BaseModel):
    """搜索结果信息"""
    # 是否有更多
    has_more: bool
    # 内容列表
    content_list: Optional[list] = None
    # 文件列表
    file_list: Optional[List[SearchFileInfo]] = None


class CategoryCountInfo(BaseModel):
    """文件分类数量信息"""
    total: Optional[int] = None
    size: Optional[int] = None
    # 文件数量
    count: int


class CategoryListItem(BaseModel):
    """CategoryList的子项"""
    # 文件在云端的唯一标识ID
    fs_id: int
    # 文件类型，含义如下：1 视频， 2 音乐，3 图片，4 文档，5 应用，6 其他，7 种子
    category: int
    # 文件的绝对路径
    path: Optional[str] = None
    # 文件名称
    server_filename: str
    # 文件大小，单位B
    size: int
    # 文件在服务端创建时间
    server_ctime: Optional[int] = None
    # 文件在服务端修改时间
    server_mtime: Optional[int] = None
    # 文件在客户端修改时间
    local_mtime: Optional[int] = None
    # 文件在客户端创建时间
    local_ctime: Optional[int] = None
    # 是否为目录，0 文件、1 目录
    isdir: int
    # 缩略图URL
    thumbs: Optional[FileMetaThumb] = None
    # 云端哈希（非文件真实MD5）
    md5: Optional[str] = None


class CategoryListResult(BaseModel):
    """CategoryList结果"""
    # 是否还有下一页，0表示无，1表示有
    has_more: bool
    # 当还有下一页时，为下一次查询的起点
    cursor: Optional[int] = None
    # 文件列表
    file_list: Optional[List[CategoryListItem]] = None


class CreatePathResult(BaseModel):
    """获取文件信息返回结果"""
    # 文件在云端的唯一标识ID
    fs_id: int
    # 文件名
    name: str
    # 上传后使用的文件绝对路径
    path: str
    # 文件类型，含义如下：1 视频， 2 音乐，3 图片，4 文档，5 应用，6 其他，7 种子
    category: int
    # 是否为目录，0 文件、1 目录
    isdir: int
    # 文件创建时间
    ctime: int
    # 文件修改时间
    mtime: int


class CopyFileInfo(BaseModel):
    """拷贝文件信息"""
    # 源目录
    source_file: str
    # 目标目录
    dest_path: str
    # 新文件名
    new_filename: str
    # 文件对应的ondup参数, fail(默认，直接返回失败)、newcopy(重命名文件)、overwrite、skip； 高于全局ondup
    ondup: Optional[str] = None


class FileSyncManageResultItem(BaseModel):
    """同步管理结果"""
    # 文件路径
    path: str
    # 当为0时成功
    errno: int


class FileAsyncManageResult(BaseModel):
    """文件异步管理结果"""
    # 当异步执行时，还有taskid
    taskid: Optional[int] = None


class MoveFileInfo(BaseModel):
    """移动文件信息"""
    # 源目录
    source_file: str
    # 目标目录
    dest_path: str
    # 新文件名
    new_filename: str
    # 文件对应的ondup参数, fail(默认，直接返回失败)、newcopy(重命名文件)、overwrite、skip； 高于全局ondup
    ondup: Optional[str] = None


class RenameFileInfo(BaseModel):
    """重命名文件信息"""
    # 源目录
    source_file: str
    # 新文件名
    new_filename: str


class PreCreateResult(BaseModel):
    """预上传结果"""
    # 错误码
    errno: int
    request_id: int
    # 文件的绝对路径
    path: Optional[str] = None
    # 上传唯一ID标识此上传任务
    uploadid: Optional[str] = None
    # 返回类型，系统内部状态字段
    return_type: Optional[int] = None
    # 需要上传的分片序号列表，索引从0开始
    block_list: Optional[list[int]] = None


class SplitUploadResult(BaseModel):
    """分片上传结果"""
    # 错误码
    errno: Optional[int] = None
    request_id: Optional[int] = None
    # 文件切片云端md5
    md5: Optional[str] = None


class ImageExifInfo(BaseModel):
    """图片额外信息"""
    # 如：6
    orientation: Optional[int] = None
    # 如：4032
    width: Optional[int] = None
    # 如：3024
    height: Optional[int] = None
    # 如：0
    recovery: Optional[int] = None
    # 如：2018:09:06 15:58:58
    date_time_original: Optional[datetime]
    # 如：2018:09:06 15:58:58
    date_time_digitized: Optional[datetime]
    # 如：2018:09:06 15:58:58
    date_time: Optional[datetime]
    # 如：iPhone 6s
    model: Optional[str] = None


class UploadCreateResult(BaseModel):
    """上传的第三步：创建文件结果"""
    # 错误码
    errno: Optional[int] = None
    show_msg: Optional[str] = None
    request_id: Optional[int] = None
    # 文件在云端的唯一标识ID
    fs_id: Optional[int] = None
    # 文件的MD5，只有提交文件时才返回，提交目录时没有该值
    md5: Optional[str] = None
    # 文件名
    server_filename: Optional[str] = None
    # 分类类型, 1 视频 2 音频 3 图片 4 文档 5 应用 6 其他 7 种子
    category: Optional[int] = None
    # 上传后使用的文件绝对路径
    path: Optional[str] = None
    name: Optional[str] = None
    # 文件大小，单位B
    size: Optional[int] = None
    # 文件创建时间
    ctime: Optional[int] = None
    # 文件修改时间
    mtime: Optional[int] = None
    # 是否目录，0 文件、1 目录
    isdir: Optional[int] = None
    from_type: Optional[int] = None


class SplitUploadTempInfo(BaseModel):
    """分片上传临时文件"""
    # 文件大小
    file_size: Optional[int] = None
    # 是否是文件夹
    is_dir: Optional[bool] = None
    # 分片信息
    part_info_list: Optional[list[tuple[int, int]]] = None
    # 预上传id
    upload_id: Optional[str] = None
    # 文件各分片MD5数组
    block_list: list[str]
    # 已经上传的分片信息
    uploaded_part_list: Optional[list[tuple[int, int]]] = []


class AudioCategoryInfo(BaseModel):
    # 播单名
    name: Optional[str] = None
    # 播单ID
    mb_id: Optional[int] = None
    # 播单内文件数目
    file_count: Optional[int] = None
    # 播单创建时间
    ctime: Optional[int] = None
    # 播单修改时间
    mtime: Optional[int] = None
    # 播单文件类型，0 音频
    btype: Optional[int] = None
    # 播单子类型，0普通 1音乐 2课程
    bstype: Optional[int] = None


class ListAudioCategoryResult(BaseModel):
    errno: Optional[int] = None
    request_id: Optional[int] = None
    show_msg: Optional[str] = None
    newno: Optional[str] = None
    # 是否还有下一页，0表示无，1表示有
    has_more: Optional[int] = None
    # 播单列表
    data_list: Optional[list[AudioCategoryInfo]] = None


class AudioInfo(BaseModel):
    # 文件在服务端的唯一标识id
    fs_id: int
    # 文件路径
    path: str
    # 文件修改时间
    broadcast_file_mtime: int
    # 以下是文件详细信息
    # 文件名称
    server_filename: Optional[str] = None
    # 是否是文件夹。1是，为文件夹；0否，为文件
    isdir: Optional[str] = None
    # 文件大小
    size: Optional[str] = None
    # 文件类型
    category: Optional[str] = None
    # 服务端哈希（非文件真实MD5）
    md5: Optional[str] = None
    # 文件私密等级
    privacy: Optional[str] = None
    server_atime: Optional[str] = None
    # 文件在服务端创建时间
    server_ctime: Optional[str] = None
    # 文件在服务端修改时间
    server_mtime: Optional[str] = None
    # 文件在客户端创建时间
    local_ctime: Optional[str] = None
    # 文件在客户端修改时间
    local_mtime: Optional[str] = None
    tkbind_id: Optional[str] = None
    owner_type: Optional[str] = None
    share: Optional[str] = None
    real_category: Optional[str] = None
    videotag: Optional[str] = None
    wpfile: Optional[str] = None
    oper_id: Optional[str] = None
    owner_id: Optional[str] = None


class ListAudioResult(BaseModel):
    errno: Optional[int] = None
    request_id: Optional[int] = None
    show_msg: Optional[str] = None
    newno: Optional[str] = None
    # 是否还有下一页，0表示无，1表示有
    has_more: Optional[int] = None
    # 文件列表
    data_list: Optional[list[AudioInfo]] = None


class AdTokenResult(BaseModel):
    # 错误码
    errno: Optional[int] = None
    # 广告播放时长
    adTime: Optional[int] = None
    # 加载广告后返回的合法token，有效期10小时
    adToken: Optional[str] = None
    # 	第二次请求应该在第一次响应后，过ltime秒后再发起
    ltime: Optional[int] = None


class CreateShareInfo(BaseModel):
    # 分享id
    share_id: Optional[str] = None
    # 分享短链
    short_url: Optional[str] = None
    # 分享访问url
    link: Optional[str] = None
    # 分享有效期
    period: Optional[str] = None
    # 分享提取码
    pwd: Optional[str] = None
    # 分享备注
    remark: Optional[str] = None


class CreateShareResult(BaseModel):
    # 错误码
    errno: Optional[int] = None
    # 请求标识
    request_id: Optional[int] = None
    # 错误信息
    show_msg: Optional[str] = None
    # 响应数据
    data: Optional[CreateShareInfo] = None


class VerifySharePwdInfo(BaseModel):
    # 加密的提取码，用于后续操作携带
    spwd: Optional[str] = None


class VerifySharePwdResult(BaseModel):
    # 错误码
    errno: Optional[int] = None
    # 请求标识
    request_id: Optional[int] = None
    # 错误信息
    show_msg: Optional[str] = None
    # 响应数据
    data: Optional[VerifySharePwdInfo] = None


class ShareLinkInfo(BaseModel):
    """分享外链信息"""
    # 分享短链
    short_url: Optional[str] = None
    # 分享id
    share_id: Optional[int] = None
    # 分享者uk
    share_uk: Optional[int] = None
    # 分享备注信息
    remark: Optional[str] = None
    # 分享行为限制
    vdt_limit: Optional[str] = None
    # 分享有效期
    period: Optional[int] = None
    # 分享创建时间
    ctime: Optional[int] = None
    # 分享者归属app_id，提取码验证通过后返回
    appid: Optional[int] = None
    # 分享链接，提取码验证通过后返回
    link: Optional[str] = None
    # 分享状态，提取码验证通过后返回
    status: Optional[int] = None
    # 分享记录最后修改时间，提取码验证通过后返回
    mtime: Optional[int] = None
    # 分享提取码，提取码验证通过后返回
    pwd: Optional[str] = None
    extra: Optional[dict] = None
    file_cnt: Optional[int] = None
    pwd_pass: Optional[bool] = None


class ShareUserInfo(BaseModel):
    """分享者信息"""
    # 分享者用户名，脱敏后
    user_name: Optional[str] = None
    # 分享者头像信息
    user_avatar: Optional[str] = None


class QueryShareInfoData(BaseModel):
    # 分享外链信息
    link_info: Optional[ShareLinkInfo] = None
    # 分享者信息
    share_user_info: Optional[ShareUserInfo] = None


class QueryShareInfoResult(BaseModel):
    # 错误码
    errno: Optional[int] = None
    # 请求标识
    request_id: Optional[int] = None
    # 错误信息
    show_msg: Optional[str] = None
    # 响应数据
    data: Optional[QueryShareInfoData] = None


class QueryShareDataListItem(BaseModel):
    # 文件分类
    category: Optional[int] = None
    # 文件id
    fsid: Optional[int] = None
    # 0 or 1, 文件是否是目录
    isdir: Optional[int] = None
    # 本地创建时间
    local_ctime: Optional[int] = None
    # 本地修改时间
    local_mtime: Optional[int] = None
    # 文件md5
    md5: Optional[str] = None
    # 文件路径
    path: Optional[str] = None
    # 服务端创建时间
    server_ctime: Optional[int] = None
    # 服务端修改时间
    server_mtime: Optional[int] = None
    # 文件名
    server_filename: Optional[str] = None
    # 文件大小
    size: Optional[int] = None


class QueryShareDataListData(BaseModel):
    # 返回的文件列表个数
    count: Optional[int] = None
    # 文件列表
    item_list: Optional[list[QueryShareDataListItem]] = None


class QueryShareDataListResult(BaseModel):
    # 错误码
    errno: Optional[int] = None
    # 请求标识
    request_id: Optional[int] = None
    # 错误信息
    show_msg: Optional[str] = None
    # 响应数据
    data: Optional[QueryShareDataListData] = None


class TransferShareData(BaseModel):
    # 任务id，同步返回 0
    task_id: Optional[str] = None
    # 权益绑定错误号
    tkbind_errno: Optional[int] = None


class TransferShareResult(BaseModel):
    # 错误码
    errno: Optional[int] = None
    # 请求标识
    request_id: Optional[int] = None
    # 错误信息
    show_msg: Optional[str] = None
    # 响应数据
    data: Optional[TransferShareData] = None


class TransferShareTaskQueryDataDescItem(BaseModel):
    """任务文件列表项"""
    from_: Optional[str] = None
    # 转存文件来源path
    # 转存文件保存path
    to: Optional[str] = None
    # 转存文件保存fsid
    to_fs_id: Optional[int] = None


class TransferShareTaskQueryDataDesc(BaseModel):
    """任务结果详情"""
    # 执行成功文件数
    succNum: Optional[int] = None
    num_limit: Optional[int] = None
    num_limit_no_vip: Optional[int] = None
    # 任务文件列表
    item_list: Optional[list[TransferShareTaskQueryDataDescItem]] = None


class TransferShareTaskQueryData(BaseModel):
    task_id: Optional[str] = None
    # 任务进度
    progress: Optional[int] = None
    # 任务状态：fail、running、success、pending（任务排队中，表示任务已经提交，待执行）
    status: Optional[str] = None
    # 任务结果详情
    desc: Optional[TransferShareTaskQueryDataDesc] = None


class TransferShareTaskQueryResult(BaseModel):
    # 错误码
    errno: Optional[int] = None
    # 请求标识
    request_id: Optional[int] = None
    # 错误信息
    show_msg: Optional[str] = None
    # 响应数据
    data: Optional[TransferShareTaskQueryData] = None
