from urllib.parse import urlparse
import json
from typing import List, Optional, Union
from datetime import datetime
from pprint import pprint
import maya
import requests
from requests.auth import HTTPBasicAuth
from loguru import logger


from ocpy import OcPyRequestException
from ocpy.api.api_client import OpenCastBaseApiClient
from ocpy.model.acl import ACL, Action


class Series:
    def __init__(self, user, password, url, data) -> None:
        self.base_url = url
        self.user = user
        self.password = password
        self.data = data

        self._augment_data()

    def __str__(self) -> str:
        return json.dumps(
            self.data,
            sort_keys=True,
            indent=4,
            separators=(",", ": "),
            default=str,
        )

    def __repr__(self) -> str:
        return self.__str__()

    def _augment_data(self) -> None:
        if "created" in self.data:
            self.data["created"] = maya.parse(self.data["created"]).datetime()

    def get_acl(self, **kwargs) -> Optional[List[ACL]]:
        res = self.data.get("acl", None)
        if res is None:
            url = self.base_url + "/acl"
            res = requests.get(
                url, timeout=kwargs.pop("timeout", 30), auth=HTTPBasicAuth(self.user, self.password)
            )
            if not res.ok:
                return None
            res = res.json()
            self.data["acl"] = res
        acls = []
        for a in res:
            acls.append(ACL(a["allow"], a["role"], Action(a["action"])))
        return acls

    def get_metadata(self, raw=False, **kwargs):
        url = self.base_url + "/metadata"
        res = requests.get(
            url, timeout=kwargs.pop("timeout", 30), auth=HTTPBasicAuth(self.user, self.password)
        )
        if res.ok:
            if raw:
                return res.json()
            meta_result = dict()
            for r in res.json():
                # merge metadata
                meta_result = {
                    **meta_result,
                    **{
                        m["id"]: m["value"]
                        for m in r["fields"]
                        if "value" in m
                    },
                }
            return meta_result
        return None

    def set_acl(self, acl_list, override=False, **kwargs):
        url = self.base_url + "/acl"
        if isinstance(acl_list, List):
            acls = []
            for a in acl_list:
                if isinstance(a, ACL):
                    acls.append(a.get_acl_dict())
                else:
                    acls.append(a)
            acl_list = acls
        if isinstance(acl_list, ACL):
            acl_list = [acl_list.get_acl_dict()]

        data = {
            "acl": json.dumps(acl_list),
            "override": "true" if override else "false",
            #"override": True if override else False,
        }
        logger.debug(f"set acl data: {data}")
        res = requests.put(
            url,
            timeout=kwargs.pop("timeout", 30),
            data=data,
            auth=HTTPBasicAuth(self.user, self.password),
        )
        if res.ok:
            return res.json()
        raise OcPyRequestException(
            "could not set ACL! ("
            + res.text
            + " ["
            + str(res.status_code)
            + "])"
            + "acl: "
            + json.dumps(acl_list)
        )

    def add_to_acl(self, acl: Union[ACL, List[ACL]], override=False):
        logger.debug(f"adding to acl: {acl}")
        actual_acl = self.get_acl()
        if not isinstance(acl, List):
            acl = [acl]
        for n_a in acl:
            found = False
            for a_a in actual_acl:
                if a_a == n_a:
                    found = True
                    break
            if not found:
                actual_acl.append(n_a)

        return self.set_acl(actual_acl, override=override)

    def remove_from_acl(self, acl: ACL):
        actual_acl = self.get_acl()

        if not isinstance(acl, List):
            acl = [acl]
        for aa in actual_acl:
            for na in acl:
                if aa == na:
                    actual_acl.remove(na)
        return self.set_acl(actual_acl)

    def get_properties(self, **kwargs):
        url = self.base_url + "/properties"
        res = requests.get(
            url, auth=HTTPBasicAuth(self.user, self.password), timeout=kwargs.pop("timeout", 30)
        )
        if res.ok:
            return res.json()
        return None

    def get_contributors(self):
        return self.data["contributors"]

    def get_created(self):
        return self.data["created"]

    def get_creator(self):
        return self.data["creator"]

    def get_identifier(self):
        return self.data["identifier"]

    def get_organizers(self):
        return self.data["organizers"]

    def get_publishers(self):
        return self.data["publishers"]

    def get_subjects(self):
        return self.data["subjects"]

    def get_title(self):
        return self.data["title"]

    def get_events(self, limit=100, **kwargs):
        from ocpy.api import EventsApi

        parsed_url = urlparse(self.base_url)
        url = "{}://{}".format(parsed_url.scheme, parsed_url.netloc)
        ev_api = EventsApi(self.user, self.password, url)
        return ev_api.get_events_part_of(self, limit, **kwargs)

    def delete(self):
        res = requests.delete(
            self.base_url, auth=HTTPBasicAuth(self.user, self.password)
        )
        if res.ok:
            return "ok"
        raise OcPyRequestException("could not delete series!", response=res)


class SeriesApi(OpenCastBaseApiClient):
    def __init__(self, user=None, password=None, server_url=None, **kwargs):
        super().__init__(user, password, server_url)
        self.base_url = self.server_url + "/api/series"

    def get_series(
        self,
        method="GET",
        limit=100,
        offset=0,
        sign=True,
        with_acl=False,
        with_metadata=False,
        with_publications=False,
        series_filter=None,
        **kwargs,
    ) -> List[Series]:
        """
        :param method:
        :param limit:
        :param offset:
        :param sign:
        :param with_acl:
        :param with_metadata:
        :param with_publications:
        :param series_filter:
        :param kwargs:
        :return: List[Series]
        """
        parameters = {
            "limit": limit,
            "offset": offset,
            "sign": sign,
            "withacl": with_acl,
            "withmetadata": with_metadata,
            "withpublications": with_publications,
        }
        if series_filter:
            if isinstance(series_filter, SeriesApi.Filter):
                parameters["filter"] = series_filter.get_filter_string()
            else:
                parameters["filter"] = series_filter
        results = []
        res = requests.request(
            method,
            self.base_url,
            timeout=kwargs.pop("timeout", 30),
            auth=HTTPBasicAuth(self.user, self.password),
            params=parameters,
            **kwargs,
        )
        if res.ok:
            for e in res.json():
                results.append(
                    Series(
                        self.user,
                        self.password,
                        self.base_url + "/" + e["identifier"],
                        e,
                    )
                )
        return results

    def get_all_series(
        self,
        sign=True,
        with_acl=False,
        with_metadata=False,
        with_publications=False,
        series_filter=None,
        batch_size=100,
    ):
        result = []
        while True:
            res = self.get_series(
                sign=sign,
                with_acl=with_acl,
                with_metadata=with_metadata,
                with_publications=with_publications,
                series_filter=series_filter,
                limit=batch_size,
                offset=len(result),
            )
            if res is None or len(res) <= 0:
                break
            result.extend(res)
        return result

    def get_series_acl(self, series_id, **kwargs) -> List[ACL]:
        res = requests.get(
            self.base_url + f"/{series_id}/acl",
            auth=HTTPBasicAuth(self.user, self.password),
            timeout=kwargs.pop("timeout", 30),
            **kwargs,
        )
        acls = []
        if res.ok:
            for a in res.json():
                acls.append(ACL(a["allow"], a["role"], Action(a["action"])))
            return acls
        raise OcPyRequestException("could not get series acls!", response=res)

    def get_series_by_id(
        self,
        series_id,
        with_acl=False,
        **kwargs,
    ) -> Series:
        parameters = {"withacl": with_acl}
        res = requests.get(
            self.base_url + "/" + series_id,
            auth=HTTPBasicAuth(self.user, self.password),
            params=parameters,
            timeout=kwargs.pop("timeout", 30),
            **kwargs,
        )
        if res.ok:
            series = res.json()
            return Series(
                self.user,
                self.password,
                self.base_url + "/" + series["identifier"],
                series,
            )
        logger.error(f"{res.status_code}: {res.text}")
        raise OcPyRequestException("could not get series!", response=res)

    def create_series(self, acl, metadata, theme=None, **kwargs) -> Series:
        if isinstance(acl, List):
            acls = []
            for a in acl:
                if isinstance(a, ACL):
                    acls.append(a.get_acl_dict())
                else:
                    acls.append(a)
            acl = acls
        if isinstance(acl, ACL):
            acl = acl.get_acl_dict()
        data = {
            "acl": json.dumps(acl),
            "metadata": json.dumps(metadata),
            "theme": theme,
        }

        res = requests.post(
            self.base_url + "/",
            timeout=kwargs.pop("timeout", 30),
            auth=HTTPBasicAuth(self.user, self.password),
            data=data,
            **kwargs,
        )
        if res.ok:
            series = res.json()
            return Series(
                self.user,
                self.password,
                self.base_url + "/" + series["identifier"],
                series,
            )
        raise OcPyRequestException(
            "could not create event! (" + res.text + ")", response=res
        )

    class Filter:
        def __init__(self):
            self.filter_string = None

        def update_filter_string(self, update_string):
            if self.filter_string is None:
                self.filter_string = update_string
            else:
                self.filter_string += "," + update_string

        def set_contributors_filter(self, contributors):
            self.update_filter_string("contributors:{}".format(contributors))
            return self

        def set_creator_filter(self, creator):
            self.update_filter_string("creator:{}".format(creator))
            return self

        def set_creation_date_filter(self, date1: datetime, date2):
            self.update_filter_string(
                "creationDate:{}/{}".format(
                    str(date1).replace("+00:00", "Z"),
                    str(date2).replace("+00:00", "Z"),
                )
            )
            return self

        def set_language_filter(self, language):
            self.update_filter_string("language:{}".format(language))
            return self

        def set_license_filter(self, oc_license):
            self.update_filter_string("license:{}".format(oc_license))
            return self

        def set_organizers_filter(self, organizers):
            self.update_filter_string("organizers:{}".format(organizers))
            return self

        def set_managed_acl_filter(self, managed_acl):
            self.update_filter_string("managedAcl:{}".format(managed_acl))
            return self

        def set_subject_filter(self, subject):
            self.update_filter_string("subject:{}".format(subject))
            return self

        def set_text_filter_filter(self, text_filter):
            self.update_filter_string("textFilter:{}".format(text_filter))
            return self

        def set_title_filter(self, title):
            self.update_filter_string("title:{}".format(title))
            return self

        def get_filter_string(self):
            return self.filter_string


def main():
    api = SeriesApi()
    # s = api.get_series(limit=1)[0]
    # pprint(s)
    # ss = api.get_series(series_filter=SeriesApi.Filter().set_text_filter_filter("Kognitive"))
    # ss = api.get_series(series_filter=SeriesApi.Filter().set_title_filter("Kognitive Systeme"))
    # ss = api.get_series(series_filter=SeriesApi.Filter().set_text_filter_filter("Automotive Vision"))
    # ss = api.get_series(series_filter=SeriesApi.Filter().set_text_filter_filter("ZML Webcast"))
    # api.create_series()
    ss = api.get_series(limit=3)
    for s in ss:
        print(s)
        pprint(s.get_metadata(True))
        evs = s.get_events()
        for e in evs:
            print(e.get_api_channel_publication())
        # s.delete()

    # pprint(s.get_metadata())
    # pprint(s.get_acl())
    # pprint(s.get_properties())


if __name__ == "__main__":
    main()
