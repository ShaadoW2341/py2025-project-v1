import os
import json
import csv
import zipfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Iterator, Optional

class Logger:
    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        self.log_dir = Path(config['log_dir'])
        self.archive_dir = self.log_dir / "archive"
        self.filename_pattern = config['filename_pattern']
        self.buffer_size = config['buffer_size']
        self.rotate_every_hours = config['rotate_every_hours']
        self.max_size_mb = config['max_size_mb']
        self.rotate_after_lines = config.get('rotate_after_lines', None)
        self.retention_days = config['retention_days']

        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        self.buffer = []
        self.current_file = None
        self.current_writer = None
        self.current_filename = ""
        self.last_rotation = datetime.now()
        self.line_count = 0

    def start(self):
        now = datetime.now()
        filename = now.strftime(self.filename_pattern)
        self.current_filename = str(self.log_dir / filename)
        new_file = not os.path.exists(self.current_filename)

        self.current_file = open(self.current_filename, mode='a', newline='', encoding='utf-8')
        self.current_writer = csv.writer(self.current_file)

        if new_file:
            self.current_writer.writerow(['timestamp', 'sensor_id', 'value', 'unit'])

        self.last_rotation = now
        self.line_count = sum(1 for _ in open(self.current_filename, 'r', encoding='utf-8')) - 1

    def stop(self):
        self._flush()
        if self.current_file:
            self.current_file.close()
        self._maybe_rotate()

    def log_reading(self, sensor_id: str, timestamp: datetime, value: float, unit: str):
        self.buffer.append([timestamp.isoformat(), sensor_id, value, unit])
        if len(self.buffer) >= self.buffer_size:
            self._flush()
            self._maybe_rotate()

    def _flush(self):
        if not self.current_writer:
            return
        self.current_writer.writerows(self.buffer)
        self.line_count += len(self.buffer)
        self.buffer.clear()
        self.current_file.flush()

    def _maybe_rotate(self):
        now = datetime.now()
        file_size_mb = os.path.getsize(self.current_filename) / (1024 * 1024)

        if (
            (now - self.last_rotation) >= timedelta(hours=self.rotate_every_hours)
            or file_size_mb >= self.max_size_mb
            or (self.rotate_after_lines and self.line_count >= self.rotate_after_lines)
        ):
            self._rotate()

    def _rotate(self):
        self.stop()
        base = Path(self.current_filename).name
        archive_path = self.archive_dir / (base + '.zip')

        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(self.current_filename, arcname=base)

        os.remove(self.current_filename)
        self._clean_old_archives()
        self.start()

    def _clean_old_archives(self):
        now = datetime.now()
        for file in self.archive_dir.glob('*.zip'):
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            if (now - mtime).days > self.retention_days:
                file.unlink()

    def read_logs(self, start: datetime, end: datetime, sensor_id: Optional[str] = None) -> Iterator[Dict]:
        def parse_row(row):
            ts = datetime.fromisoformat(row[0])
            if start <= ts <= end:
                if not sensor_id or row[1] == sensor_id:
                    return {
                        "timestamp": ts,
                        "sensor_id": row[1],
                        "value": float(row[2]),
                        "unit": row[3]
                    }
            return None

        for file in self.log_dir.glob('*.csv'):
            with open(file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    parsed = parse_row(row)
                    if parsed:
                        yield parsed

        for archive in self.archive_dir.glob('*.zip'):
            with zipfile.ZipFile(archive, 'r') as zipf:
                for name in zipf.namelist():
                    with zipf.open(name) as f:
                        lines = f.read().decode('utf-8').splitlines()
                        reader = csv.reader(lines)
                        next(reader)
                        for row in reader:
                            parsed = parse_row(row)
                            if parsed:
                                yield parsed
