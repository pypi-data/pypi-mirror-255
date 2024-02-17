import io

import pyarrow as pa
import pyarrow.parquet as pq

from sarus.typing import Client


def fetch_synthetic(client: Client, id: str) -> pa.Table:
    """Fetch synthetic data for a Dataset."""
    resp = client.session().get(
        f"{client.url()}/synthetic_data/{id}",
        stream=True,
        params={
            "textual_categories": True,
            "rows_number": None,
        },
    )
    if resp.status_code > 200:
        raise Exception(
            f"Error while retrieving synthetic data. "
            f"Gateway answer was: \n{resp}"
        )

    synthetic_table = pq.ParquetFile(io.BytesIO(resp.content)).read()

    return synthetic_table
