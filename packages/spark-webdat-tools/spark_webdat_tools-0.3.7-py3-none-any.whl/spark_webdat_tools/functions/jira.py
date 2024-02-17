import json

import requests


class Jira(object):
    def __init__(self, username=None, token=None, proxy=False):
        self._session = requests.Session()
        self._session.auth = (username, token)
        self.base_url = "https://bitbucket.globaldevtools.bbva.com/bitbucket"
        self.base_path = ""
        self.proxies = proxy
        self.current_proxies = {
            'https': 'http://118.180.54.170:8080',
            'http': 'http://118.180.54.170:8080'
        }
        self.headers = {
            'Content-Type': 'application/json'
        }

        self._session.headers.update(self.headers)
        if not self.proxies:
            self._session.proxies.update({})
        else:
            self._session.proxies.update(self.current_proxies)

    def get_paginate(self, base_path=None):
        self.base_path = base_path
        url = f"{self.base_url}{self.base_path}"
        response = self._session.get(url, params={'start': 0})
        data_json = [response.json()]
        is_last_page = False
        paginate_list = list()
        while not is_last_page:
            for t in data_json:
                is_last_page = t["isLastPage"]
                data_values = t["values"]
                next_page_start = str(t.get("nextPageStart", None))
                for i in data_values:
                    paginate_list.append(i)
                    if is_last_page is False or next_page_start is None:
                        response2 = self._session.get(url, params={'start': next_page_start})
                        data_json = [response2.json()]
        return paginate_list

    def get_projects_key(self, project_name):
        self.base_path = f"/rest/api/1.0/projects/{project_name}/repos"
        rs = self.get_paginate(base_path=self.base_path)
        for i in rs:
            print(i)

    def get_projects_repo_branch_key(self, project_name, repo_name):
        self.base_path = f"/rest/api/1.0/projects/{project_name}/repos/{repo_name}/branches"
        rs = self.get_paginate(base_path=self.base_path)
        for i in rs:
            print(i)

    def get_projects_repo_permissions_groups(self, project_name, repo_name):
        self.base_path = f"/rest/api/1.0/projects/{project_name}/repos/{repo_name}/permissions/groups"
        rs = self.get_paginate(base_path=self.base_path)
        for i in rs:
            print(i)

    def post_projects_repo_permissions_groups(self, project_name, repo_name):
        self.base_path = f"/rest/api/1.0/projects/{project_name}/repos/{repo_name}/permissions/groups"
        url = f"{self.base_url}{self.base_path}"
        payload = {"permission": "REPO_READ", "name": "bbva_pe_datahub"}
        headers = {
            'Content-Type': "application/json"
        }
        self._session.put(url, headers=headers, params=payload)

    def get_projects_repo_permissions_users(self, project_name, repo_name):
        self.base_path = f"/rest/api/1.0/projects/{project_name}/repos/{repo_name}/permissions/users"
        rs = self.get_paginate(base_path=self.base_path)
        for i in rs:
            print(i)

    def get_projects_repo_reviewers_key(self, project_name, repo_name):
        self.base_path = f"/rest/default-reviewers/latest/projects/{project_name}/repos/{repo_name}/conditions"
        url = f"{self.base_url}{self.base_path}"
        rs = self._session.get(url)
        for i in rs:
            print(i)

    def post_projects_repo_reviewers_key(self, project_name, repo_name):
        self.base_path = f"/rest/default-reviewers/latest/projects/{project_name}/repos/{repo_name}/condition"
        url = f"{self.base_url}{self.base_path}"
        payload = json.dumps({
            "sourceMatcher": {
                "id": "ANY_REF_MATCHER_ID",
                "type": {
                    "id": "ANY_REF"
                }
            },
            "targetMatcher": {
                "id": "refs/heads/master",
                "type": {
                    "id": "BRANCH"
                }
            },
            "reviewers": [
                {
                    "emailAddress": "enrique.peinado@bbva.com",
                    "avatarUrl": "/bitbucket/users/enrique.peinado/avatar.png?s=32&v=1624888009569",
                    "displayName": "Enrique Peinado",
                    "name": "enrique.peinado",
                    "active": True,
                    "id": 40263,
                    "type": "NORMAL",
                    "slug": "enrique.peinado"
                },
                {
                    "emailAddress": "jack.guillen@bbva.com",
                    "avatarUrl": "https://secure.gravatar.com/avatar/214e3aa3094d0110d7ff7a73d46e6192.jpg?s=32&d=mm",
                    "displayName": "jack.guillen",
                    "name": "jack.guillen",
                    "active": True,
                    "id": 55495,
                    "type": "NORMAL",
                    "slug": "jack.guillen"
                },
                {
                    "emailAddress": "ray.lescano@bbva.com",
                    "avatarUrl": "/bitbucket/users/ray.lescano/avatar.png?s=32&v=1622843534992",
                    "displayName": "ray.lescano",
                    "name": "ray.lescano",
                    "active": True,
                    "id": 54832,
                    "type": "NORMAL",
                    "slug": "ray.lescano"
                },
                {
                    "emailAddress": "jesus.cierralta@bbva.com",
                    "avatarUrl": "https://secure.gravatar.com/avatar/9a68093d4b2e59ed5ed788d1663a06c6.jpg?s=32&d=mm",
                    "displayName": "jesus.cierralta",
                    "name": "jesus.cierralta",
                    "active": True,
                    "id": 33314,
                    "type": "NORMAL",
                    "slug": "jesus.cierralta"
                },
                {
                    "emailAddress": "joel.fernandez@bbva.com",
                    "avatarUrl": "/bitbucket/users/joel.fernandez/avatar.png?s=32&v=1691522130432",
                    "displayName": "joel.fernandez",
                    "name": "joel.fernandez",
                    "active": True,
                    "id": 108175,
                    "type": "NORMAL",
                    "slug": "joel.fernandez"
                },
            ],
            "requiredApprovals": "1"
        })
        headers = {
            'Content-Type': "application/json"
        }
        self._session.post(url, headers=headers, data=payload)

    def post_projects_repo_branch_permissions_key(self, project_name, repo_name):
        self.base_path = f"/rest/branch-permissions/2.0/projects/{project_name}/repos/{repo_name}/restrictions"
        url = f"{self.base_url}{self.base_path}"
        payload = json.dumps([{"scope": {"type": "REPOSITORY", "resourceId": 384332}, "id": 1458307, "type": "fast-forward-only",
                               "matcher": {"active": True, "id": "master", "displayId": "master", "type": {"name": "Branch", "id": "BRANCH"}},
                               "users": ["bot-datio-sandbox-bitbucket", "bot-dataproc-stacker-bitbucket"]},
                              {"scope": {"type": "REPOSITORY", "resourceId": 384332}, "id": 1458309, "type": "pull-request-only",
                               "matcher": {"active": True, "id": "master", "displayId": "master", "type": {"name": "Branch", "id": "BRANCH"}},
                               "users": ["bot-datio-sandbox-bitbucket", "bot-dataproc-stacker-bitbucket", "jonathan.quiza"]},
                              {"scope": {"type": "REPOSITORY", "resourceId": 384332}, "id": 1458308, "type": "no-deletes",
                               "matcher": {"active": True, "id": "master", "displayId": "master",
                                           "type": {"name": "Branch", "id": "BRANCH"}},
                               "users": ["bot-datio-sandbox-bitbucket", "bot-dataproc-stacker-bitbucket"]}])
        headers = {
            'Content-Type': "application/vnd.atl.bitbucket.bulk+json"
        }
        self._session.post(url, headers=headers, data=payload)
