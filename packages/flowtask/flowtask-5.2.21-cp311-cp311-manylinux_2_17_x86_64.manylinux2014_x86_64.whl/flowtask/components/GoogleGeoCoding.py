# import orjson
import asyncio
import aiohttp
import logging
# import requests
import pandas as pd
from flowtask.conf import GOOGLE_API_KEY
from flowtask.components import DtComponent
from flowtask.exceptions import ComponentError


logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

class GoogleGeoCoding(DtComponent):
    base_url: str = "https://maps.googleapis.com/maps/api/geocode/json"

    async def start(self, **kwargs):
        self._counter: int = 0
        if self.previous:
            self.data = self.input
        if not hasattr(self, 'columns'):
            raise RuntimeError(
                'GoogleGeoCoding requires a Column Attribute'
            )
        if not isinstance(self.columns, list):
            raise RuntimeError(
                'GoogleGeoCoding requires a Column Attribute as list'
            )
        if not isinstance(self.data, pd.DataFrame):
            raise ComponentError(
                "Incompatible Pandas Dataframe", code=404
            )
        return True

    async def get_coordinates(self, idx, row):
        if pd.isnull(row.get('place_id', None)):
            return idx, None
        street_address = self.columns[0]
        if pd.notnull(row[street_address]):
            print('== ENTRA AQUI === ')
            address = ', '.join(row[self.columns])
            params = {
                "address": address,
                "key": GOOGLE_API_KEY
            }
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.base_url, params=params) as response:
                        self._counter += 1
                        if response.status == 200:
                            result = await response.json()
                            if result['status'] == 'OK':
                                data = result['results'][0]
                                return idx, {
                                    "latitude": data['geometry']['location']['lat'],
                                    "longitude": data['geometry']['location']['lng'],
                                    "formatted_address": data['formatted_address'],
                                    "place_id": str(data['place_id'])
                                }
            except asyncio.TimeoutError as exc:
                self._logger.error(f"TimeoutException: {exc}")
                return idx, None
        return idx, None

    async def run(self):
        # initialize columns:
        self.data['geometry'] = pd.NaT
        self.data['place_id'] = pd.NaT
        self.data['formatted_address'] = pd.NaT
        self._result = self.data
        tasks = [
            self.get_coordinates(idx, row) for idx, row in self.data.iterrows()
            if pd.isnull(row.get('place_id', None))
        ]
        results = await asyncio.gather(*tasks)
        for idx, result in results:
            if result:
                for key, value in result.items():
                    self.data.at[idx, key] = value
        self.add_metric("DOWNLOADED", self._counter)
        return self._result

    async def close(self):
        pass
