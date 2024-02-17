from pathlib import Path

import pandas as pd
from process_nitta import DMASample


def test_dma():
    workspace_dir = Path(__file__).parent.parent
    sample = DMASample(
        file_path=f"{workspace_dir}/sample_data/dma.csv",
        name="sample",
    )
    result_df = sample.get_result_df()
    answer_df = pd.read_csv(f"{workspace_dir}/tests/answer_data/dma.csv", index_col=0)
    pd.testing.assert_frame_equal(result_df, answer_df)
