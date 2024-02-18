from __future__ import annotations
from weakref import WeakValueDictionary

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.CustomReport import *


class CustomReportManager:
    """
    A suite to run a simple or complex query with conditions across a linage of records.
    """

    user: SapioUser
    __instances: WeakValueDictionary[SapioUser, CustomReportManager] = WeakValueDictionary()
    __initialized: bool

    def __new__(cls, user: SapioUser):
        """
        Observes singleton pattern per record model manager object.
        """
        obj = cls.__instances.get(user)
        if not obj:
            obj = object.__new__(cls)
            obj.__initialized = False
            cls.__instances[user] = obj
        return obj

    def __init__(self, user: SapioUser):
        """
        Obtain a custom report manager to run advanced searches for a user context.
        :param user: The user context to create custom report.
        """
        if self.__initialized:
            return
        self.user = user
        self.__initialized = True

    def run_system_report_by_name(self, system_report_name: str,
                                  page_size: Optional[int] = None, page_number: Optional[int] = None) -> CustomReport:
        """
        Given a custom report name of a saved custom report, run it and return results.
        :param system_report_name: The system report name to search for.
        :param page_size: The page size of this report.
        If this is greater than the license limit, it will be limited by license on result.
        :param page_number: The page number of this report.
        """
        sub_path = self.user.build_url(['report', 'runSystemReportByName', system_report_name])
        params = dict()
        if page_size is not None:
            params['pageSize'] = page_size
        if page_number is not None:
            params['pageNumber'] = page_number
        response = self.user.get(sub_path, params)
        self.user.raise_for_status(response)
        json_dct = response.json()
        return CustomReport.from_json(json_dct)

    def run_custom_report(self, custom_report_request: CustomReportCriteria) -> CustomReport:
        """
        Run on-demand custom report.
        :param custom_report_request: The custom report request object containing all attributes about the request.
        :return: A custom report that has been executed by server.
        """
        sub_path = self.user.build_url(['report', 'runCustomReport'])
        payload = custom_report_request.to_json()
        response = self.user.post(sub_path, payload=payload)
        self.user.raise_for_status(response)
        json_dct = response.json()
        return CustomReport.from_json(json_dct)

    def run_quick_report(self, report_term: RawReportTerm,
                         page_size: Optional[int] = None, page_number: Optional[int] = None) -> CustomReport:
        """
        Restricted to single condition but easier to use.
        :param page_size: The page size of this report. If this is greater than the license limit,
        it will be limited by license on result.
        :param page_number: The page number of this report.
        :param report_term:
        :return:
        """
        sub_path = self.user.build_url(['report', 'runQuickReport'])
        payload = report_term.to_json()
        params = dict()
        if page_size is not None:
            params['pageSize'] = page_size
        if page_number is not None:
            params['pageNumber'] = page_number
        response = self.user.post(sub_path, params=params, payload=payload)
        self.user.raise_for_status(response)
        json_dct = response.json()
        return CustomReport.from_json(json_dct)
