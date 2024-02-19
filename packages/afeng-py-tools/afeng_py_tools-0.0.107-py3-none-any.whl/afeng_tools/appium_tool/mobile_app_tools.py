"""
- pip install pydantic -i https://pypi.tuna.tsinghua.edu.cn/simple/
"""
from enum import Enum

from pydantic import BaseModel, Field


class MobileAppInfo(BaseModel):
    """手机应用信息"""
    app_name: str = Field(title="应用名")
    app_package: str = Field(title="应用package")
    app_activity: str = Field(title="应用activity")


class MobileAppInfoEnum(Enum):
    bai_jia_hao = MobileAppInfo(app_name='百家号', app_package='com.baidu.baijia',
                                app_activity='.splash.SplashActivity')
    bi_jian = MobileAppInfo(app_name='必剪', app_package='com.bilibili.studio',
                            app_activity='com.bcut.homepage.widget.MainActivity')
    bili_bili = MobileAppInfo(app_name='哔哩哔哩', app_package='tv.danmaku.bili', app_activity='.MainActivityV2')
    dou_yin = MobileAppInfo(app_name='抖音', app_package='com.ss.android.ugc.aweme',
                            app_activity='.splash.SplashActivity')
    kuai_shou = MobileAppInfo(app_name='快手', app_package='com.smile.gifmaker',
                              app_activity='com.yxcorp.gifshow.HomeActivity')
    qi_e_hao = MobileAppInfo(app_name='企鹅号', app_package='com.tencent.omapp',
                             app_activity='.ui.activity.SplashActivity')
    qq = MobileAppInfo(app_name='QQ', app_package='com.tencent.mobileqq',
                       app_activity='com.tencent.mobileqq.activity.SplashActivity')
    tao_bao = MobileAppInfo(app_name='淘宝', app_package='com.taobao.taobao',
                            app_activity='com.taobao.tao.welcome.Welcome')
    wei_xin = MobileAppInfo(app_name='微信', app_package='com.tencent.mm', app_activity='.ui.LauncherUI')
    xiao_hong_shu = MobileAppInfo(app_name='小红书', app_package='com.xingin.xhs',
                                  app_activity='.index.v2.IndexActivityV2')
    xi_gua_shi_pin = MobileAppInfo(app_name='西瓜视频', app_package='com.ss.android.article.video',
                                   app_activity='.activity.SplashActivity')
    zhi_fu_bao = MobileAppInfo(app_name='支付宝', app_package='com.eg.android.AlipayGphone',
                               app_activity='.AlipayLogin')
    jing_dong_reader = MobileAppInfo(app_name='京东读书', app_package='com.jd.app.reader',
                                     app_activity='com.jingdong.app.reader.logo.JdLogoActivity')
