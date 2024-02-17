from pathlib import Path

import pandas as pd
from process_nitta import InstronSample


def test_instron():
    workspace_dir = Path(__file__).parent.parent
    sample = InstronSample(
        file_path=f"{workspace_dir}/sample_data/instron.csv",
        name="sample",
        width_mm=2.5,
        length_mm=10,
        thickness_μm=2000,
        speed_mm_per_min=500,
    )
    result_df = sample.get_result_df()
    answer_df = pd.read_csv(
        f"{workspace_dir}/tests/answer_data/instron.csv", index_col=0
    )
    pd.testing.assert_frame_equal(result_df, answer_df)
