"""
Contains functionality for limiting http requests made by Omnata plugins
"""
from __future__ import annotations

import datetime
import re
import threading
from email.utils import parsedate_to_datetime
from logging import getLogger
from typing import List, Literal, Optional, Dict, Tuple
import requests
from pydantic import Field, root_validator
from pydantic.json import pydantic_encoder
from .configuration import SubscriptableBaseModel

logger = getLogger(__name__)

TimeUnitType = Literal["second", "minute", "hour", "day"]

HttpMethodType = Literal[
    "GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"
]


class HttpRequestMatcher(SubscriptableBaseModel):
    """
    A class used to match an HTTP request
    """

    http_methods: List[HttpMethodType]
    url_regex: str

    @classmethod
    def match_all(cls):
        """
        A HttpRequestMatcher which will match all requests.
        """
        return cls(
            http_methods=[
                "GET",
                "HEAD",
                "POST",
                "PUT",
                "DELETE",
                "CONNECT",
                "OPTIONS",
                "TRACE",
                "PATCH",
            ],
            url_regex=".*",
        )


class ApiLimits(SubscriptableBaseModel):
    """
    Encapsulates the constraints imposed by an app's APIs
    """

    endpoint_category: str = Field(
        "All endpoints",
        description='the name of the API category (e.g. "Data loading endpoints")',
    )
    request_matchers: List[HttpRequestMatcher] = Field(
        [HttpRequestMatcher.match_all()],
        description="a list of request matchers. If None is provided, all requests will be matched",
    )
    request_rates: List[RequestRateLimit] = Field(
        None,
        description="imposes time delays between requests to stay under a defined rate limit",
    )

    def request_matches(self, method: HttpMethodType, url: str):
        """
        Given the request matchers that exist, determines whether the provided HTTP method and url is a match
        """
        for request_matcher in self.request_matchers:
            if method in request_matcher.http_methods and re.search(
                request_matcher.url_regex, url
            ):
                return True
        return False

    @classmethod
    def apply_overrides(
        cls, default_api_limits: List[ApiLimits], overridden_values: List[ApiLimits]
    ) -> List[ApiLimits]:
        """
        Takes a list of default api limits, and replaces them with any overridden values
        """
        if overridden_values is None or len(overridden_values) == 0:
            return default_api_limits
        overrides_keyed = {l.endpoint_category: l.request_rates for l in overridden_values}
        for api_limit in default_api_limits:
            if api_limit.endpoint_category in overrides_keyed.keys():
                api_limit.request_rates = overrides_keyed[api_limit.endpoint_category]
        return default_api_limits

    @classmethod
    def request_match(
        cls, all_api_limits: List[ApiLimits], method: HttpMethodType, url: str
    ) -> List[ApiLimits]:
        """
        Given a set of defined API limits, return all those that match the request
        """
        return [api_limit for api_limit in all_api_limits if api_limit.request_matches(method, url)]

    def calculate_wait(self, rate_limit_state: RateLimitState) -> datetime.datetime:
        """
        Based on the configured wait limits, given a sorted list of previous requests (newest to oldest),
        determine when the next request is allowed to occur.
        Each rate limit is a number of requests over a time window.
        Examples:
        If the rate limit is 5 requests every 10 seconds, we:
         - determine the timestamp of the 5th most recent request
         - add 10 seconds to that timestamp
        The resulting timestamp is when the next request can be made (if it's in the past, it can be done immediately)
        If multiple rate limits exist, the maximum timestamp is used (i.e. the most restrictive rate limit applies)
        """
        logger.info(
            f"calculating wait time, given previous requests as {rate_limit_state.previous_request_timestamps}"
        )
        if self.request_rates is None:
            return datetime.datetime.now(datetime.timezone.utc)
        longest_wait = datetime.datetime.now(datetime.timezone.utc)
        if (
            rate_limit_state.wait_until is not None
            and rate_limit_state.wait_until > longest_wait
        ):
            longest_wait = rate_limit_state.wait_until
        for request_rate in self.request_rates:
            print(request_rate)
            if rate_limit_state.previous_request_timestamps is not None and len(rate_limit_state.previous_request_timestamps) > 0:
                previous_request_timestamps = rate_limit_state.get_relevant_history(request_rate)
                print(f"previous_request_timestamps: {len(previous_request_timestamps)}")
                request_index = request_rate.request_count - 1
                if request_index > len(previous_request_timestamps) - 1:
                    continue # we have not yet made enough requests to hit this rate limit
                request_index = len(previous_request_timestamps) - 1
                timestamp_at_horizon = previous_request_timestamps[request_index]
                print("timestamp_at_horizon: " + str(timestamp_at_horizon))
                now = datetime.datetime.now().astimezone(datetime.timezone.utc)
                seconds_since_horizon = (timestamp_at_horizon - now).total_seconds()
                print("seconds_since_horizon: " + str(seconds_since_horizon))
                next_allowed_request = timestamp_at_horizon + datetime.timedelta(
                    seconds=request_rate.number_of_seconds()
                )
                if next_allowed_request > longest_wait:
                    longest_wait = next_allowed_request

        return longest_wait

def datetime_to_epoch_milliseconds(dt: datetime.datetime) -> int:
    return int(dt.astimezone(datetime.timezone.utc).timestamp() * 1000)

def epoch_milliseconds_to_datetime(epoch: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(epoch / 1000, tz=datetime.timezone.utc)

def datetimes_as_ints_encoder(obj):
    if isinstance(obj, datetime.datetime):
        return datetime_to_epoch_milliseconds(obj)
    return pydantic_encoder(obj)


class RateLimitState(SubscriptableBaseModel):
    """
    Encapsulates the rate limiting state of an endpoint category for a particular connection (as opposed to configuration)
    Importantly, we are very strict on all timestamps being timezone aware and UTC.
    Accuracy is critical for these calculations, so we raise errors early to ensure that we're not making mistakes.
    """

    wait_until: Optional[datetime.datetime] = Field(
        None,
        description="Providing a value here means that no requests should occur until a specific moment in the future",
    )
    previous_request_timestamps: Optional[List[datetime.datetime]] = Field(
        [],
        description="A list of timestamps where previous requests have been made, used to calculate the next request time",
    )
    _request_timestamps_lock = threading.Lock()

    # Combined root validator
    @root_validator(pre=True)
    def validate_datetime_fields(cls, values):
        # Handling wait_until
        wait_until = values.get('wait_until')
        if isinstance(wait_until, int):
            values['wait_until'] = epoch_milliseconds_to_datetime(wait_until)
        elif wait_until and isinstance(wait_until, datetime.datetime):
            if wait_until.tzinfo is None:
                raise ValueError("wait_until must be timezone aware")
            elif wait_until.tzinfo != datetime.timezone.utc:
                raise ValueError("wait_until must be timezone aware and UTC")

        # Handling previous_request_timestamps
        timestamps = values.get('previous_request_timestamps', [])
        if timestamps and isinstance(timestamps[0], int):
            values['previous_request_timestamps'] = [epoch_milliseconds_to_datetime(epoch) for epoch in timestamps]
        elif timestamps and isinstance(timestamps[0], datetime.datetime):
            if timestamps[0].tzinfo is None:
                raise ValueError("previous_request_timestamps must be timezone aware")
            elif timestamps[0].tzinfo != datetime.timezone.utc:
                raise ValueError("previous_request_timestamps must be timezone aware and UTC")
        
        return values

    def merge(self,other:RateLimitState):
        """
        Merges the other rate limit state into this one
        """
        if other.wait_until is not None and (self.wait_until is None or other.wait_until > self.wait_until):
            self.wait_until = other.wait_until
        if other.previous_request_timestamps is not None and len(other.previous_request_timestamps) > 0:
            self.previous_request_timestamps.extend(other.previous_request_timestamps)
            self.previous_request_timestamps.sort(reverse=True) # they should be sorted newest to oldest
    
    @classmethod
    def collapse(cls,state:Dict[int,Dict[str,Dict[str,RateLimitState]]],selected_sync_id:int,selected_branch_name:str) -> Tuple[Dict[str,RateLimitState],Dict[str,RateLimitState]]:
        """
        Given a dictionary of rate limit states, collapses them into a single state for all endpoints, and a single state for the selected sync_id and branch_name
        """
        result_all: Dict[str,RateLimitState] = {}
        result_this_branch: Dict[str,RateLimitState] = {}
        for sync_id in state.keys():
            for branch_name in state[sync_id].keys():
                if selected_sync_id == int(sync_id) and selected_branch_name == branch_name:
                    result_this_branch = state[sync_id][branch_name]
                for endpoint_category in state[sync_id][branch_name].keys():
                    if endpoint_category not in result_all:
                        result_all[endpoint_category] = RateLimitState()
                    result_all[endpoint_category].merge(state[sync_id][branch_name][endpoint_category])
        return (result_all,result_this_branch)

    def register_http_request(self):
        """
        Registers a request as having just occurred, for rate limiting purposes.
        You only need to use this if your HTTP requests are not automatically being
        registered, which happens if http.client.HTTPConnection is not being used.
        """
        with self._request_timestamps_lock:
            append_time = datetime.datetime.now(datetime.timezone.utc)
            if self.previous_request_timestamps is None:
                self.previous_request_timestamps = []
            self.previous_request_timestamps.insert(0, append_time)

    def prune_history(self, request_rates: List[RequestRateLimit] = None):
        """
        When we store the request history, it doesn't make sense to go back indefinitely.
        We only need the requests which fall within the longest rate limiting window

        """
        if request_rates is None:
            return
        
        longest_window_seconds = max(
            [rate.number_of_seconds() for rate in [request_rate for request_rate in request_rates]]
        )
        irrelevance_horizon = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
            seconds=longest_window_seconds
        )
        self.previous_request_timestamps = [
            ts for ts in self.previous_request_timestamps if ts > irrelevance_horizon
        ]

    def get_relevant_history(self, request_rate: RequestRateLimit = None):
        """
        Returns the previous requests which are relevant to a specific rate limiting window.
        First, we prune out timestamps which are older than the time window.
        We also only need to keep timestamps up until the request count for the rate limit.
        For example:
        - Rate limit is 10 requests per 10 seconds
        - If (somehow, for the sake of argument) there were 20 requests in the last 10 seconds, 
        we only need to keep the most recent 10 to base our calculation on
        """
        if request_rate is None:
            return self.previous_request_timestamps
        longest_window_seconds = request_rate.number_of_seconds()
        irrelevance_horizon = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
            seconds=longest_window_seconds
        )
        
        pruned = [ts for ts in self.previous_request_timestamps if ts > irrelevance_horizon]
        if len(pruned) > request_rate.request_count:
            return pruned[:request_rate.request_count]
        else:
            return pruned


class RequestRateLimit(SubscriptableBaseModel):
    """
    Request rate limits
        Defined as a request count, time unit and number of units e.g. (1,"second",5) = 1 request per 5 seconds, or (100, "minute", 15) = 100 requests per 15 minutes
    """

    request_count: int
    time_unit: TimeUnitType
    unit_count: int

    def number_of_seconds(self):
        """
        Converts the time_unit and unit_count to a number of seconds.
        E.g. 5 minutes = 300
        2 hours = 7200
        """
        if self.time_unit == "second":
            return self.unit_count
        elif self.time_unit == "minute":
            return self.unit_count * 60
        elif self.time_unit == "hour":
            return self.unit_count * 3600
        elif self.time_unit == "day":
            return self.unit_count * 86400
        else:
            raise ValueError(f"Unknown time unit: {self.time_unit}")

    def to_description(self) -> str:
        """Returns a readable description of this limit.
        For example:
        "1 request per minute"
        "5 requests per 2 seconds"

        Returns:
            str: the description as described above
        """
        return (
            str(self.request_count)
            + " "
            + "request"
            + ("s" if self.request_count > 1 else "")
            + " per "
            + (
                self.time_unit
                if self.unit_count == 1
                else f"{self.unit_count} {self.time_unit}s"
            )
        )


class RetryLaterException(Exception):
    """
    Exception raised when the app has notified that rate limits are exceeded.
    Throwing this during record apply imposes a temporary extra API constraint that
    we need to wait until a future date before more requests are made.

    """

    def __init__(self, future_datetime: datetime.datetime):
        self.future_datetime = future_datetime
        message = "Remote system wants us to retry later"
        self.message = message
        super().__init__(self.message)


class InterruptedWhileWaitingException(Exception):
    """
    Indicates that while waiting for rate limiting to expire, the sync was interrupted
    """
    def __init__(self):
        message = "The sync was interrupted while waiting"
        self.message = message
        super().__init__(self.message)

def too_many_requests_hook(
    fallback_future_datetime: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
    + datetime.timedelta(hours=24),
):
    """
    A Requests hook which raises a RetryLaterException if an HTTP 429 response is returned.
    Examines the Retry-After header (https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Retry-After)
    to determine the appropriate future datetime to retry.
    If that isn't available, it falls back to fallback_future_datetime.

    """

    def hook(resp: requests.Response, *args, **kwargs):
        """
        The actual hook implementation
        """
        if resp.status_code == 429:
            if "Retry-After" in resp.headers:
                retry_after: str = resp.headers["Retry-After"]
                if retry_after.isnumeric():
                    raise RetryLaterException(
                        future_datetime=datetime.datetime.now(datetime.timezone.utc)
                        + datetime.timedelta(seconds=int(retry_after))
                    )
                retry_date = parsedate_to_datetime(retry_after)
                raise RetryLaterException(future_datetime=retry_date)
            raise RetryLaterException(future_datetime=fallback_future_datetime)

    return hook


ApiLimits.update_forward_refs()
