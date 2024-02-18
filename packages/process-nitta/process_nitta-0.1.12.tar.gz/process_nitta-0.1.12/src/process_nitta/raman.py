import pandas as pd
from pybaselines import Baseline

from process_nitta.csv_config import ColumnStrEnum as col
from process_nitta.csv_config import CSVConfig
from process_nitta.models import Base


class RamanSample(Base):
    def baseline_correction(
        self, df: pd.DataFrame, lam: float = 1e7, p: float = 0.02
    ) -> pd.DataFrame:
        df = df.copy()
        baseline_fitter = Baseline(df[col.RAMAN_SHIFT].values, check_finite=False)
        bkg = baseline_fitter.asls(df[col.INTENSITY], lam=lam, p=p)[0]
        df[col.INTENSITY] = df[col.INTENSITY] - bkg
        return df

    def get_raw_df(self, config: CSVConfig = CSVConfig().Raman()) -> pd.DataFrame:
        return pd.read_csv(self.file_path, **config.to_dict())

    def get_result_df(
        self, lam: float = 1e7, p: float = 0.02, config: CSVConfig = CSVConfig().Raman()
    ) -> pd.DataFrame:
        return self.baseline_correction(
            self.get_raw_df(config=config),
            lam=lam,
            p=p,
        )
