from pathlib import Path

import pandas as pd
from process_nitta import AGISSample


def test_agis():
    workspace_dir = Path(__file__).parent.parent
    sample = AGISSample(
        file_path=f"{workspace_dir}/sample_data/agis.csv",
        name="sample",
    )
    result_df = sample.get_result_df()
    answer_df = pd.read_csv(f"{workspace_dir}/tests/answer_data/agis.csv", index_col=0)
    pd.testing.assert_frame_equal(result_df, answer_df)
