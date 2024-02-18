# The MIT License (MIT)
# Copyright © 2024 Nimble Labs Ltd

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from __future__ import annotations

import asyncio
import uuid
import time
import torch
import aiohttp
import nimlib
from fastapi import Response
from typing import Union, Optional, List, Union, AsyncGenerator, Any


class boson(torch.nn.Module):
    """
    The Boson class, inheriting from PyTorch's Module class, represents the abstracted
    implementation of a network client module. In the brain analogy, bosons receive signals
    from other particles (in this case, network servers or fermions), and the Boson class here is designed
    to send requests to those endpoint to recieve inputs.

    This class includes a wallet or keypair used for signing messages, and methods for making
    HTTP requests to the network servers. It also provides functionalities such as logging
    network requests and processing server responses.

    Attributes:
        keypair: The wallet or keypair used for signing messages.
        external_ip (str): The external IP address of the local system.
        nucleon_history (list): A list of Nucleon objects representing the historical responses.

    Methods:
        __str__(): Returns a string representation of the Boson object.
        __repr__(): Returns a string representation of the Boson object, acting as a fallback
                    for __str__().
        query(self, *args, **kwargs) -> Union[nimlib.Nucleon, List[nimlib.Nucleon]]:
            Makes synchronous requests to one or multiple target Fermions and returns responses.

        forward(self, fermions, nucleon=nimlib.Nucleon(), timeout=12, deserialize=True, run_async=True, streaming=False) -> nimlib.Nucleon:
            Asynchronously sends requests to one or multiple Fermions and collates their responses.

        call(self, target_fermion, nucleon=nimlib.Nucleon(), timeout=12.0, deserialize=True) -> nimlib.Nucleon:
            Asynchronously sends a request to a specified Fermion and processes the response.

        call_stream(self, target_fermion, nucleon=nimlib.Nucleon(), timeout=12.0, deserialize=True) -> AsyncGenerator[nimlib.Nucleon, None]:
            Sends a request to a specified Fermion and yields an AsyncGenerator that contains streaming
            response chunks before finally yielding the filled Nucleon as the final element.

        preprocess_nucleon_for_request(self, target_fermion_info, nucleon, timeout=12.0) -> nimlib.Nucleon:
            Preprocesses the nucleon for making a request, including building headers and signing.

        process_server_response(self, server_response, json_response, local_nucleon):
            Processes the server response, updates the local nucleon state, and merges headers.

        close_session(self):
            Synchronously closes the internal aiohttp client session.

        aclose_session(self):
            Asynchronously closes the internal aiohttp client session.

    NOTE: When working with async aiohttp client sessions, it is recommended to use a context manager.

    Example with a context manager:
        >>> aysnc with boson(wallet = nimlib.wallet()) as d:
        >>>     print(d)
        >>>     d( <fermion> ) # ping fermion
        >>>     d( [<fermions>] ) # ping multiple
        >>>     d( nimlib.fermion(), nimlib.Nucleon )

    However, you are able to safely call boson.query() without a context manager in a synchronous setting.

    Example without a context manager:
        >>> d = boson(wallet = nimlib.wallet() )
        >>> print(d)
        >>> d( <fermion> ) # ping fermion
        >>> d( [<fermions>] ) # ping multiple
        >>> d( nimlib.fermion(), nimlib.Nucleon )
    """

    def __init__(
        self, wallet: Optional[Union[nimlib.wallet, nimlib.keypair]] = None
    ):
        """
        Initializes the Boson object, setting up essential properties.

        Args:
            wallet (Optional[Union['nimlib.wallet', 'nimlib.keypair']], optional):
                The user's wallet or keypair used for signing messages. Defaults to None,
                in which case a new nimlib.wallet().hotkey is generated and used.
        """
        # Initialize the parent class
        super(boson, self).__init__()

        # Unique identifier for the instance
        self.uuid = str(uuid.uuid1())

        # Get the external IP
        self.external_ip = nimlib.utils.networking.get_external_ip()

        # If a wallet or keypair is provided, use its hotkey. If not, generate a new one.
        self.keypair = (
            wallet.hotkey if isinstance(wallet, nimlib.wallet) else wallet
        ) or nimlib.wallet().hotkey

        self.nucleon_history: list = []

        self._session: aiohttp.ClientSession = None

    @property
    async def session(self) -> aiohttp.ClientSession:
        """
        An asynchronous property that provides access to the internal aiohttp client session.

        This property ensures the management of HTTP connections in an efficient way. It lazily
        initializes the aiohttp.ClientSession on its first use. The session is then reused for subsequent
        HTTP requests, offering performance benefits by reusing underlying connections.

        This is used internally by the boson when querying fermions, and should not be used directly
        unless absolutely necessary for your application.

        Returns:
            aiohttp.ClientSession: The active aiohttp client session instance. If no session exists, a
            new one is created and returned. This session is used for asynchronous HTTP requests within
            the boson, adhering to the async nature of the network interactions in the nimble framework.

        Example usage:
            import nimble as nb                    # Import nimble
            wallet = nb.wallet( ... )                 # Initialize a wallet
            boson = nb.boson( wallet )          # Initialize a boson instance with the wallet

            async with (await boson.session).post( # Use the session to make an HTTP POST request
                url,                                  # URL to send the request to
                headers={...},                        # Headers dict to be sent with the request
                json={...},                           # JSON body data to be sent with the request
                timeout=10,                           # Timeout duration in seconds
            ) as response:
                json_response = await response.json() # Extract the JSON response from the server

        """
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    def close_session(self):
        """
        Closes the internal aiohttp client session synchronously.

        This method ensures the proper closure and cleanup of the aiohttp client session, releasing any
        resources like open connections and internal buffers. It is crucial for preventing resource leakage
        and should be called when the boson instance is no longer in use, especially in synchronous contexts.

        Note: This method utilizes asyncio's event loop to close the session asynchronously from a synchronous
        context. It is advisable to use this method only when asynchronous context management is not feasible.

        Usage:
            # When finished with boson in a synchronous context
            boson_instance.close_session()
        """
        if self._session:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._session.close())
            self._session = None

    async def aclose_session(self):
        """
        Asynchronously closes the internal aiohttp client session.

        This method is the asynchronous counterpart to the `close_session` method. It should be used in
        asynchronous contexts to ensure that the aiohttp client session is closed properly. The method
        releases resources associated with the session, such as open connections and internal buffers,
        which is essential for resource management in asynchronous applications.

        Usage:
            # When finished with boson in an asynchronous context
            await boson_instance.aclose_session()

        Example:
            async with boson_instance:
                # Operations using boson
                pass
            # The session will be closed automatically after the above block
        """
        if self._session:
            await self._session.close()
            self._session = None

    def _get_endpoint_url(self, target_fermion, request_name):
        """
        Constructs the endpoint URL for a network request to a target fermion.

        This internal method generates the full HTTP URL for sending a request to the specified fermion. The
        URL includes the IP address and port of the target fermion, along with the specific request name. It
        differentiates between requests to the local system (using '0.0.0.0') and external systems.

        Args:
            target_fermion: The target fermion object containing IP and port information.
            request_name: The specific name of the request being made.

        Returns:
            str: A string representing the complete HTTP URL for the request.
        """
        endpoint = (
            f"0.0.0.0:{str(target_fermion.port)}"
            if target_fermion.ip == str(self.external_ip)
            else f"{target_fermion.ip}:{str(target_fermion.port)}"
        )
        return f"http://{endpoint}/{request_name}"

    def _handle_request_errors(self, nucleon, request_name, exception):
        """
        Handles exceptions that occur during network requests, updating the nucleon with appropriate status
        codes and messages.

        This method interprets different types of exceptions and sets the corresponding status code and
        message in the nucleon object. It covers common network errors such as connection issues and timeouts.

        Args:
            nucleon: The nucleon object associated with the request.
            request_name: The name of the request during which the exception occurred.
            exception: The exception object caught during the request.

        Note: This method updates the nucleon object in-place.
        """
        if isinstance(exception, aiohttp.ClientConnectorError):
            nucleon.boson.status_code = "503"
            nucleon.boson.status_message = f"Service at {nucleon.fermion.ip}:{str(nucleon.fermion.port)}/{request_name} unavailable."
        elif isinstance(exception, asyncio.TimeoutError):
            nucleon.boson.status_code = "408"
            nucleon.boson.status_message = (
                f"Timedout after {nucleon.timeout} seconds."
            )
        else:
            nucleon.boson.status_code = "422"
            nucleon.boson.status_message = (
                f"Failed to parse response object with error: {str(exception)}"
            )

    def _log_outgoing_request(self, nucleon):
        """
        Logs information about outgoing requests for debugging purposes.

        This internal method logs key details about each outgoing request, including the size of the
        request, the name of the nucleon, the fermion's details, and a success indicator. This information
        is crucial for monitoring and debugging network activity within the nimble network.

        To turn on debug messages, set the environment variable nimble_DEBUG to 1. or call the nimble
        debug method like so:
        ```python
        import nimble
        nimlib.debug()
        ```

        Args:
            nucleon: The nucleon object representing the request being sent.
        """
        nimlib.logging.debug(
            f"boson | --> | {nucleon.get_total_size()} B | {nucleon.name} | {nucleon.fermion.hotkey} | {nucleon.fermion.ip}:{str(nucleon.fermion.port)} | 0 | Success"
        )

    def _log_incoming_response(self, nucleon):
        """
        Logs information about incoming responses for debugging and monitoring.

        Similar to `_log_outgoing_request`, this method logs essential details of the incoming responses,
        including the size of the response, nucleon name, fermion details, status code, and status message.
        This logging is vital for troubleshooting and understanding the network interactions in nimble.

        Args:
            nucleon: The nucleon object representing the received response.
        """
        nimlib.logging.debug(
            f"boson | <-- | {nucleon.get_total_size()} B | {nucleon.name} | {nucleon.fermion.hotkey} | {nucleon.fermion.ip}:{str(nucleon.fermion.port)} | {nucleon.boson.status_code} | {nucleon.boson.status_message}"
        )

    def query(
        self, *args, **kwargs
    ) -> Union[
        nimlib.Nucleon,
        List[nimlib.Nucleon],
        nimlib.StreamingNucleon,
        List[nimlib.StreamingNucleon],
    ]:
        """
        Makes a synchronous request to multiple target Fermions and returns the server responses.

        Cleanup is automatically handled and sessions are closed upon completed requests.

        Args:
            fermions (Union[List[Union['nimlib.FermionInfo', 'nimlib.fermion']], Union['nimlib.FermionInfo', 'nimlib.fermion']]):
                The list of target Fermion information.
            nucleon (nimlib.Nucleon, optional): The Nucleon object. Defaults to nimlib.Nucleon().
            timeout (float, optional): The request timeout duration in seconds.
                Defaults to 12.0 seconds.
        Returns:
            Union[nimlib.Nucleon, List[nimlib.Nucleon]]: If a single target fermion is provided,
                returns the response from that fermion. If multiple target fermions are provided,
                returns a list of responses from all target fermions.
        """
        result = None
        try:
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(self.forward(*args, **kwargs))
        except:
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            result = loop.run_until_complete(self.forward(*args, **kwargs))
            new_loop.close()
        finally:
            self.close_session()
            return result

    async def forward(
        self,
        fermions: Union[
            List[Union[nimlib.FermionInfo, nimlib.fermion]],
            Union[nimlib.FermionInfo, nimlib.fermion],
        ],
        nucleon: nimlib.Nucleon = nimlib.Nucleon(),
        timeout: float = 12,
        deserialize: bool = True,
        run_async: bool = True,
        streaming: bool = False,
    ) -> List[
        Union[AsyncGenerator[Any], nimlib.Nucleon, nimlib.StreamingNucleon]
    ]:
        """
        Asynchronously sends requests to one or multiple Fermions and collates their responses.

        This function acts as a bridge for sending multiple requests concurrently or sequentially
        based on the provided parameters. It checks the type of the target Fermions, preprocesses
        the requests, and then sends them off. After getting the responses, it processes and
        collates them into a unified format.

        When querying an Fermion that sends a single response, this function returns a Nucleon object
        containing the response data. If multiple Fermions are queried, a list of Nucleon objects is
        returned, each containing the response from the corresponding Fermion.

        For example:
            >>> ...
            >>> wallet = nimlib.wallet()                   # Initialize a wallet
            >>> nucleon = nimlib.Nucleon(...)              # Create a nucleon object that contains query data
            >>> dendrte = nimlib.boson(wallet = wallet) # Initialize a boson instance
            >>> fermions = megastring.fermions                       # Create a list of fermions to query
            >>> responses = await boson(fermions, nucleon)    # Send the query to all fermions and await the responses

        When querying an Fermion that sends back data in chunks using the Boson, this function
        returns an AsyncGenerator that yields each chunk as it is received. The generator can be
        iterated over to process each chunk individually.

        For example:
            >>> ...
            >>> dendrte = nimlib.boson(wallet = wallet)
            >>> async for chunk in boson.forward(fermions, nucleon, timeout, deserialize, run_async, streaming):
            >>>     # Process each chunk here
            >>>     print(chunk)

        Args:
            fermions (Union[List[Union['nimlib.FermionInfo', 'nimlib.fermion']], Union['nimlib.FermionInfo', 'nimlib.fermion']]):
                The target Fermions to send requests to. Can be a single Fermion or a list of Fermions.
            nucleon (nimlib.Nucleon, optional): The Nucleon object encapsulating the data. Defaults to a new nimlib.Nucleon instance.
            timeout (float, optional): Maximum duration to wait for a response from an Fermion in seconds. Defaults to 12.0.
            deserialize (bool, optional): Determines if the received response should be deserialized. Defaults to True.
            run_async (bool, optional): If True, sends requests concurrently. Otherwise, sends requests sequentially. Defaults to True.
            streaming (bool, optional): Indicates if the response is expected to be in streaming format. Defaults to False.

        Returns:
            Union[AsyncGenerator, nimlib.Nucleon, List[nimlib.Nucleon]]: If a single Fermion is targeted, returns its response.
            If multiple Fermions are targeted, returns a list of their responses.
        """
        is_list = True
        # If a single fermion is provided, wrap it in a list for uniform processing
        if not isinstance(fermions, list):
            is_list = False
            fermions = [fermions]

        # Check if nucleon is an instance of the StreamingNucleon class or if streaming flag is set.
        is_streaming_subclass = issubclass(
            nucleon.__class__, nimlib.StreamingNucleon
        )
        if streaming != is_streaming_subclass:
            nimlib.logging.warning(
                f"Argument streaming is {streaming} while issubclass(nucleon, StreamingNucleon) is {nucleon.__class__.__name__}. This may cause unexpected behavior."
            )
        streaming = is_streaming_subclass or streaming

        async def query_all_fermions(
            is_stream: bool,
        ) -> Union[
            AsyncGenerator[Any], nimlib.Nucleon, nimlib.StreamingNucleon
        ]:
            """
            Handles the processing of requests to all targeted fermions, accommodating both streaming and
            non-streaming responses.

            This function manages the concurrent or sequential dispatch of requests to a list of fermions.
            It utilizes the `is_stream` parameter to determine the mode of response handling (streaming
            or non-streaming). For each fermion, it calls 'single_fermion_response' and aggregates the responses.

            Args:
                is_stream (bool): Flag indicating whether the fermion responses are expected to be streamed.
                If True, responses are handled in streaming mode.

            Returns:
                List[Union[AsyncGenerator, nimlib.Nucleon, nimlib.StreamingNucleon]]: A list
                containing the responses from each fermion. The type of each response depends on the
                streaming mode and the type of nucleon used.
            """

            async def single_fermion_response(
                target_fermion,
            ) -> Union[
                AsyncGenerator[Any], nimlib.Nucleon, nimlib.StreamingNucleon
            ]:
                """
                Manages the request and response process for a single fermion, supporting both streaming and
                non-streaming modes.

                This function is responsible for initiating a request to a single fermion. Depending on the
                'is_stream' flag, it either uses 'call_stream' for streaming responses or 'call' for
                standard responses. The function handles the response processing, catering to the specifics
                of streaming or non-streaming data.

                Args:
                    target_fermion: The target fermion object to which the request is to be sent. This object
                    contains the necessary information like IP address and port to formulate the request.

                Returns:
                    Union[AsyncGenerator, nimlib.Nucleon, nimlib.StreamingNucleon]: The response
                    from the targeted fermion. In streaming mode, an AsyncGenerator is returned, yielding
                    data chunks. In non-streaming mode, a Nucleon or StreamingNucleon object is returned
                    containing the response.
                """
                if is_stream:
                    # If in streaming mode, return the async_generator
                    return self.call_stream(
                        target_fermion=target_fermion,
                        nucleon=nucleon.copy(),
                        timeout=timeout,
                        deserialize=deserialize,
                    )
                else:
                    # If not in streaming mode, simply call the fermion and get the response.
                    return await self.call(
                        target_fermion=target_fermion,
                        nucleon=nucleon.copy(),
                        timeout=timeout,
                        deserialize=deserialize,
                    )

            # If run_async flag is False, get responses one by one.
            if not run_async:
                return [
                    await single_fermion_response(target_fermion)
                    for target_fermion in fermions
                ]
            # If run_async flag is True, get responses concurrently using asyncio.gather().
            return await asyncio.gather(
                *(
                    single_fermion_response(target_fermion)
                    for target_fermion in fermions
                )
            )

        # Get responses for all fermions.
        responses = await query_all_fermions(streaming)
        # Return the single response if only one fermion was targeted, else return all responses
        if len(responses) == 1 and not is_list:
            return responses[0]
        else:
            return responses

    async def call(
        self,
        target_fermion: Union[nimlib.FermionInfo, nimlib.fermion],
        nucleon: nimlib.Nucleon = nimlib.Nucleon(),
        timeout: float = 12.0,
        deserialize: bool = True,
    ) -> nimlib.Nucleon:
        """
        Asynchronously sends a request to a specified Fermion and processes the response.

        This function establishes a connection with a specified Fermion, sends the encapsulated
        data through the Nucleon object, waits for a response, processes it, and then
        returns the updated Nucleon object.

        Args:
            target_fermion (Union['nimlib.FermionInfo', 'nimlib.fermion']): The target Fermion to send the request to.
            nucleon (nimlib.Nucleon, optional): The Nucleon object encapsulating the data. Defaults to a new nimlib.Nucleon instance.
            timeout (float, optional): Maximum duration to wait for a response from the Fermion in seconds. Defaults to 12.0.
            deserialize (bool, optional): Determines if the received response should be deserialized. Defaults to True.

        Returns:
            nimlib.Nucleon: The Nucleon object, updated with the response data from the Fermion.
        """

        # Record start time
        start_time = time.time()
        target_fermion = (
            target_fermion.info()
            if isinstance(target_fermion, nimlib.fermion)
            else target_fermion
        )

        # Build request endpoint from the nucleon class
        request_name = nucleon.__class__.__name__
        url = self._get_endpoint_url(target_fermion, request_name=request_name)

        # Preprocess nucleon for making a request
        nucleon = self.preprocess_nucleon_for_request(
            target_fermion, nucleon, timeout
        )

        try:
            # Log outgoing request
            self._log_outgoing_request(nucleon)

            # Make the HTTP POST request
            async with (await self.session).post(
                url,
                headers=nucleon.to_headers(),
                json=nucleon.dict(),
                timeout=timeout,
            ) as response:
                # Extract the JSON response from the server
                json_response = await response.json()
                # Process the server response and fill nucleon
                self.process_server_response(response, json_response, nucleon)

            # Set process time and log the response
            nucleon.boson.process_time = str(time.time() - start_time)

        except Exception as e:
            self._handle_request_errors(nucleon, request_name, e)

        finally:
            self._log_incoming_response(nucleon)

            # Log nucleon event history
            self.nucleon_history.append(
                nimlib.Nucleon.from_headers(nucleon.to_headers())
            )

            # Return the updated nucleon object after deserializing if requested
            if deserialize:
                return nucleon.deserialize()
            else:
                return nucleon

    async def call_stream(
        self,
        target_fermion: Union[nimlib.FermionInfo, nimlib.fermion],
        nucleon: nimlib.Nucleon = nimlib.Nucleon(),
        timeout: float = 12.0,
        deserialize: bool = True,
    ) -> AsyncGenerator[Any]:
        """
        Sends a request to a specified Fermion and yields streaming responses.

        Similar to `call`, but designed for scenarios where the Fermion sends back data in
        multiple chunks or streams. The function yields each chunk as it is received. This is
        useful for processing large responses piece by piece without waiting for the entire
        data to be transmitted.

        Args:
            target_fermion (Union['nimlib.FermionInfo', 'nimlib.fermion']): The target Fermion to send the request to.
            nucleon (nimlib.Nucleon, optional): The Nucleon object encapsulating the data. Defaults to a new nimlib.Nucleon instance.
            timeout (float, optional): Maximum duration to wait for a response (or a chunk of the response) from the Fermion in seconds. Defaults to 12.0.
            deserialize (bool, optional): Determines if each received chunk should be deserialized. Defaults to True.

        Yields:
            object: Each yielded object contains a chunk of the arbitrary response data from the Fermion.
            nimlib.Nucleon: After the AsyncGenerator has been exhausted, yields the final filled Nucleon.
        """

        # Record start time
        start_time = time.time()
        target_fermion = (
            target_fermion.info()
            if isinstance(target_fermion, nimlib.fermion)
            else target_fermion
        )

        # Build request endpoint from the nucleon class
        request_name = nucleon.__class__.__name__
        endpoint = (
            f"0.0.0.0:{str(target_fermion.port)}"
            if target_fermion.ip == str(self.external_ip)
            else f"{target_fermion.ip}:{str(target_fermion.port)}"
        )
        url = f"http://{endpoint}/{request_name}"

        # Preprocess nucleon for making a request
        nucleon = self.preprocess_nucleon_for_request(
            target_fermion, nucleon, timeout
        )

        try:
            # Log outgoing request
            self._log_outgoing_request(nucleon)

            # Make the HTTP POST request
            async with (await self.session).post(
                url,
                headers=nucleon.to_headers(),
                json=nucleon.dict(),
                timeout=timeout,
            ) as response:
                # Use nucleon subclass' process_streaming_response method to yield the response chunks
                async for chunk in nucleon.process_streaming_response(response):
                    yield chunk  # Yield each chunk as it's processed
                json_response = nucleon.extract_response_json(response)

                # Process the server response
                self.process_server_response(response, json_response, nucleon)

            # Set process time and log the response
            nucleon.boson.process_time = str(time.time() - start_time)

        except Exception as e:
            self._handle_request_errors(nucleon, request_name, e)

        finally:
            self._log_incoming_response(nucleon)

            # Log nucleon event history
            self.nucleon_history.append(
                nimlib.Nucleon.from_headers(nucleon.to_headers())
            )

            # Return the updated nucleon object after deserializing if requested
            if deserialize:
                yield nucleon.deserialize()
            else:
                yield nucleon

    def preprocess_nucleon_for_request(
        self,
        target_fermion_info: nimlib.FermionInfo,
        nucleon: nimlib.Nucleon,
        timeout: float = 12.0,
    ) -> nimlib.Nucleon:
        """
        Preprocesses the nucleon for making a request. This includes building
        headers for Boson and Fermion and signing the request.

        Args:
            target_fermion_info (nimlib.FermionInfo): The target fermion information.
            nucleon (nimlib.Nucleon): The nucleon object to be preprocessed.
            timeout (float, optional): The request timeout duration in seconds.
                Defaults to 12.0 seconds.

        Returns:
            nimlib.Nucleon: The preprocessed nucleon.
        """
        # Set the timeout for the nucleon
        nucleon.timeout = str(timeout)

        # Build the Boson headers using the local system's details
        nucleon.boson = nimlib.TerminalInfo(
            **{
                "ip": str(self.external_ip),
                "version": str(nimlib.__version_as_int__),
                "nonce": f"{time.monotonic_ns()}",
                "uuid": str(self.uuid),
                "hotkey": str(self.keypair.ss58_address),
            }
        )

        # Build the Fermion headers using the target fermion's details
        nucleon.fermion = nimlib.TerminalInfo(
            **{
                "ip": str(target_fermion_info.ip),
                "port": str(target_fermion_info.port),
                "hotkey": str(target_fermion_info.hotkey),
            }
        )

        # Sign the request using the boson, fermion info, and the nucleon body hash
        message = f"{nucleon.boson.nonce}.{nucleon.boson.hotkey}.{nucleon.fermion.hotkey}.{nucleon.boson.uuid}.{nucleon.body_hash}"
        nucleon.boson.signature = f"0x{self.keypair.sign(message).hex()}"

        return nucleon

    def process_server_response(
        self,
        server_response: Response,
        json_response: dict,
        local_nucleon: nimlib.Nucleon,
    ):
        """
        Processes the server response, updates the local nucleon state with the
        server's state and merges headers set by the server.

        Args:
            server_response (object): The aiohttp response object from the server.
            json_response (dict): The parsed JSON response from the server.
            local_nucleon (nimlib.Nucleon): The local nucleon object to be updated.

        Raises:
            None, but errors in attribute setting are silently ignored.
        """
        # Check if the server responded with a successful status code
        if server_response.status == 200:
            # If the response is successful, overwrite local nucleon state with
            # server's state only if the protocol allows mutation. To prevent overwrites,
            # the protocol must set allow_mutation = False
            server_nucleon = local_nucleon.__class__(**json_response)
            for key in local_nucleon.dict().keys():
                try:
                    # Set the attribute in the local nucleon from the corresponding
                    # attribute in the server nucleon
                    setattr(local_nucleon, key, getattr(server_nucleon, key))
                except:
                    # Ignore errors during attribute setting
                    pass

        # Extract server headers and overwrite None values in local nucleon headers
        server_headers = nimlib.Nucleon.from_headers(server_response.headers)

        # Merge boson headers
        local_nucleon.boson.__dict__.update(
            {
                **local_nucleon.boson.dict(exclude_none=True),
                **server_headers.boson.dict(exclude_none=True),
            }
        )

        # Merge fermion headers
        local_nucleon.fermion.__dict__.update(
            {
                **local_nucleon.fermion.dict(exclude_none=True),
                **server_headers.fermion.dict(exclude_none=True),
            }
        )

        # Update the status code and status message of the boson to match the fermion
        local_nucleon.boson.status_code = local_nucleon.fermion.status_code
        local_nucleon.boson.status_message = (
            local_nucleon.fermion.status_message
        )

    def __str__(self) -> str:
        """
        Returns a string representation of the Boson object.

        Returns:
            str: The string representation of the Boson object in the format "boson(<user_wallet_address>)".
        """
        return "boson({})".format(self.keypair.ss58_address)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Boson object, acting as a fallback for __str__().

        Returns:
            str: The string representation of the Boson object in the format "boson(<user_wallet_address>)".
        """
        return self.__str__()

    async def __aenter__(self):
        """
        Asynchronous context manager entry method.

        Enables the use of the `async with` statement with the Boson instance. When entering the context,
        the current instance of the class is returned, making it accessible within the asynchronous context.

        Returns:
            Boson: The current instance of the Boson class.

        Usage:
            async with Boson() as boson:
                await boson.some_async_method()
        """
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """
        Asynchronous context manager exit method.

        Ensures proper cleanup when exiting the `async with` context. This method will close the aiohttp client session
        asynchronously, releasing any tied resources.

        Args:
            exc_type (Type[BaseException], optional): The type of exception that was raised.
            exc_value (BaseException, optional): The instance of exception that was raised.
            traceback (TracebackType, optional): A traceback object encapsulating the call stack at the point
                                                where the exception was raised.

        Usage:
            async with nb.boson( wallet ) as boson:
                await boson.some_async_method()

        Note: This automatically closes the session by calling __aexit__ after the context closes.
        """
        await self.aclose_session()

    def __del__(self):
        """
        Boson destructor.

        This method is invoked when the Boson instance is about to be destroyed. The destructor ensures that the
        aiohttp client session is closed before the instance is fully destroyed, releasing any remaining resources.

        Note: Relying on the destructor for cleanup can be unpredictable. It's recommended to explicitly close sessions
        using the provided methods or the `async with` context manager.

        Usage:
            boson = Boson()
            # ... some operations ...
            del boson  # This will implicitly invoke the __del__ method and close the session.
        """
        asyncio.run(self.aclose_session())
