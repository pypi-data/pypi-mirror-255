import asyncio
import threading

import websockets
import logging

class websocketWrapper:
    def __init__(self):
        self.websocket : websockets.WebSocketClientProtocol = None # type: ignore
        self.websocket_loop : asyncio.AbstractEventLoop = None # type: ignore
        self.websocket_thread : threading.Thread = None # type: ignore

    async def connect(self,websocket_uri, on_message = None ,on_connected=None, on_disconnected=None):
        
        logging.info(f"connect,websocket_uri={websocket_uri}")

        async def _main_thread_executor(func,param):
            func(param)
            
        def _start_loop(loop,main_loop):
            logging.debug(f"websocket thread, running, tid={threading.current_thread()}")

            asyncio.set_event_loop(loop)

            def _threadsafe_on_message(message):
                asyncio.run_coroutine_threadsafe(_main_thread_executor(on_message,message), main_loop)

            def _threadsafe_on_connected(websocket):
                logging.debug(f"ws_thread_on_connected, tid={threading.current_thread()}")
                asyncio.run_coroutine_threadsafe(_main_thread_executor(on_connected,websocket), main_loop)

            def _threadsafe_ondisconnected(websocket):
                logging.debug(f"ws_thread_ondisconnected, tid={threading.current_thread()}")
                asyncio.run_coroutine_threadsafe(_main_thread_executor(on_disconnected,websocket), main_loop)

            loop.run_until_complete(self._connect_websocket(uri=websocket_uri,on_message=_threadsafe_on_message,on_connected=_threadsafe_on_connected,on_disconnected=_threadsafe_ondisconnected))
            logging.debug(f"websocket thread, done, tid={threading.current_thread()}")
        
        self.main_loop = asyncio.get_running_loop()
        self.websocket_loop = asyncio.new_event_loop()
        self.websocket_thread = threading.Thread(target=_start_loop, args=(self.websocket_loop,self.main_loop))
        self.websocket_thread.start()

    async def disconnect(self):
        logging.info(f"disconnect")
        if self.websocket_loop is None:
            logging.error(f"websocket loop is None")
            return

        if self.websocket_thread is None:
            logging.error(f"websocket thread is None")
            return

        try:
            if self.websocket:
                await self.websocket.close()
        except Exception as e:
            pass

        self.websocket_thread.join()

    async def send_message(self,message):

        if self.websocket is None:
            logging.error(f"websocket connection is None")
            return
        
        await self.websocket.send(message)

    async def _connect_websocket(self,uri,on_message = None ,on_connected=None, on_disconnected=None):

        logging.info(f"Connecting to {uri}")
        try:
            async with websockets.connect(uri=uri) as websocket:

                self.websocket = websocket

                logging.info(f"Connected to {uri}")
                if on_connected:
                    on_connected(websocket)

                while True:
                    message = await websocket.recv()
                    if message is None:
                        break

                    if on_message:
                        on_message(message)

                logging.info(f"Disconnected to {uri}")
                if on_disconnected:
                    on_disconnected(websocket)
        except Exception as e:
            # if on_disconnected:
            #     on_disconnected(None)
            logging.error(f"Error, {e}")
