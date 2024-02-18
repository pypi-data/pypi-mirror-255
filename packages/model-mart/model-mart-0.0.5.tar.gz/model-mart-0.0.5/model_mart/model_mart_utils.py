import http
import json
import os.path
import uuid
import sys
import time
from queue import Empty, Queue
from threading import Thread

import requests
from minio import Minio
from minio.error import S3Error

_BAR_SIZE = 20
_KILOBYTE = 1024
_FINISHED_BAR = '#'
_REMAINING_BAR = '-'

_UNKNOWN_SIZE = '?'
_STR_MEGABYTE = ' MB'

_HOURS_OF_ELAPSED = '%d:%02d:%02d'
_MINUTES_OF_ELAPSED = '%02d:%02d'

_RATE_FORMAT = '%5.2f'
_PERCENTAGE_FORMAT = '%3d%%'
_HUMANINZED_FORMAT = '%0.2f'

_DISPLAY_FORMAT = '|%s| %s/%s %s [elapsed: %s left: %s, %s MB/sec]'

_REFRESH_CHAR = '\r'



class PandoraBox:
    def __init__(self, username, password, admin_host):
        self.admin_host = admin_host
        if username == "":
            print("Login failed, param username is empty")
            return
        if password == "":
            print("Login failed, param password is empty")
            return
        info = json.dumps({
            'username': username,
            'password': password
        })
        resp = self._login_req(info)
        if resp.status_code == http.HTTPStatus.BAD_REQUEST:
            if resp.text == "":
                return
            print(f"Login failed, err msg:{resp.json().get('msg')}")
            return
        if resp.status_code == http.HTTPStatus.OK:
            if resp.text == "":
                return
            code = resp.json().get("code")
            if code != 0:
                print(f"Login failed, err msg:{resp.json().get('msg')}")
                return
            self.key = resp.json()['gateway_info']['access_key']
            self.secret = resp.json()['gateway_info']['access_secret']
            self.bucket = resp.json()['gateway_info']['bucket']
            self.gateway = resp.json()['gateway_info']['gateway']
        self.client = Minio(
            self.gateway,
            access_key=self.key,
            secret_key=self.secret,
            secure=False,
        )
        self.user = username
        self.is_login = True
        print("Login succeeded")
        return

    def model_init(self, model_name, description, library, data_set, task):
        if not self.is_login:
            print("User is not login")
            return
        if model_name == "":
            print("Param model_name is empty")
            return
        info = json.dumps({
            'model_name': model_name,
            'description': description,
            'library': library,
            'data_set': data_set,
            'task': task,
            'creator': self.user,
        })
        resp = self._new_model_req(info)
        print(resp.text)

    def my_models(self):
        if not self.is_login:
            print("User is not login")
            return
        resp = self._get_user_model_list_req()
        if resp.status_code != http.HTTPStatus.OK:
            print(resp.status_code)
            return
        print(resp.json().get("data"))
        return resp.json().get("data")

    def get_model(self, model_name, tag, destination_path):
        if not self.is_login:
            print("User is not login")
            return
        if tag == "":
            print("Param tag is empty")
            return
        if model_name == "":
            print("Param model_name is empty")
            return
        if os.path.isfile(destination_path):
            print("Param destination_path must be a folder")
            return
        if not os.path.exists(destination_path):
            print("Destination_path is not exist")
            return
        resp = self._get_tag_storage_path_req(model_name, tag)
        if resp.status_code == http.HTTPStatus.BAD_REQUEST:
            print(resp.text)
            return
        blob_path = resp.json().get("blob_path")
        if os.path.isdir(destination_path):
            objects = self.client.list_objects(
                self.bucket, recursive=True, prefix=blob_path,
            )
            for obj in objects:
                parts = obj.object_name.split('/')
                if len(parts) > 4:
                    full_path = '/'.join(parts[3:])
                else:
                    full_path = ''
                err = self._download(obj.object_name, os.path.join(destination_path, full_path))
                if err != "":
                    return err

            print("Files download successfully.")
        return

    def version_list(self, model_name):
        if not self.is_login:
            print("User is not login")
            return
        resp = self._get_model_version_list_req(model_name)
        if resp.status_code != http.HTTPStatus.OK:
            print(resp.status_code)
            return
        print(resp.json().get("version_list"))
        return resp.json().get("version_list")

    def register_model(self, model_name, tag, local_path):
        if not self.is_login:
            print("User is not login")
            return
        if model_name == "":
            print("Param model_name is empty")
            return
        if local_path == "":
            print("Param local_path is empty")
            return
        if tag == "":
            print("Param tag is empty")
            return
        blob_path = ""
        guid = str(uuid.uuid4())
        resp = self._get_model_id_req(model_name)
        if resp.status_code == http.HTTPStatus.BAD_REQUEST:
            print(resp.json().get("msg"))
            return
        if resp.status_code != http.HTTPStatus.OK:
            print(resp.status_code)
            return
        if os.path.isfile(local_path):
            folder_name = os.path.basename(os.path.dirname(local_path))
            file_name = os.path.basename(local_path)
            destination_path = "/models/{model_name}/{guid}/{folder_name}/{file_name}".format(model_name=model_name,
                                                                                              guid=guid,
                                                                                              folder_name=folder_name,
                                                                                              file_name=file_name)
            err = self._upload(local_path, destination_path)
            if err != "":
                return
            blob_path = destination_path
            print("File uploaded successfully.")
        elif os.path.isdir(local_path):
            local_path = os.path.abspath(local_path)
            allfiles = _allfiles(local_path)
            for file in allfiles:
                master_folder_name = os.path.basename(os.path.dirname(local_path))
                file_path = file.split(master_folder_name + '/')[1]
                destination_path = os.path.join('models', model_name, guid, file_path)
                source_path = os.path.join(local_path, file)
                err = self._upload(source_path, destination_path)
                if err != "":
                    return
            blob_path = "/models/{model_name}/{guid}/".format(model_name=model_name, guid=guid)
            print("Files uploaded successfully.")
        else:
            print("Please input right path")

        info = json.dumps({
            'model_name': model_name,
            'tag': tag,
            'blob_path': blob_path,
            'guid': "{guid}".format(guid=guid),
        })
        address = self._add_model_version_req(info)
        if address.status_code == http.HTTPStatus.BAD_REQUEST:
            print(address.json().get("msg"))
            return
        if resp.status_code != http.HTTPStatus.OK:
            print(resp.status_code)
            return

    def _upload(self, local_path, destination):
        try:
            self.client.fput_object(
                self.bucket,
                destination,
                local_path,
                progress=Progress(),  # 在回调中调用线程对象的run方法
            )
            print("File uploaded successfully.")
            return ""
        except S3Error as err:
            print("Error: ", err)
            return err

    def _download(self, source, destination):
        try:
            # Download data of an object.
            self.client.fget_object(
                self.bucket,
                source,
                destination,
                progress=Progress(),  # 在回调中调用线程对象的run方法
            )
            return ""
        except S3Error as err:
            print("Error: ", err)
            return err

    # def _delete_model_version_req(self, model_name, model_version):
    #     base_url = "http://{host}/api/v1/model/version/{model_name}/{model_version}" \
    #         .format(host=ADMIN_HOST, model_name=model_name, model_version=model_version)
    #     resp = requests.delete(url=base_url)
    #     return resp
    #
    # def _delete_model_tag_req(self, model_name, model_tag):
    #     base_url = "http://{host}/api/v1/model/tag/{model_name}/{model_tag}" \
    #         .format(host=ADMIN_HOST, model_name=model_name, model_tag=model_tag)
    #     resp = requests.delete(url=base_url)
    #     return resp
    #
    # def _delete_model_req(self, model_name):
    #     base_url = "http://{host}/api/v1/model/{model_name}" \
    #         .format(host=ADMIN_HOST, model_name=model_name)
    #     resp = requests.delete(url=base_url)
    #     return resp

    def _get_model_id_req(self, model_name):
        headers = {'username': self.user}
        base_url = "{host}/api/v1/model/{model_name}/id" \
            .format(host=self.admin_host, model_name=model_name)
        resp = requests.get(url=base_url, headers=headers)
        return resp

    def _get_model_info_req(self, model_name):
        headers = {'username': self.user}
        base_url = "{host}/api/v1/model/{model_name}/info" \
            .format(host=self.admin_host, model_name=model_name)
        resp = requests.get(url=base_url, headers=headers)
        return resp

    def _get_tag_storage_path_req(self, model_name, model_tag):
        headers = {'username': self.user}
        base_url = "{host}/api/v1/model/tag/{model_name}/{model_tag}/storage" \
            .format(host=self.admin_host, model_name=model_name, model_tag=model_tag)
        resp = requests.get(url=base_url, headers=headers)
        return resp

    def _get_version_storage_path_req(self, model_name, model_version):
        headers = {'username': self.user}
        base_url = "{host}/api/v1/model/version/{model_name}/{model_version}/storage" \
            .format(host=self.admin_host, model_name=model_name, model_version=model_version)
        resp = requests.get(url=base_url, headers=headers)
        return resp

    def _get_model_version_list_req(self, model_name):
        headers = {'username': self.user}
        base_url = "{host}/api/v1/model/{model_name}/version/list" \
            .format(host=self.admin_host, model_name=model_name)
        resp = requests.get(url=base_url, headers=headers)
        return resp

    def _get_user_model_list_req(self):
        headers = {'username': self.user}
        base_url = "{host}/api/v1/{username}/model/list" \
            .format(host=self.admin_host, username=self.user)
        resp = requests.get(url=base_url, headers=headers)
        return resp

    def _add_model_version_req(self, json_info):
        headers = {'Content-Type': 'application/json', 'username': self.user}
        base_url = "{host}/api/v1/model/version/add".format(host=self.admin_host)
        resp = requests.post(url=base_url, data=json_info, headers=headers)
        return resp

    def _new_model_req(self, json_info):
        headers = {'Content-Type': 'application/json', 'username': self.user}
        base_url = "{host}/api/v1/model/init".format(host=self.admin_host)
        resp = requests.post(url=base_url, data=json_info, headers=headers)
        return resp

    def _login_req(self, json_info):
        headers = {'Content-Type': 'application/json'}
        base_url = "{host}/api/v1/login".format(host=self.admin_host)
        resp = requests.post(url=base_url, data=json_info, headers=headers)
        return resp

    def get_login_status(self):
        return self.is_login


def _allfiles(folder):
    filepath_list = []
    for root, folder_names, file_names in os.walk(folder):
        for file_name in file_names:
            file_path = root + os.sep + file_name
            filepath_list.append(file_path)
            print(file_path)
    # file_path = sorted(file_path, key=str.lower)
    return filepath_list


class Progress(Thread):
    """
        Constructs a :class:`Progress` object.
        :param interval: Sets the time interval to be displayed on the screen.
        :param stdout: Sets the standard output

        :return: :class:`Progress` object
    """

    def __init__(self, interval=1, stdout=sys.stdout):
        Thread.__init__(self)
        self.prefix = None
        self.daemon = True
        self.total_length = 0
        self.interval = interval
        self.object_name = None

        self.last_printed_len = 0
        self.current_size = 0

        self.display_queue = Queue()
        self.initial_time = time.time()
        self.stdout = stdout
        self.start()

    def set_meta(self, total_length, object_name):
        """
        Metadata settings for the object. This method called before uploading
        object
        :param total_length: Total length of object.
        :param object_name: Object name to be showed.
        """
        self.total_length = total_length
        self.object_name = object_name
        self.prefix = self.object_name + ': ' if self.object_name else ''

    def run(self):
        displayed_time = 0
        while True:
            try:
                # display every interval secs
                task = self.display_queue.get(timeout=self.interval)
            except Empty:
                elapsed_time = time.time() - self.initial_time
                if elapsed_time > displayed_time:
                    displayed_time = elapsed_time
                if self.total_length == 0:
                    continue
                self.print_status(current_size=self.current_size,
                                  total_length=self.total_length,
                                  displayed_time=displayed_time,
                                  prefix=self.prefix)
                continue

            current_size, total_length = task
            displayed_time = time.time() - self.initial_time
            if self.total_length == 0:
                continue
            self.print_status(current_size=current_size,
                              total_length=total_length,
                              displayed_time=displayed_time,
                              prefix=self.prefix)
            self.display_queue.task_done()
            if current_size == total_length:
                # once we have done uploading everything return
                self.done_progress()
                return

    def update(self, size):
        """
        Update object size to be showed. This method called while uploading
        :param size: Object size to be showed. The object size should be in
                     bytes.
        """
        if not isinstance(size, int):
            raise ValueError('{} type can not be displayed. '
                             'Please change it to Int.'.format(type(size)))

        self.current_size += size
        self.display_queue.put((self.current_size, self.total_length))

    def done_progress(self):
        self.total_length = 0
        self.object_name = None
        self.last_printed_len = 0
        self.current_size = 0

    def print_status(self, current_size, total_length, displayed_time, prefix):
        formatted_str = prefix + format_string(
            current_size, total_length, displayed_time)
        self.stdout.write(_REFRESH_CHAR + formatted_str + ' ' *
                          max(self.last_printed_len - len(formatted_str), 0))
        self.stdout.flush()
        self.last_printed_len = len(formatted_str)


def seconds_to_time(seconds):
    """
    Consistent time format to be displayed on the elapsed time in screen.
    :param seconds: seconds
    """
    minutes, seconds = divmod(int(seconds), 60)
    hours, m = divmod(minutes, 60)
    if hours:
        return _HOURS_OF_ELAPSED % (hours, m, seconds)
    else:
        return _MINUTES_OF_ELAPSED % (m, seconds)


def format_string(current_size, total_length, elapsed_time):
    """
    Consistent format to be displayed on the screen.
    :param current_size: Number of finished object size
    :param total_length: Total object size
    :param elapsed_time: number of seconds passed since start
    """

    n_to_mb = current_size / _KILOBYTE / _KILOBYTE
    elapsed_str = seconds_to_time(elapsed_time)

    rate = _RATE_FORMAT % (
            n_to_mb / elapsed_time) if elapsed_time else _UNKNOWN_SIZE
    frac = float(current_size) / total_length
    bar_length = int(frac * _BAR_SIZE)
    bar = (_FINISHED_BAR * bar_length +
           _REMAINING_BAR * (_BAR_SIZE - bar_length))
    percentage = _PERCENTAGE_FORMAT % (frac * 100)
    left_str = (
        seconds_to_time(
            elapsed_time / current_size * (total_length - current_size))
        if current_size else _UNKNOWN_SIZE)

    humanized_total = _HUMANINZED_FORMAT % (
            total_length / _KILOBYTE / _KILOBYTE) + _STR_MEGABYTE
    humanized_n = _HUMANINZED_FORMAT % n_to_mb + _STR_MEGABYTE

    return _DISPLAY_FORMAT % (bar, humanized_n, humanized_total, percentage,
                              elapsed_str, left_str, rate)
