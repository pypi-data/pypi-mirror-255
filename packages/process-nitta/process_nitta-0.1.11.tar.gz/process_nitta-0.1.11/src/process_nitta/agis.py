from typing import Any

import pandas as pd

from process_nitta.csv_config import ColumnStrEnum as col
from process_nitta.csv_config import CSVConfig
from process_nitta.models import Sample


class AGISSample(Sample):
    calibration_coefficient: float = 0.84  # 2023/1/02時点
    width_mm: float = 0
    length_mm: float = 0
    thickness_μm: float = 0
    mean_range: int = 100

    def model_post_init(
        self, __context: Any
    ) -> None:  # インスタンス生成後に実行される。csvから試料の大きさを取得する
        super().model_post_init(__context)
        if not all([self.width_mm, self.length_mm, self.thickness_μm]):
            self.set_sample_size()
        return

    def set_sample_size(self) -> None:
        size_df: pd.DataFrame = pd.read_csv(
            self.file_path,
            **CSVConfig(
                skiprows=[n for n in range(10)],
                nrows=1,
                usecols=[1, 2, 3],
                dtype={"1": float, "2": float, "3": float},
            ).to_dict(),
        )

        thickness_mm, self.width_mm, self.length_mm = size_df.values[0]
        self.thickness_μm = thickness_mm * 1000
        return

    def trim_df(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        roll = pd.DataFrame(df[col.FORCE].rolling(window=self.mean_range).mean().diff())

        start = (
            int(roll[col.FORCE][self.mean_range : self.mean_range * 2].idxmax())
            - self.mean_range
            + 1
        )  # 傾きが最大のところを探す

        result = df[start:].reset_index(drop=True)
        result[col.STROKE] = result[col.STROKE] - result[col.STROKE][0]
        result[col.FORCE] = result[col.FORCE] - result[col.FORCE][0]
        return result

    def calc_stress_strain_df(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        area_mm2 = self.width_mm * self.thickness_μm / 1000

        stress_Mpa = self.calibration_coefficient * df[col.FORCE] / area_mm2
        strain = df[col.STROKE] / self.length_mm

        return pd.DataFrame(
            {col.STRAIN: strain, col.STRESS: stress_Mpa},
        )

    def get_result_df(self, csv_config: CSVConfig = CSVConfig().AGIS()) -> pd.DataFrame:
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

    def get_raw_df(self, csv_config: CSVConfig = CSVConfig().AGIS()) -> pd.DataFrame:
        df: pd.DataFrame = pd.read_csv(
            self.file_path,
            **csv_config.to_dict(),
        )
        return df
