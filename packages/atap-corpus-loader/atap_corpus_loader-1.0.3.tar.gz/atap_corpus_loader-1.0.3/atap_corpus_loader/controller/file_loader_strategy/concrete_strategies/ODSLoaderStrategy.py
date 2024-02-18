from pandas import DataFrame, read_excel

from atap_corpus_loader.controller.data_objects import CorpusHeader, DataType, FileReference
from atap_corpus_loader.controller.file_loader_strategy.FileLoaderStrategy import FileLoaderStrategy


class ODSLoaderStrategy(FileLoaderStrategy):
    def get_inferred_headers(self) -> list[CorpusHeader]:
        filepath: str = self.file_ref.resolve_real_file_path()
        df: DataFrame = read_excel(filepath, engine='odf', nrows=2)
        headers: list[CorpusHeader] = []
        for header_name, dtype_obj in df.dtypes.items():
            dtype: DataType
            try:
                dtype = DataType(str(dtype_obj))
            except ValueError:
                dtype = DataType.TEXT
            headers.append(CorpusHeader(str(header_name), dtype, True))

        return headers

    def get_dataframe(self, headers: list[CorpusHeader]) -> DataFrame:
        included_headers: list[str] = [header.name for header in headers if header.include]
        filepath: str = self.file_ref.resolve_real_file_path()
        df: DataFrame = read_excel(filepath, engine='odf', header=0, names=included_headers)
        dtypes_applied_df: DataFrame = FileLoaderStrategy._apply_selected_dtypes(df, headers)

        return dtypes_applied_df
