import json
from utils.trace import trace
from utils.is_num import is_num
from utils.is_latitude_longitude import is_latitude_longitude


@trace
def load(file):
    """
    Считывает сохраненные конфигурации из json файлов вида:
    {
      "mode": "Граф"(или "Карта"),
      "coordinates": [[x,y], ...], (для графа)
      "lat_long": [ {"lat": ..., "lng": ...}, ...], (для карты)
      "matrix": [[0, 12, ...], ...]
      (может не быть, в таком случае будет сгенерировано, либо запрошено)
    }
    """
    with open(file, 'r', encoding='utf-8') as file:
        configuration: dict = json.load(file)
        e = 'Неправильный формат файла'

        if 'mode' not in configuration:
            raise Exception(e)

        if configuration['mode'] == 'Граф':
            if 'coordinates' not in configuration:
                raise Exception(e)
            for x, y in configuration['coordinates']:
                if not is_num(x) or not is_num(y):
                    raise Exception(e)

        elif configuration['mode'] == 'Карта':
            if 'lat_long' not in configuration:
                raise Exception(e)
            for lat_long in configuration['lat_long']:
                if not is_latitude_longitude(lat_long):
                    raise Exception(e)

        else:
            raise Exception(e)

        if 'matrix' in configuration:
            matrix = configuration['matrix']
            if not isinstance(matrix, list):
                raise Exception(e)
            size = len(matrix)
            for line in matrix:
                if not isinstance(line, list):
                    raise Exception(e)
                if len(line) != size:
                    raise Exception(e)
                for elem in line:
                    if not is_num(elem):
                        raise Exception(e)

        return configuration


@trace
def save(file, obj):
    with open(file, 'w') as file:
        json.dump(obj, file, indent=2)
