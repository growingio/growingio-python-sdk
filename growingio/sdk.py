# -*- coding: utf-8 -*-

import datetime
import time
import json
import urllib
import urllib2
import snappy


SDK_VERSION = '1.0.1'

try:
    isinstance("", basestring)

    def is_str(s):
        return isinstance(s, basestring)
except NameError:
    def is_str(s):
        return isinstance(s, str)
try:
    isinstance(1, long)

    def is_int(n):
        return isinstance(n, int) or isinstance(n, long)
except NameError:
    def is_int(n):
        return isinstance(n, int)


class GrowingIOException(Exception):
    pass


class GrowingIOIllegalDataException(GrowingIOException):
    """
    在发送的数据格式有误时，SDK会抛出此异常，用户应当捕获并处理。
    """
    pass


class GrowingIONetworkException(GrowingIOException):
    """
    在因为网络或者不可预知的问题导致数据无法发送时，SDK会抛出此异常，用户应当捕获并处理。
    """
    pass


class GrowingIO(object):
    """
    使用一个 GrowingIO 的实例来进行数据发送。
    """

    def __init__(self, ai=None, client_id=None, is_debug=False, _request_timeout=None):
        """
        初始化一个 GrowingIO 的实例。
        @param ai account id 从 GrowingIO 的管理界面获得。
        @param client id 从 GrowingIO 申请获得。
        """
        self._ai = ai
        self._client_id = client_id
        self._url = "https://api.growingio.com/custom/{ai}/events".format(
            ai=ai)
        self._is_debug = is_debug
        self._request_timeout = _request_timeout

    def track(self, user_id, event_name, properties=None):
        """
        跟踪一个用户的行为。

        :param user_id: 登陆用户的唯一标识
        :param event_name: 事件名称
        :param properties: 事件的属性
        :param gr_user_id: 访问用户唯一标识
        :param session_id: 用户会话唯一标识
        """
        data = self._check_data(event_name, properties)
        normal_data = self._normalize_data(data, event_name, user_id)
        self._send(normal_data)

    # def track_signup(self, distinct_id, original_id, properties=None):
        """
        映射访问用户和登陆用户，暂未实现。
        """

    def _normalize_data(self, data, event_name, user_id):
        time = self._extract_user_time(data)
        gr_user_id = data['u']
        del data['u']
        session_id = data['s']
        del data['s']
        common_properties = self._get_common_properties()
        parameters = {
            "tm": time,
            "cs1": "user:{user_id}".format(user_id=user_id),
            "s": session_id,
            "u": gr_user_id,
            "ai": "{ai}".format(ai=self._ai),
            "t": "cstm",
            "n": event_name,
            "e": data
        }
        return [dict(common_properties, **parameters)]

    def _check_data(self, event_name, data):
        # 检查 u session_id
        if data["u"] is None or len(str(data['u'])) == 0:
            raise GrowingIOIllegalDataException(
                "property [u] must not be empty")

        if data["s"] is None or len(str(data['s'])) == 0:
            raise GrowingIOIllegalDataException(
                "property [s] must not be empty")

        # 检查 time
        if data.has_key('time') and isinstance(data['time'], datetime.datetime):
            data['time'] = time.mktime(
                data['time'].timetuple()) * 1000 + data['time'].microsecond / 1000
        if data.has_key('time'):
            ts = int(data['time'])
            ts_num = len(str(ts))
            if ts_num < 10 or ts_num > 13:
                raise GrowingIOIllegalDataException(
                    "property [time] must be a timestamp in microseconds")

            if ts_num == 10:
                ts *= 1000
            data['time'] = ts

        # 检查 Event Name

        # 检查 properties
        for key in data.keys():
            if not is_str(key):
                raise GrowingIOIllegalDataException(
                    "property key must be a str. [key=%s]" % str(key))
            if len(key) > 255:
                raise GrowingIOIllegalDataException(
                    "the max length of property key is 256. [key=%s]" % str(key))

            value = data[key]

            if is_str(value) and len(value) > 8191:
                raise GrowingIOIllegalDataException(
                    "the max length of property key is 8192. [key=%s]" % str(key))

            if not is_str(value) and not is_int(value) and not isinstance(value, float)\
                    and not isinstance(value, datetime.datetime) and not isinstance(value, datetime.date)\
                    and not isinstance(value, list) and value is not None:
                raise GrowingIOIllegalDataException(
                    "property value must be a str/int/float/datetime/date/list. [value=%s]" % type(value))
            if isinstance(value, list):
                for lvalue in value:
                    if not is_str(lvalue):
                        raise GrowingIOIllegalDataException(
                            "[list] property's value must be a str. [value=%s]" % type(lvalue))

        return data
    @staticmethod
    def _now():
        """
        系统当前时间。
        """
        return int(time.time() * 1000)

    def _extract_user_time(self, properties):
        """
        如果用户传入了 $time 字段，则不使用当前时间。
        """
        if properties is not None and '$time' in properties:
            t = properties['$time']
            del (properties['$time'])
            return t
        return self._now()

    def _do_request(self, data):
        """
        使用 urllib 发送数据给服务器，如果发生错误会抛出异常。
        """
        try:
            request = urllib2.Request(self._url + '?stm=' + str(self._now()), data)
            request.add_header('Content-Type', 'text/plain')
            request.add_header('charset', 'utf-8')
            request.add_header('X-Client-Id', self._client_id)
            if self._request_timeout is not None:
                urllib2.urlopen(request, timeout=self._request_timeout)
            else:
                urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            raise GrowingIONetworkException(e)
        return True

    def _compress_msg(self, msg):
        """
        使用snappy压缩数据
        """
        raw_data = json.dumps(msg)
        if self._is_debug:
            print msg
        compress_data = snappy.compress(raw_data)
        return compress_data

    def _send(self, msg):
        compress_msg = self._compress_msg(msg)
        result = self._do_request(compress_msg)
        return result

    def _get_common_properties(self):
        """
        构造所有 Event 通用的属性: 比如SDK版本属性
        """
        common_properties = {
            'sdk_type': 'python',
            'sdk_version': SDK_VERSION,
        }
        return common_properties
