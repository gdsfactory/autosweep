from pathlib import Path

from ta.utils import io
from ta.utils.data_types import metadata


def find_last_run(path):
    timestamps = []
    runs = []

    for run in sorted(Path(path).glob('*')):
        if run.is_dir():
            status_path = run / 'status.json'
            if status_path.exists():
                status = io.read_json(path=status_path)
                timestamp_strs = status.get('timestamp')
                if timestamp_strs:
                    ts = metadata.TimeStamp(timestamp=timestamp_strs['start'])
                    timestamps.append(ts)
                    runs.append(run)

    sort_idx = [ii for ii, ts in sorted(enumerate(timestamps), key=lambda x: x[1])]
    return runs[sort_idx[-1]]
