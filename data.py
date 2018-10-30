import glob
import gzip
import io
import os
import pandas as pd

import carball
import requests
from carball.analysis.analysis_manager import PandasManager, AnalysisManager
from carball.analysis.utils.proto_manager import ProtobufManager
from carball.generated.api.game_pb2 import Game

BASE_URL = 'https://calculated.gg/api/v1/'


class Calculated:

    def get_replay_list(self, num=50):
        r = requests.get(BASE_URL + 'replays?key=1&minrank=19&teamsize=3')
        return [replay['id'] for replay in r.json()['data']]

    def get_pandas(self, id_):
        url = BASE_URL + 'parsed/{}.replay.gzip?key=1'.format(id_)
        r = requests.get(url)
        gzip_file = gzip.GzipFile(fileobj=io.BytesIO(r.content), mode='rb')

        pandas_ = PandasManager.safe_read_pandas_to_memory(gzip_file)
        return pandas_

    def get_proto(self, id_):
        url = BASE_URL + 'parsed/{}.replay.pts?key=1'.format(id_)
        r = requests.get(url)
        #     file_obj = io.BytesIO()
        #     for chunk in r.iter_content(chunk_size=1024):
        #         if chunk: # filter out keep-alive new chunks
        #             file_obj.write(chunk)
        proto = ProtobufManager.read_proto_out_from_file(io.BytesIO(r.content))
        return proto


class Carball:
    REPLAYS_DIR = 'replays'
    REPLAYS_MAP = {}

    def get_replay_list(self):
        replays = glob.glob(os.path.join(self.REPLAYS_DIR, '*.replay'))
        return [os.path.basename(replay).split('.')[0] for replay in replays]

    def get_pandas(self, id_) -> pd.DataFrame:
        return self._process(id_).data_frame

    def get_proto(self, id_) -> Game:
        return self._process(id_).protobuf_game

    def _process(self, id_) -> AnalysisManager:
        if id_ in self.REPLAYS_MAP:
            return self.REPLAYS_MAP[id_]
        path = os.path.join(self.REPLAYS_DIR, id_ + '.replay')
        manager = carball.analyze_replay_file(path, "replay.json")
        self.REPLAYS_MAP[id_] = manager
        return manager
