
from time import time, sleep
from uuid import UUID
import requests


def get_sesames(apikey=None):
    ret = requests.get('https://api.candyhouse.co/public/sesames',
                       headers={'Authorization': apikey})
    if ret.status_code == 200:
        try:
            return [
                Sesame(UUID(profile['device_id']), apikey, profile['serial'],
                       profile['nickname'])
                for profile in ret.json()]
        except (TypeError, ValueError):
            raise SesameError('Can not parse server response')
    elif ret.status_code == 401:
        raise SesameAuthorityError('[%s] %s' % (ret.status_code, ret.text))
    else:
        raise SesameError('[%s] %s' % (ret.status_code, ret.text))


class Sesame(object):
    _id = None
    _apikey = None
    _serial = None
    _nickname = None

    def __init__(self, uuid, apikey, serial=None, nickname=None):
        self._id = uuid
        self._apikey = apikey
        self._serial = serial
        self._nickname = nickname

    def __repr__(self):
        return '<pysesame2.Sesame %s, nickname=%s>' % (self._id, self._nickname)

    @property
    def id(self):
        return self._id

    @property
    def serial(self):
        return self._serial

    @property
    def nickname(self):
        return self._nickname

    def get_status(self):
        ret = requests.get('https://api.candyhouse.co/public/sesame/%s' % str(self._id),
                           headers={'Authorization': self._apikey})
        if ret.status_code == 200:
            try:
                return ret.json()
            except (TypeError, ValueError):
                raise SesameError('Can not parse server response')
        elif ret.status_code == 401:
            raise SesameAuthorityError('[%s] %s' % (ret.status_code, ret.text))
        else:
            raise SesameError('[%s] %s' % (ret.status_code, ret.text))

    def _async_command(self, command):
        ret = requests.post('https://api.candyhouse.co/public/sesame/%s' % str(self._id),
                            headers={'Authorization': self._apikey},
                            json={'command': command})
        if ret.status_code == 200:
            try:
                task_id = ret.json()['task_id']
                return AsyncTask(task_id, self._apikey)
            except (TypeError, ValueError):
                raise SesameError('Can not parse server response')
        elif ret.status_code == 401:
            raise SesameAuthorityError('[%s] %s' % (ret.status_code, ret.text))
        else:
            raise SesameError('[%s] %s' % (ret.status_code, ret.text))

    def _sync_command(self, command, timeout):
        ttl = time() + timeout

        task = self._async_command(command)
        sleep(3)

        while task.pooling() is not True:
            if time() > ttl:
                raise SesameTimeoutError('Operation Timeout', task)

            if task.result is None:
                # Task is still in the queue
                sleep(1.5)
            else:
                # Task is processing
                sleep(0.35)
        return task

    def async_flush_status(self):
        return self._async_command('sync')

    def async_lock(self):
        return self._async_command('lock')

    def async_unlock(self):
        return self._async_command('unlock')

    def flush_status(self, timeout=180):
        return self._sync_command('sync', timeout)

    def lock(self, timeout=180):
        return self._sync_command('lock', timeout)

    def unlock(self, timeout=180):
        return self._sync_command('unlock', timeout)


class AsyncTask(object):
    _task_id = None
    _apikey = None
    result = None

    def __init__(self, task_id, apikey):
        self._task_id = task_id
        self._apikey = apikey

    def pooling(self):
        ret = requests.get('https://api.candyhouse.co/public/action-result?task_id=%s' % self._task_id,
                           headers={'Authorization': self._apikey})
        if ret.status_code == 200:
            try:
                self.result = ret.json()
                return self.result['status'] == 'terminated'
            except (TypeError, ValueError):
                raise SesameError('Can not parse server response')
        elif ret.status_code == 400:
            return False
        elif ret.status_code == 401:
            raise SesameAuthorityError('[%s] %s' % (ret.status_code, ret.text))
        else:
            raise SesameError('[%s] %s' % (ret.status_code, ret.text))

    @property
    def is_successful(self):
        if self.result is not None and self.result['status'] == 'terminated':
            return self.result['successful']
        else:
            return None

    @property
    def error(self):
        if self.result is not None and self.result['status'] == 'terminated':
            return self.result.get('error')
        else:
            return None


class SesameError(Exception):
    pass


class SesameAuthorityError(SesameError):
    pass


class SesameTimeoutError(SesameError):
    pass
