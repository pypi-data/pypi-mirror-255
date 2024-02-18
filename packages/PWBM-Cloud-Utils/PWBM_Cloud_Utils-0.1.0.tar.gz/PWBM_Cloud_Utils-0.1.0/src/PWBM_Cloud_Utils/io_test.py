from .io_config import IO_Config
from .io_reader import IO_Reader

import io
import pandas as pd
from pathlib import Path


def main():
    path = 'C:\\Users\\yunyej\\Documents\\GitHub\\PWBM_Cloud_Utils\\src\\PWBM_Cloud_Utils\\.env'
    file_path = Path(path)
    print("test")
    config = IO_Config(path=file_path)
    print(config.region_name)
    reader = IO_Reader(config)
    data = reader.read(
        "tax-calc-data",
        "SOIMatching/Interfaces/2023-06-15-jricco/CPS-SOIMatch2019.csv",
        False,
    )

    print(pd.read_csv(io.BytesIO(data)))


if __name__ == "__main__":
    main()
