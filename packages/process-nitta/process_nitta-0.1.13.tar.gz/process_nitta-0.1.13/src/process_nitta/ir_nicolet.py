import pandas as pd

from process_nitta.csv_config import CSVConfig
from process_nitta.models import Base


class IRNICOLETSample(Base):
    def get_result_df(
        self, csv_config: CSVConfig = CSVConfig().IR_NICOLET()
    ) -> pd.DataFrame:
        df: pd.DataFrame = pd.read_csv(
            self.file_path,
            **csv_config.to_dict(),
        )
        return df

    def get_raw_df(
        self, csv_config: CSVConfig = CSVConfig().IR_NICOLET()
    ) -> pd.DataFrame:
        df: pd.DataFrame = pd.read_csv(
            self.file_path,
            **csv_config.to_dict(),
        )
        return df
