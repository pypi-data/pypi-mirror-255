import asyncio
import logging

import aiohttp
import lamini
from lamini.api.utils.base_async_inference_queue import BaseAsyncInferenceQueue
from lamini.api.utils.process_batch import process_batch

logger = logging.getLogger(__name__)


class AsyncInferenceQueue(BaseAsyncInferenceQueue):
    async def submit(self, request, local_cache_file, callback=None):
        # Break the request into batches
        results = []
        exceptions = []
        local_cache = None
        if local_cache_file:
            local_cache = self.read_local_cache(local_cache_file)
        self.reservation_api.initialize_reservation(
            len(request["prompt"]),
        )
        self.reservation_api.pause_for_reservation_start()
        connector = aiohttp.TCPConnector(limit=self.get_max_workers())
        async with aiohttp.ClientSession(connector=connector) as client:
            batches = self.form_batches(
                request,
                client,
                self.api_key,
                self.api_prefix,
                local_cache_file,
                local_cache,
                callback,
            )
            self.reservation_polling_task = asyncio.create_task(
                self.reservation_api.kickoff_reservation_polling(client)
            )
            semaphore = asyncio.Semaphore(lamini.max_workers)
            tasks = [
                asyncio.ensure_future(wrapper(semaphore, process_batch(batch)))
                for batch in batches
            ]
            mixed_results = await asyncio.gather(*tasks)
            for result in mixed_results:
                if isinstance(result, Exception):
                    exceptions.append(result)
                else:
                    results.append(result)
        self.reservation_api.is_working = False
        if self.reservation_polling_task is not None:
            self.reservation_polling_task.cancel()
        if self.reservation_api.polling_task is not None:
            self.reservation_api.polling_task.cancel()
        if len(exceptions) > 0:
            print(
                f"Encountered {len(exceptions)} errors during run. Raising first as an exception."
            )
            raise exceptions[0]
        # Combine the results and return them
        return self.combine_results(results)

    def combine_results(self, results):
        combined_results = []
        for result in results:
            logger.info(f"inference result: {result}")
            if isinstance(result, list):
                combined_results.extend(result)
            else:
                combined_results.append(result)

        return combined_results

    def form_batches(
        self, request, client, key, api_prefix, local_cache_file, local_cache, callback
    ):
        batch_size = self.get_batch_size()

        if isinstance(request["prompt"], str):
            yield {
                "api_prefix": api_prefix,
                "key": key,
                "batch": request,
                "client": client,
                "local_cache_file": local_cache_file,
                "local_cache": local_cache,
                "index": 0,
                "callback": callback,
            }
        else:
            for i in range(0, len(request["prompt"]), batch_size):
                batch = request.copy()
                end = min(i + batch_size, len(request["prompt"]))
                batch["prompt"] = request["prompt"][i:end]
                yield {
                    "api_prefix": api_prefix,
                    "key": key,
                    "batch": batch,
                    "client": client,
                    "local_cache_file": local_cache_file,
                    "local_cache": local_cache,
                    "index": i,
                    "callback": callback,
                }


async def wrapper(semaphore, aw):
    async with semaphore:
        return await aw
