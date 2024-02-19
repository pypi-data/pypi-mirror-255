#file to wrap the original openai library to log the requests to our service before sending them to openai
from openai import OpenAI as OldOpenAI
from openai import AsyncOpenAI as OldAsyncOpenAI
from openai.resources import Chat as OldChat
from openai.resources.chat.completions import Completions as OldCompletions
from openai.resources.chat.completions import AsyncCompletions as OldAsyncCompletions
from .core_client.client import GigaMlApi
from typing import Union, Mapping, Optional, Dict 

import httpx, time, json

from openai._base_client import DEFAULT_MAX_RETRIES 
from openai import OpenAIError, Timeout
from openai._compat import cached_property
from openai._types import NotGiven, NOT_GIVEN
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai._streaming import Stream, AsyncStream
from openai.resources.files import Files as OldFiles
from openai.resources.files import AsyncFiles as OldAsyncFiles
from openai.resources.fine_tuning import FineTuning as OldFineTuning
from openai.resources.fine_tuning.jobs import Jobs as OldJobs
from openai.resources.fine_tuning import AsyncFineTuning as OldAsyncFineTuning
from openai.resources.fine_tuning.jobs import AsyncJobs as OldAsyncJobs
from openai.pagination import SyncPage, AsyncPage
from openai.types.fine_tuning import FineTuningJob
from openai.types import FileObject

from .utils import merge_openai_chunks

class NewCompletions(OldCompletions):
    def __init__(
        self, 
        client: OldOpenAI,
        gigaml_logger: Optional[GigaMlApi] = None,
        gigaml_inference_client: Optional[OldOpenAI] = None,
    ) -> None:
        super().__init__(client)
        self.gigaml_logger = gigaml_logger
        self.gigaml_inference_client = gigaml_inference_client

    def create(
        self, *args, **kwargs
    ) -> Union[ChatCompletion, Stream[ChatCompletionChunk]]:
        #extra support for logging the requests here 
        
        request_creation_time = int(time.time()*1000)
        model = kwargs.get("model")
        tags = kwargs.pop("tags", [])
        logging = kwargs.pop("logging", True)

        if model.startswith("gigaml:") and self.gigaml_inference_client is not None:
            #extra handling for gigaml models - send the request to gigaml models, send the tags through extra headers 
            extra_headers = {"tags": json.dumps(tags), "logging": str(logging)}

            #logging is automatically taken care of in the backend of the inference server
            return self.gigaml_inference_client.chat.completions.create(*args, **kwargs, extra_headers = extra_headers)

        if self.gigaml_logger is None or not logging:
            #return the regular completions - do not log if logging is none
            return super().create(*args, **kwargs)
        chat_completion = super().create(*args, **kwargs)

        if isinstance(chat_completion, Stream):
            #extra handling to do here for streaming 
            def generate():
                assembled_completion = None 
                for chunk in chat_completion:
                    assembled_completion = merge_openai_chunks(assembled_completion, chunk)
                    yield chunk

                total_request_time = int(time.time()*1000) - request_creation_time
                self.gigaml_logger.log(
                    request_creation_time = request_creation_time,
                    request_payload = kwargs,
                    response_payload = assembled_completion.model_dump(),
                    total_request_time=total_request_time,
                    tags = tags,
                    response_status = 200,
                ) 

            return generate()
        else:
            #normal response from the OpenAI API 
            total_request_time = int(time.time()*1000) - request_creation_time
            self.gigaml_logger.log( 
                request_creation_time = request_creation_time,
                request_payload = kwargs,
                response_payload = chat_completion.model_dump(),
                total_request_time = total_request_time,
                tags = tags,
                response_status = 200,
            )
            return chat_completion

class NewChat(OldChat):
    #wrapper over the original Chat class to log the requests
    def __init__(
        self,
        client: OldOpenAI,
        gigaml_logger: Optional[GigaMlApi] = None,
        gigaml_inference_client: Optional[OldOpenAI] = None,
    ) -> None:
        super().__init__(client)
        self.gigaml_logger = gigaml_logger
        self.gigaml_inference_client = gigaml_inference_client

    @cached_property
    def completions(self):
        return NewCompletions(self._client, gigaml_logger = self.gigaml_logger, gigaml_inference_client = self.gigaml_inference_client)

class NewFile(OldFiles):
    #wrapper over the original Files class to redirect to gigaml when needed 
    def __init__(
        self,
        client: OldOpenAI,
        gigaml_api_client: Optional[OldOpenAI] = None,
    ) -> None:
        super().__init__(client)
        self.gigaml_api_client = gigaml_api_client
    
    #modify the create property to redirect to gigaml when needed
    def create(
        self, *args, **kwargs
    ) -> FileObject:
        #extra support for logging the requests here 
        use_gigaml = kwargs.pop("use_gigaml", False)
        if use_gigaml:
            #send the request to gigaml
            return self.gigaml_api_client.files.create(*args, **kwargs)
        
        #use original openai client
        return super().create(*args, **kwargs)
    
    #similar function for list
    def list(
        self, *args, **kwargs
    ) -> SyncPage[FileObject]:
        #extra support for logging the requests here 
        use_gigaml = kwargs.pop("use_gigaml", False)
        if use_gigaml:
            #send the request to gigaml
            return self.gigaml_api_client.files.list(*args, **kwargs)
        
        #use original openai client
        return super().list(*args, **kwargs)
    
class NewJobs(OldJobs):
    def __init__(
        self,
        client: OldOpenAI,
        gigaml_api_client: Optional[OldOpenAI] = None,
    ) -> None:
        super().__init__(client)
        self.gigaml_api_client = gigaml_api_client

    #overload the create property to redirect to gigaml when needed
    def create(
        self, *args, **kwargs
    ) -> FineTuningJob:
        #extra support for logging the requests here 
        use_gigaml = kwargs.pop("use_gigaml", False)
        if use_gigaml:
            #send the request to gigaml
            return self.gigaml_api_client.fine_tuning.jobs.create(*args, **kwargs)
        
        #use original openai client
        return super().create(*args, **kwargs)
    
#finetuning class wrapper 
class NewFineTuning(OldFineTuning):
    def __init__(
        self,
        client: OldOpenAI,
        gigaml_api_client: Optional[OldOpenAI] = None,
    ) -> None:
        super().__init__(client)
        self.gigaml_api_client = gigaml_api_client
    
    @cached_property
    def jobs(self):
        return NewJobs(self._client, gigaml_api_client = self.gigaml_api_client)
    

#sync openai client 
class SyncOpenAIWrapper(OldOpenAI):
    #wrapper over the original OpenAI to log the requests 
    def __init__(
        self,
        *,
        api_key: str | None = None,
        organization: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client. See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
        gigaml_client: Optional[GigaMlApi] = None,
    ) -> None:
        super().__init__(
            api_key = api_key,
            organization = organization,
            base_url = base_url,
            timeout = timeout,
            max_retries = max_retries,
            default_headers = default_headers,
            default_query = default_query,
            http_client = http_client,
            _strict_response_validation = _strict_response_validation,
        )
        self.gigaml_logger = gigaml_client
        self.gigaml_api_client = OldOpenAI(
            api_key = gigaml_client._client_wrapper._get_token(),
            organization = organization,
            base_url = gigaml_client._client_wrapper.get_base_url()+"/v1",
            timeout = timeout,
            max_retries = max_retries,
            default_headers = default_headers,
            default_query = default_query,
            http_client = http_client,
            _strict_response_validation = _strict_response_validation,
        ) if gigaml_client is not None else None
        self.gigaml_inference_client = OldOpenAI(
            api_key = gigaml_client._client_wrapper._get_token(),
            organization = organization,
            base_url = "https://inference.gigaml.com"+"/v1",
            timeout = timeout,
            max_retries = max_retries,
            default_headers = default_headers,
            default_query = default_query,
            http_client = http_client,
            _strict_response_validation = _strict_response_validation,
        ) if gigaml_client is not None else None
        self.chat = NewChat(self, gigaml_logger = self.gigaml_logger, gigaml_inference_client = self.gigaml_inference_client)
        self.files = NewFile(self, gigaml_api_client = self.gigaml_api_client)
        self.fine_tuning = NewFineTuning(self, gigaml_api_client = self.gigaml_api_client)

#Async parts 
class NewAsyncCompletions(OldAsyncCompletions):
    def __init__(
        self, 
        client: OldAsyncOpenAI,
        gigaml_logger: Optional[GigaMlApi] = None,
        gigaml_inference_client: Optional[OldAsyncOpenAI] = None,
    ) -> None:
        super().__init__(client)
        self.gigaml_logger = gigaml_logger
        self.gigaml_inference_client = gigaml_inference_client

    async def create(
        self, *args, **kwargs
    ) -> Union[ChatCompletion, AsyncStream[ChatCompletionChunk]]:

        #handle various instances 
        request_creation_time = int(time.time()*1000)
        model = kwargs.get("model")
        tags = kwargs.pop("tags", {})
        logging = kwargs.pop("logging", True)

        if model.startswith("gigaml:") and self.gigaml_inference_client is not None:
            #extra handling for gigaml models - send the request to gigaml models, send the tags through extra headers 
            extra_headers = {"tags": json.dumps(tags), "logging": str(logging)}

            #logging is automatically taken care of in the backend of the inference server
            return await self.gigaml_inference_client.chat.completions.create(*args, **kwargs, extra_headers = extra_headers)

        if self.gigaml_logger is None or not logging:
            #return the regular completions - do not log if user does not want to
            return await super().create(*args, **kwargs)
        chat_completion = await super().create(*args, **kwargs)

        if isinstance(chat_completion, AsyncStream):
            #extra handling for streaming 
            async def generate():
                assembled_completion = None 
                async for chunk in chat_completion:
                    assembled_completion = merge_openai_chunks(assembled_completion, chunk)
                    yield chunk

                total_request_time = int(time.time()*1000) - request_creation_time
                await self.gigaml_logger.log(
                    request_creation_time = request_creation_time,
                    request_payload = kwargs,
                    total_request_time=total_request_time,
                    tags = tags,
                    response_payload = assembled_completion.model_dump_json(),
                    response_status = 200,
                )

            return generate()
        else:
            #normal response from the OpenAI API 
            total_request_time = int(time.time()*1000) - request_creation_time
            await self.gigaml_logger.log(
                request_creation_time = request_creation_time,
                request_payload = kwargs,
                tags = tags,
                total_request_time=total_request_time,
                response_payload = chat_completion.model_dump_json(),
                response_status = 200,
            )
            return chat_completion
        
class NewAsyncChat(OldChat):
    #wrapper over the original Chat class to log the requests
    def __init__(
        self,
        client: OldAsyncOpenAI,
        gigaml_logger: Optional[GigaMlApi] = None,
        gigaml_inference_client: Optional[OldAsyncOpenAI] = None,
    ) -> None:
        super().__init__(client)
        self.gigaml_logger = gigaml_logger
        self.gigaml_inference_client = gigaml_inference_client

    @cached_property
    def completions(self):
        return NewAsyncCompletions(self._client, gigaml_logger = self.gigaml_logger, gigaml_inference_client = self.gigaml_inference_client)
    
class NewAsyncFiles(OldAsyncFiles):
    def __init__(
        self,
        client: OldAsyncOpenAI,
        gigaml_api_client: Optional[OldAsyncOpenAI] = None,
    ) -> None:
        super().__init__(client)
        self.gigaml_api_client = gigaml_api_client

    #overload the create property to redirect to gigaml when needed
    async def create(
        self, *args, **kwargs
    ) -> FileObject:
        #extra support for logging the requests here 
        use_gigaml = kwargs.pop("use_gigaml", False)
        if use_gigaml:
            #send the request to gigaml
            return await self.gigaml_api_client.files.create(*args, **kwargs)
        
        #use original openai client
        return await super().create(*args, **kwargs)
    
    #similar function for list
    async def list(
        self, *args, **kwargs
    ) -> AsyncPage[FileObject]:
        #extra support for logging the requests here 
        use_gigaml = kwargs.pop("use_gigaml", False)
        if use_gigaml:
            #send the request to gigaml
            return await self.gigaml_api_client.files.list(*args, **kwargs)
        
        #use original openai client
        return await super().list(*args, **kwargs)
    
class NewAsyncJobs(OldAsyncJobs):
    def __init__(
        self,
        client: OldAsyncOpenAI,
        gigaml_api_client: Optional[OldAsyncOpenAI] = None,
    ) -> None:
        super().__init__(client)
        self.gigaml_api_client = gigaml_api_client

    #overload the create property to redirect to gigaml when needed
    async def create(
        self, *args, **kwargs
    ) -> FineTuningJob:
        #extra support for logging the requests here 
        use_gigaml = kwargs.pop("use_gigaml", False)
        if use_gigaml:
            #send the request to gigaml
            return await self.gigaml_api_client.fine_tuning.jobs.create(*args, **kwargs)
        
        #use original openai client
        return await super().create(*args, **kwargs)
    
class NewAsyncFineTuning(OldAsyncFineTuning):
    def __init__(
        self,
        client: OldAsyncOpenAI,
        gigaml_api_client: Optional[OldAsyncOpenAI] = None,
    ) -> None:
        super().__init__(client)
        self.gigaml_api_client = gigaml_api_client
    
    @cached_property
    def jobs(self):
        return NewAsyncJobs(self._client, gigaml_api_client = self.gigaml_api_client)

class AsyncOpenAIWrapper(OldAsyncOpenAI):
    #wrapper over the original OpenAI to log the requests 
    def __init__(
        self,
        *,
        api_key: str | None = None,
        organization: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client. See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
        gigaml_client: Optional[GigaMlApi] = None,
    ) -> None:
        super().__init__(
            api_key = api_key,
            organization = organization,
            base_url = base_url,
            timeout = timeout,
            max_retries = max_retries,
            default_headers = default_headers,
            default_query = default_query,
            http_client = http_client,
            _strict_response_validation = _strict_response_validation,
        )
        self.gigaml_logger = gigaml_client
        self.gigaml_api_client = OldAsyncOpenAI(
            api_key = gigaml_client._client_wrapper._get_token(),
            organization = organization,
            base_url = gigaml_client._client_wrapper.get_base_url()+"/v1",
            timeout = timeout,
            max_retries = max_retries,
            default_headers = default_headers,
            default_query = default_query,
            http_client = http_client,
            _strict_response_validation = _strict_response_validation,
        ) if gigaml_client is not None else None
        self.gigaml_inference_client = OldAsyncOpenAI(
            api_key = gigaml_client._client_wrapper._get_token(),
            organization = organization,
            base_url = "https://inference.gigaml.com"+"/v1",
            timeout = timeout,
            max_retries = max_retries,
            default_headers = default_headers,
            default_query = default_query,
            http_client = http_client,
            _strict_response_validation = _strict_response_validation,
        ) if gigaml_client is not None else None
        self.chat = NewAsyncChat(self, gigaml_logger = self.gigaml_logger, gigaml_inference_client = self.gigaml_inference_client)
        self.files = NewAsyncFiles(self, gigaml_api_client = self.gigaml_api_client)
        self.fine_tuning = NewAsyncFineTuning(self, gigaml_api_client = self.gigaml_api_client)