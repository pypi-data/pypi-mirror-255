from hamunafs.net.api import upload, send

from threading import Lock

class TuCang:
    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password
        self.login_token = None
        self.parent_id = None
        self.folder_need_reload = True

        self.locker = Lock()

    @property
    def logined(self):
        return self.login_token is not None

    async def init(self):
        ret = await self.login()

        if ret:
            ret = await self.list_folders()

    async def login(self):
        resp = await send('https://tucang.cc/api/auth/login', 'post', {
            'username': self.username,
            'password': self.password,
            'verificationCode': ''
        })

        if resp is not None:
            if resp['code'] == '200':
                self.login_token = resp['data']['token']
                print('Tucang 登录成功!')
                return True
            else:
                print('Tucang 登录失败: ' + resp['msg'])
        return False

    async def list_folders(self, tries=0):
        with self.locker:
            resp = await send('https://tucang.cc/api/folder/folderList', 'get', {
                'token': self.login_token
            })
            if resp is not None:
                if resp['code'] == '200':
                    self.folders = resp['data']

                    parent_folder = [f for f in self.folders if f['parentId'] == 0]
                    if len(parent_folder) >= 1:
                        self.parent_id = parent_folder[0]['id']
                    
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                if tries < 3:
                    return await self.list_folders(tries+1)
                return False

    async def create_folder(self, name, tries=0):
        ret, e = self.folder_match(name)
        if not ret:
            resp = await send('https://tucang.cc/api/folder/create', 'post', {
                'parentId': self.parent_id,
                'folderName': name
            }, headers={
                'token': self.login_token
            })

            if resp is not None:
                self.folder_need_reload = True
                ret = await self.list_folders()
                if ret:
                    print('刷新目录成功')
                    self.folder_need_reload = False
                else:
                    print('刷新目录失败')

                return True
            else:
                if tries < 3:
                    return await self.create_folder(name)
                else:
                    return False

    def folder_match(self, folder_name):
        matches = [f for f in self.folders if f['name'] == folder_name]
        ret = len(matches) > 0
        if ret:
            return ret, matches[0]
        else:
            return ret, None

    async def upload(self, file, folder_name, auto_create_folder=True):
        can_upload = True
        if auto_create_folder:
            if self.folder_need_reload:
                ret = await self.list_folders()
                if ret:
                    ret, match = self.folder_match(folder_name)
                    if not ret:
                        ret = await self.create_folder(folder_name)
                        if ret:
                            can_upload, match = self.folder_match(folder_name)
        else:
            can_upload, match = self.folder_match(folder_name)
        if can_upload:
            resp = await upload('https://tucang.cc/api/image/upload', file, {
                'folderId': str(match['id'])
            }, headers={
                'token': self.login_token
            })

            if resp:
                if resp['success']:
                    return True, resp['data']['url']
                else:
                    return False, resp['msg']
            else:
                return False, 'API出错'
        else:
            return False, '列出目录失败'