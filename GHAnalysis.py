import json
import os
import argparse
import time
import mmap
from multiprocessing import Pool, cpu_count
import shutil

class Data:
    def __init__(self, dict_address: str = None, reload: int = 0):
        if reload == 1:
            try:
                os.makedirs('json_tempfolder')
            except:
                shutil.rmtree('json_tempfolder')
                os.makedirs('json_tempfolder')
            self.__init(dict_address)

        if dict_address is None and not os.path.exists('Personal_Event.json') and not os.path.exists('Project_Event.json') and not os.path.exists('Personal_Project_Event.json'):
            raise RuntimeError("Error: init failed")

        x = open('Personal_Event.json', 'r', encoding='utf-8').read()
        # 每个人四种事件的数量
        self.__4Events4PerP = json.loads(x)
        x = open('Project_Event.json', 'r', encoding='utf-8').read()
        # 每个项目四种事件的数量
        self.__4Events4PerR = json.loads(x)
        x = open('Personal_Project_Event.json', 'r', encoding='utf-8').read()
        # 每个人在每个项目中四种事件的数量
        self.__4Events4PerPPerR = json.loads(x)

    def save_Processed_JsonFile(self, json_list, filename):
        # 把处理完的文件以json文件格式存下来，便于查询
        selected_infomation = []
        for i in json_list:
            if i['type'] not in ["PushEvent", "IssueCommentEvent", "IssuesEvent", "PullRequestEvent"]:
                continue
            selected_infomation.append({'actor__login': i['actor']['login'], 'type': i['type'], 'repo__name': i['repo']['name']})
        with open('json_tempfolder\\' + filename, 'w', encoding='utf-8') as f:
            json.dump(selected_infomation, f)

    def extract_Data_From_File(self, f, dict_address):
        # 从文件中读取数据
        json_list = []
        if f[-5:] == '.json':
            json_path = f
            x = open(dict_address + '\\' + json_path, 'r', encoding='utf-8')
            with mmap.mmap(x.fileno(), 0, access=mmap.ACCESS_READ) as m:
                # 通过mmap来进行内存映射
                m.seek(0, 0)
                obj = m.read()
                obj = str(obj, encoding="utf-8")
                str_list = [_x for _x in obj.split('\n') if len(_x) > 0]
                for _str in str_list:
                    try:
                        json_list.append(json.loads(_str))
                    except:
                        pass
            self.save_Processed_JsonFile(json_list, f)

    def __init(self, dict_address: str):
        self.__4Events4PerP = {}
        self.__4Events4PerR = {}
        self.__4Events4PerPPerR = {}

        for root, dic, files in os.walk(dict_address):
            # 调用多进程来处理文件的读取
            pool = Pool(processes=max(cpu_count(), 6))
            for f in files:
                if f[-5:] == '.json':
                    pool.apply_async(self.extract_Data_From_File, args=(f, dict_address))
            pool.close()
            pool.join()

        for root, dic, files in os.walk("json_tempfolder"):
            for f in files:
                if f[-5:] == '.json':
                    json_list = json.loads(open("json_tempfolder" + '\\' + f, 'r', encoding='utf-8').read())
                    for item in json_list:
                        if not self.__4Events4PerP.get(item['actor__login'], 0):
                            self.__4Events4PerP.update({item['actor__login']: {}})
                            self.__4Events4PerPPerR.update({item['actor__login']: {}})
                        self.__4Events4PerP[item['actor__login']][item['type']] = \
                            self.__4Events4PerP[item['actor__login']].get(item['type'], 0) + 1

                        if not self.__4Events4PerR.get(item['repo__name'], 0):
                            self.__4Events4PerR.update({item['repo__name']: {}})
                        self.__4Events4PerR[item['repo__name']][item['type']] = \
                            self.__4Events4PerR[item['repo__name']].get(item['type'], 0) + 1

                        if not self.__4Events4PerPPerR[item['actor__login']].get(item['repo__name'], 0):
                            self.__4Events4PerPPerR[item['actor__login']].update({item['repo__name']: {}})
                        self.__4Events4PerPPerR[item['actor__login']][item['repo__name']][item['type']] = \
                            self.__4Events4PerPPerR[item['actor__login']][item['repo__name']].get(item['type'], 0) + 1

        with open('Personal_Event.json', 'w', encoding='utf-8') as f:
            json.dump(self.__4Events4PerP, f)
        with open('Project_Event.json', 'w', encoding='utf-8') as f:
            json.dump(self.__4Events4PerR, f)
        with open('Personal_Project_Event.json', 'w', encoding='utf-8') as f:
            json.dump(self.__4Events4PerPPerR, f)


    def getEventsUsers(self, username: str, event: str) -> int:
        if not self.__4Events4PerP.get(username,0):
            return 0
        else:
            return self.__4Events4PerP[username].get(event,0)

    def getEventsRepos(self, reponame: str, event: str) -> int:
        if not self.__4Events4PerR.get(reponame,0):
            return 0
        else:
            return self.__4Events4PerR[reponame].get(event,0)

    def getEventsUsersAndRepos(self, username: str, reponame: str, event: str) -> int:
        if not self.__4Events4PerP.get(username,0):
            return 0
        elif not self.__4Events4PerPPerR[username].get(reponame,0):
            return 0
        else:
            return self.__4Events4PerPPerR[username][reponame].get(event,0)


class Run:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.data = None
        self.argInit()
        print(self.analyse())

    def argInit(self):
        self.parser.add_argument('-i', '--init')
        self.parser.add_argument('-u', '--user')
        self.parser.add_argument('-r', '--repo')
        self.parser.add_argument('-e', '--event')

    def analyse(self):
        if self.parser.parse_args().init:
            self.data = Data(self.parser.parse_args().init, 1)
            return 0
        else:
            if self.data is None:
                self.data = Data()
            if self.parser.parse_args().event:
                if self.parser.parse_args().user:
                    if self.parser.parse_args().repo:
                        res = self.data.getEventsUsersAndRepos(
                            self.parser.parse_args().user, self.parser.parse_args().repo, self.parser.parse_args().event)
                    else:
                        res = self.data.getEventsUsers(
                            self.parser.parse_args().user, self.parser.parse_args().event)
                elif self.parser.parse_args().repo:
                    res = self.data.getEventsRepos(
                        self.parser.parse_args().repo, self.parser.parse_args().event)
                else:
                    raise RuntimeError("Error: argument -u|--user or -r|--repo cannot be found!")
            else:
                raise RuntimeError("Error: argument -e|--event cannot be found!")
        return res


if __name__ == '__main__':
    a = Run()
