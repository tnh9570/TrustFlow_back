from typing import List, Dict, Tuple
import logging
logger = logging.getLogger("app.utils")

def parse_filters(filters: List[str]) -> Dict[str, List[str]]:
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

def build_filter_query(filter_result:str, filters:dict[List], allow_filter_columns:dict) :
    logger.debug(f"start build_filter_query")
    filter_query_params = []  # 바인딩할 파라미터 값을 저장할 리스트
    del_list = []
    
    for column, value in filters.items():
        if column in allow_filter_columns:
            placeholders = ", ".join(["%s"] * len(value))  # IN 절의 플레이스홀더 생성
            filter_result += f"AND {allow_filter_columns[column]} IN ({placeholders}) "
            filter_query_params.extend(value)  # 바인딩 값 추가
        else:
            del_list.append(column)

    for li in del_list:
        del filters[li]

    logger.debug(f"Executing query: {filter_result}")
    logger.debug(f"Executing query parameters: {filter_query_params}")

    return filter_result, filter_query_params

def build_sort_query(sort_result:str, sorts:List, allow_sort_columns:dict, allow_sort_directions:List[str]):
    logger.debug(f"start build_sort_query")

    sort_query_params = []
    for item in sorts:
        column, direction = item.split(":")
        # direction을 소문자로 변환 후 검증
        direction = direction.lower()
        if column in allow_sort_columns and direction in allow_sort_directions:
            sort_query_params.append(f"{column} {direction.upper()}")
    
    sort_result = " ORDER BY "+", ".join(sort_query_params)

    logger.debug(f"Executing query: {sort_result}")
    logger.debug(f"Executing query parameters: {sort_query_params}")

    return sort_result

def calculate_pagination(page: int, size: int) -> Tuple[int, int]:
    """페이징을 위한 offset과 limit 계산."""
    offset = (page - 1) * size
    limit = size
    return offset, limit