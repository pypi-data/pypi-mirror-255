from loguru import logger
from pathlib import Path
from pq_dataset import PQDataset

log_file_path = Path.joinpath(Path(__file__).parent, 'pqd_log.log')
logger.add(log_file_path, level="DEBUG", colorize=False, backtrace=True, diagnose=True)

if __name__ == '__main__':

    json_data = r'1924932.zip'
    json_map = r'1924932.json'
    data_path = r'C:\Users\ctf\pq_data\barnets_perspektiv'
    output_path = r'C:\Users\ctf\pq_data\barnets_perspektiv'

    bp = PQDataset(
        input_file=json_data,
        json_file=json_map,
        input_path=data_path,
        output_path=output_path,
        room_id=491,
        debug=True
    )
    
    bp.identify_relevante_data_ftp(1924932)
