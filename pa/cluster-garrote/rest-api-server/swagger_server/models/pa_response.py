# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.pa_response_used_l_ls import PAResponseUsedLLs  # noqa: F401,E501
from swagger_server.models.pa_response_used_nfvi_pops import PAResponseUsedNFVIPops  # noqa: F401,E501
from swagger_server.models.pa_response_used_v_ls import PAResponseUsedVLs  # noqa: F401,E501
from swagger_server import util


class PAResponse(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, worked=None, result=None, used_nfvi_pops=None, used_l_ls=None, used_v_ls=None, total_latency=None, total_cost=None):  # noqa: E501
        """PAResponse - a model defined in Swagger

        :param worked: The worked of this PAResponse.  # noqa: E501
        :type worked: bool
        :param result: The result of this PAResponse.  # noqa: E501
        :type result: str
        :param used_nfvi_pops: The used_nfvi_pops of this PAResponse.  # noqa: E501
        :type used_nfvi_pops: List[PAResponseUsedNFVIPops]
        :param used_l_ls: The used_l_ls of this PAResponse.  # noqa: E501
        :type used_l_ls: List[PAResponseUsedLLs]
        :param used_v_ls: The used_v_ls of this PAResponse.  # noqa: E501
        :type used_v_ls: List[PAResponseUsedVLs]
        :param total_latency: The total_latency of this PAResponse.  # noqa: E501
        :type total_latency: float
        :param total_cost: The total_cost of this PAResponse.  # noqa: E501
        :type total_cost: float
        """
        self.swagger_types = {
            'worked': bool,
            'result': str,
            'used_nfvi_pops': List[PAResponseUsedNFVIPops],
            'used_l_ls': List[PAResponseUsedLLs],
            'used_v_ls': List[PAResponseUsedVLs],
            'total_latency': float,
            'total_cost': float
        }

        self.attribute_map = {
            'worked': 'worked',
            'result': 'result',
            'used_nfvi_pops': 'usedNFVIPops',
            'used_l_ls': 'usedLLs',
            'used_v_ls': 'usedVLs',
            'total_latency': 'totalLatency',
            'total_cost': 'totalCost'
        }

        self._worked = worked
        self._result = result
        self._used_nfvi_pops = used_nfvi_pops
        self._used_l_ls = used_l_ls
        self._used_v_ls = used_v_ls
        self._total_latency = total_latency
        self._total_cost = total_cost

    @classmethod
    def from_dict(cls, dikt):
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The PAResponse of this PAResponse.  # noqa: E501
        :rtype: PAResponse
        """
        return util.deserialize_model(dikt, cls)

    @property
    def worked(self):
        """Gets the worked of this PAResponse.

        Specifies if the PA worked and found a solution  # noqa: E501

        :return: The worked of this PAResponse.
        :rtype: bool
        """
        return self._worked

    @worked.setter
    def worked(self, worked):
        """Sets the worked of this PAResponse.

        Specifies if the PA worked and found a solution  # noqa: E501

        :param worked: The worked of this PAResponse.
        :type worked: bool
        """
        if worked is None:
            raise ValueError("Invalid value for `worked`, must not be `None`")  # noqa: E501

        self._worked = worked

    @property
    def result(self):
        """Gets the result of this PAResponse.

        Description of the PA result  # noqa: E501

        :return: The result of this PAResponse.
        :rtype: str
        """
        return self._result

    @result.setter
    def result(self, result):
        """Sets the result of this PAResponse.

        Description of the PA result  # noqa: E501

        :param result: The result of this PAResponse.
        :type result: str
        """

        self._result = result

    @property
    def used_nfvi_pops(self):
        """Gets the used_nfvi_pops of this PAResponse.

        Array of all used NFVI PoPs with mapped VNFs  # noqa: E501

        :return: The used_nfvi_pops of this PAResponse.
        :rtype: List[PAResponseUsedNFVIPops]
        """
        return self._used_nfvi_pops

    @used_nfvi_pops.setter
    def used_nfvi_pops(self, used_nfvi_pops):
        """Sets the used_nfvi_pops of this PAResponse.

        Array of all used NFVI PoPs with mapped VNFs  # noqa: E501

        :param used_nfvi_pops: The used_nfvi_pops of this PAResponse.
        :type used_nfvi_pops: List[PAResponseUsedNFVIPops]
        """

        self._used_nfvi_pops = used_nfvi_pops

    @property
    def used_l_ls(self):
        """Gets the used_l_ls of this PAResponse.

        Array of all used LL between NFVIPoPs by the mapped Network Service VLs  # noqa: E501

        :return: The used_l_ls of this PAResponse.
        :rtype: List[PAResponseUsedLLs]
        """
        return self._used_l_ls

    @used_l_ls.setter
    def used_l_ls(self, used_l_ls):
        """Sets the used_l_ls of this PAResponse.

        Array of all used LL between NFVIPoPs by the mapped Network Service VLs  # noqa: E501

        :param used_l_ls: The used_l_ls of this PAResponse.
        :type used_l_ls: List[PAResponseUsedLLs]
        """

        self._used_l_ls = used_l_ls

    @property
    def used_v_ls(self):
        """Gets the used_v_ls of this PAResponse.

        Array of all used VL inside NFVIPoPs by the mapped Network Service VLs  # noqa: E501

        :return: The used_v_ls of this PAResponse.
        :rtype: List[PAResponseUsedVLs]
        """
        return self._used_v_ls

    @used_v_ls.setter
    def used_v_ls(self, used_v_ls):
        """Sets the used_v_ls of this PAResponse.

        Array of all used VL inside NFVIPoPs by the mapped Network Service VLs  # noqa: E501

        :param used_v_ls: The used_v_ls of this PAResponse.
        :type used_v_ls: List[PAResponseUsedVLs]
        """

        self._used_v_ls = used_v_ls

    @property
    def total_latency(self):
        """Gets the total_latency of this PAResponse.

        Network Sewrvice latency after placement  # noqa: E501

        :return: The total_latency of this PAResponse.
        :rtype: float
        """
        return self._total_latency

    @total_latency.setter
    def total_latency(self, total_latency):
        """Sets the total_latency of this PAResponse.

        Network Sewrvice latency after placement  # noqa: E501

        :param total_latency: The total_latency of this PAResponse.
        :type total_latency: float
        """

        self._total_latency = total_latency

    @property
    def total_cost(self):
        """Gets the total_cost of this PAResponse.

        cost of mapping the Network Service expressed in euros  # noqa: E501

        :return: The total_cost of this PAResponse.
        :rtype: float
        """
        return self._total_cost

    @total_cost.setter
    def total_cost(self, total_cost):
        """Sets the total_cost of this PAResponse.

        cost of mapping the Network Service expressed in euros  # noqa: E501

        :param total_cost: The total_cost of this PAResponse.
        :type total_cost: float
        """

        self._total_cost = total_cost
