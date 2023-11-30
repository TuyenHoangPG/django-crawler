import datetime
import json
import logging
import re
import time

from request_logging.middleware import LoggingMiddleware, DEFAULT_HTTP_4XX_LOG_LEVEL

request_logger = logging.getLogger("django.request")


class CustomLoggingMiddleware(LoggingMiddleware):
    def __call__(self, request):
        start_time = time.time()
        if request.body and not request.POST:
            self.cached_request_body = request.body
        elif request.body:
            self.cached_request_body = dict(request.POST)
        elif request.GET:
            self.cached_request_body = dict(request.GET)

        response = self.get_response(request)
        self._log_request(request, response)
        execute_time = f"{time.time() - start_time}s"
        self.process_response(request, response, execute_time)
        return response

    def process_response(self, request, response, execute_time):
        time = datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S.%f")
        resp_log = "{} {} {} - {}".format(
            time, execute_time, request.get_full_path(), response.status_code
        )
        skip_logging, because = self._should_log_route(request)
        if skip_logging:
            if because is not None:
                self.logger.log_error(
                    logging.INFO,
                    resp_log,
                    {"args": {}, "kwargs": {"extra": {"no_logging": because}}},
                )
            return response
        logging_context = self._get_logging_context(request, response)

        if response.status_code in range(400, 500):
            if self.http_4xx_log_level == DEFAULT_HTTP_4XX_LOG_LEVEL:
                # default, log as per 5xx
                self.logger.log_error(logging.INFO, resp_log, logging_context)
                self._log_resp(logging.ERROR, response, logging_context)
            else:
                self.logger.log(self.http_4xx_log_level, resp_log, logging_context)
                self._log_resp(self.log_level, response, logging_context)
        elif response.status_code in range(500, 600):
            self.logger.log_error(logging.INFO, resp_log, logging_context)
            self._log_resp(logging.ERROR, response, logging_context)
        else:
            self.logger.log(logging.INFO, resp_log, logging_context)
            self._log_resp(self.log_level, response, logging_context)

        return response

    def _log_request(self, request, response):
        time = datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S.%f")
        method_path = "{} {} {}".format(time, request.method, request.get_full_path())
        logging_context = self._get_logging_context(request, None)

        # Determine log level depending on response status
        log_level = self.log_level
        if response is not None:
            if response.status_code in range(400, 500):
                log_level = self.http_4xx_log_level
            elif response.status_code in range(500, 600):
                log_level = logging.ERROR

        self.logger.log(logging.INFO, method_path, logging_context)
        self._log_request_body(request, logging_context, log_level)

    def _log_request_body(self, request, logging_context, log_level):
        if self.cached_request_body is not None:
            content_type = request.META.get("CONTENT_TYPE", "")
            is_multipart = content_type.startswith("multipart/form-data")
            if is_multipart:
                self.boundary = (
                    "--" + content_type[30:]
                )  # First 30 characters are "multipart/form-data; boundary="
            if is_multipart:
                self._log_multipart(
                    self.cached_request_body, logging_context, log_level
                )
            else:
                self.logger.log(log_level, self.cached_request_body, logging_context)

    def _log_resp(self, level, response, logging_context):
        if re.match("^application/json", response.get("Content-Type", ""), re.I):
            if response.streaming:
                # There's a chance that if it's streaming it's because large and it might hit
                # the max_body_length very often. Not to mention that StreamingHttpResponse
                # documentation advises to iterate only once on the content.
                # So the idea here is to just _not_ log it.
                self.logger.log(level, "(data_stream)", logging_context)
            else:
                self.logger.log(level, json.loads(response.content), logging_context)
