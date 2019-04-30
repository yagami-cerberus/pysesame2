
from time import time, sleep
from uuid import UUID
from requests import Session


def get_sesames(apikey=None):
    session = Session()
    session.headers['Authorization'] = apikey
    ret = session.get('https://api.candyhouse.co/public/sesames')
    if ret.status_code == 200:
        try:
            return [
                Sesame(UUID(profile['device_id']), serial=profile['serial'],
                       nickname=profile['nickname'], session=session)
                for profile in ret.json()]
        except (TypeError, ValueError):
            raise SesameError('Can not parse server response')
    elif ret.status_code == 401:
        raise SesameAuthorityError('[%s] %s' % (ret.status_code, ret.text))
    else:
        raise SesameError('[%s] %s' % (ret.status_code, ret.text))


class Sesame(object):
    _id = None
    _serial = None
    _nickname = None
    _session = None

    def __init__(self, uuid, apikey=None, serial=None, nickname=None, session=None):
        self._id = uuid
        self._serial = serial
        self._nickname = nickname

        if session:
            self._session = session
        else:
            self._session = Session()
            self._session.headers['Authorization'] = apikey

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
        ret = self._session.get('https://api.candyhouse.co/public/sesame/%s' % str(self._id))
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
        ret = self._session.post('https://api.candyhouse.co/public/sesame/%s' % str(self._id),
                                 json={'command': command})
        if ret.status_code == 200:
            try:
                task_id = ret.json()['task_id']
                return AsyncTask(task_id, self._session)
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
            sleep(0.75)
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

    def __init__(self, task_id, session):
        self._task_id = task_id
        self._session = session

    def pooling(self):
        ret = self._session.get('https://api.candyhouse.co/public/action-result?task_id=%s' % self._task_id)
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
