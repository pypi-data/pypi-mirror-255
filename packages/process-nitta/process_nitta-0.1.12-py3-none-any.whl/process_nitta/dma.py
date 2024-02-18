from typing import Any, Optional, Tuple

import pandas as pd

from process_nitta.csv_config import CSVConfig
from process_nitta.models import Base


class DMASample(Base):
    temp_range: Optional[Tuple[float, float]] = None

    def model_post_init(
        self, __context: Any
    ) -> None:  # インスタンス生成後に実行される。csvから試料の大きさを取得する
        super().model_post_init(__context)
        if not self.temp_range:
            self.set_temp_range()
        return

    def set_temp_range(self) -> None:
        df: pd.DataFrame = pd.read_csv(
            self.file_path,
            **CSVConfig(
                skiprows=[n for n in range(9)],
                nrows=1,
                usecols=[23, 31],
            ).to_dict(),
        )

        self.temp_range = df.values[0]
        return

    def get_result_df(self, csv_config: CSVConfig = CSVConfig().DMA()) -> pd.DataFrame:
        df: pd.DataFrame = pd.read_csv(
            self.file_path,
            **csv_config.to_dict(),
        )
        return df

    def get_raw_df(self, csv_config: CSVConfig = CSVConfig().DMA()) -> pd.DataFrame:
        df: pd.DataFrame = pd.read_csv(
            self.file_path,
            **csv_config.to_dict(),
        )
        return df
