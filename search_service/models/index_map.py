from amundsen_common.models.index_map import TABLE_INDEX_MAP


class IndexMap:
    def __init__(self, map: str = TABLE_INDEX_MAP) -> None:
        # Specifying default mapping for elasticsearch index
        # Documentation: https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html
        # Setting type to "text" for all fields that would be used in search
        # Using Simple Analyzer to convert all text into search terms
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-simple-analyzer.html
        # Standard Analyzer is used for all text fields that don't explicitly specify an analyzer
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-standard-analyzer.html
        self.mapping = map

    def __repr__(self) -> str:
        return 'IndexMap()'
