import pandas as pd

from process_nitta.csv_config import ColumnStrEnum as col
from process_nitta.csv_config import CSVConfig
from process_nitta.models import Sample


class InstronSample(Sample):
    speed_mm_per_min: float
    freq_Hz: float = 0.05
    load_cell_max_N: int = 100
    load_cell_calibration_coef: float = 1
    max_Voltage: float = 10
    mean_range: int = 100

    def trim_df(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        roll = pd.DataFrame(
            df[col.VOLTAGE].rolling(window=self.mean_range).mean().diff()
        )

        start = (
            int(roll[col.VOLTAGE][self.mean_range : self.mean_range * 2].idxmax())
            - self.mean_range
            + 1
        )  # 傾きが最大のところを探す
        end = int(roll[col.VOLTAGE].idxmin()) + 10

        result = df[start:end].reset_index(drop=True)
        result[col.VOLTAGE] = (
            result[col.VOLTAGE] - result[col.VOLTAGE][0]
        )  # 初期値を0にする

        return result

    def calc_stress_strain_df(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        df = raw_df.copy()
        area_mm2 = self.width_mm * self.thickness_μm / 1000
        speed_mm_per_sec = self.speed_mm_per_min / 60

        stress_Mpa = (
            self.load_cell_max_N
            / (self.load_cell_calibration_coef * self.max_Voltage)
            / area_mm2
            * df[col.VOLTAGE]
        )
        strain = speed_mm_per_sec * self.freq_Hz * df.index / self.length_mm

        return pd.DataFrame(
            {col.STRAIN: strain, col.STRESS: stress_Mpa},
        )

    def get_result_df(
        self, csv_config: CSVConfig = CSVConfig().Instron()
    ) -> pd.DataFrame:
        df: pd.DataFrame = pd.read_csv(self.file_path, **csv_config.to_dict())
        stress_strain_df = self.calc_stress_strain_df(self.trim_df(df))
        draw_ratio = stress_strain_df[col.STRAIN] + 1

        result_df = pd.DataFrame(
            {
                col.STRAIN: stress_strain_df[col.STRAIN],
                col.STRESS: stress_strain_df[col.STRESS],
                col.DRAW_RATIO: draw_ratio,
                col.GAUSSIAN_STRAIN: draw_ratio**2 - 1 / draw_ratio,
                col.TRUE_STRESS: draw_ratio * stress_strain_df[col.STRESS],
            }
        )
        return result_df

    def get_raw_df(self, csv_config: CSVConfig = CSVConfig().Instron()) -> pd.DataFrame:
        df: pd.DataFrame = pd.read_csv(
            self.file_path,
            **csv_config.to_dict(),
        )
        return df
