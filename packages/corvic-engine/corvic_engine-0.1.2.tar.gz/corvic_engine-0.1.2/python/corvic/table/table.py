"""Table."""

import polars as pl

from corvic.table.schema import Schema, SchemaHints


class Table:
    """A table."""

    @classmethod
    def from_polars(cls, df: pl.DataFrame, *, schema_hints: SchemaHints | None = None):
        """Create a table from a pl.DataFrame.

        Args:
            df: a polars DataFrame
            schema_hints: How to map DataFrame types into a Schema
        """

    @property
    def schema(self) -> Schema:
        """Return schema for table."""
        return Schema()

    def to_polars(self) -> pl.DataFrame:
        """Return a copy of the table as a pl.DataFrame."""
        return pl.DataFrame()
