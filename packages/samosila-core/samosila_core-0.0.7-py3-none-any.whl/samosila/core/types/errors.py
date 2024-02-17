from openai import (
    APIConnectionError as OAIAPIConnectionError,
    AuthenticationError as OAIAuthenticationError,
    BadRequestError as OAIBadRequestError,
    RateLimitError as OAIRateLimitError,
    APIStatusError as OAIAPIStatusError,
    OpenAIError as OAIOpenAIError,
    APIError as OAIAPIError,
    APITimeoutError as OAIAPITimeoutError,
    APIResponseValidationError as OAIAPIResponseValidationError
)
import httpx


class AuthenticationError(OAIAuthenticationError):  # type: ignore
    def __init__(self, message, llm_provider, model, response: httpx.Response):
        self.status_code = 401
        self.message = message
        self.llm_provider = llm_provider
        self.model = model
        super().__init__(
            self.message,
            response=response,
            body=None
        )  # Call the base class constructor with the parameters it needs


class BadRequestError(OAIBadRequestError):  # type: ignore
    def __init__(self, message, model, llm_provider, response: httpx.Response):
        self.status_code = 400
        self.message = message
        self.model = model
        self.llm_provider = llm_provider
        super().__init__(
            self.message,
            response=response,
            body=None
        )  # Call the base class constructor with the parameters it needs


class Timeout(OAIAPITimeoutError):  # type: ignore
    def __init__(self, message, model, llm_provider):
        self.status_code = 408
        self.message = message
        self.model = model
        self.llm_provider = llm_provider
        request = httpx.Request(method="POST", url="https://api.openai.com/v1")
        super().__init__(
            request=request
        )  # Call the base class constructor with the parameters it needs


class RateLimitError(OAIRateLimitError):  # type: ignore
    def __init__(self, message, llm_provider, model, response: httpx.Response):
        self.status_code = 429
        self.message = message
        self.llm_provider = llm_provider
        self.modle = model
        super().__init__(
            self.message,
            response=response,
            body=None
        )  


class ContextWindowExceededError(OAIBadRequestError):
    def __init__(self, message, model, llm_provider, response: httpx.Response):
        self.status_code = 400
        self.message = message
        self.model = model
        self.llm_provider = llm_provider
        super().__init__(
            message=self.message,
            model=self.model,  # type: ignore
            llm_provider=self.llm_provider,  # type: ignore
            response=response
        )

class ServiceUnavailableError(OAIAPIStatusError):  # type: ignore
    def __init__(self, message, llm_provider, model, response: httpx.Response):
        self.status_code = 503
        self.message = message
        self.llm_provider = llm_provider
        self.model = model
        super().__init__(
            self.message,
            response=response,
            body=None
        )  # Call the base class constructor with the parameters it needs


class APIError(OAIAPIError):
    def __init__(self, status_code, message, llm_provider, model, request: httpx.Request):
        self.status_code = status_code
        self.message = message
        self.llm_provider = llm_provider
        self.model = model
        super().__init__(
            self.message,
            request=request,  # type: ignore
            body=None
        )

# raised if an invalid request (not get, delete, put, post) is made


class APIConnectionError(OAIAPIConnectionError): 
  def __init__(self, message, llm_provider, model, request: httpx.Request):
        self.message = message
        self.llm_provider = llm_provider
        self.model = model
        self.status_code = 500
        super().__init__(
            message=self.message,
            request=request
        )

# raised if an invalid request (not get, delete, put, post) is made


class APIResponseValidationError(OAIAPIResponseValidationError):  
    def __init__(self, message, llm_provider, model):
        self.message = message
        self.llm_provider = llm_provider
        self.model = model
        request = httpx.Request(method="POST", url="https://api.openai.com/v1")
        response = httpx.Response(status_code=500, request=request)
        super().__init__(
            response=response,
            body=None,
            message=message
        )


class OpenAIError(OAIOpenAIError):  
    def __init__(self, original_exception):
        self.status_code = original_exception.http_status
        super().__init__(
            http_body=original_exception.http_body, # type: ignore
            http_status=original_exception.http_status, # type: ignore
            json_body=original_exception.json_body, # type: ignore
            headers=original_exception.headers, # type: ignore
            code=original_exception.code, # type: ignore
        )
        self.llm_provider = "openai"


class BudgetExceededError(Exception):
    def __init__(self, current_cost, max_budget):
        self.current_cost = current_cost
        self.max_budget = max_budget
        message = f"Budget has been exceeded! Current cost: {current_cost}, Max budget: {max_budget}"
        super().__init__(message)


class UnsupportedParamsError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(
            self.message
        )  # Call the base class constructor with the parameters it needs
