from typing import List, Dict

async def parse_filters(filters: List[str]) -> Dict[str, List[str]]:
    """
    필터 문자열을 파싱하여 딕셔너리 형태로 반환합니다.
    예: ["status:success", "version:1.0"] -> {"status": ["success"], "version": ["1.0"]}
    """
    query_filters = {}
    if filters:
        for filter_param in filters:
            try:
                column, value = filter_param.split(":")
                query_filters.setdefault(column, []).append(value)
            except ValueError:
                raise ValueError(f"Invalid filter format: {filter_param}. Expected 'column:value'")
    return query_filters
