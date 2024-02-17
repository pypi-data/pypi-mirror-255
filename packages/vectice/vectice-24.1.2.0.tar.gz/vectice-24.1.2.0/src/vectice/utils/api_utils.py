INDEX_ORDERED = {"field": "index", "direction": "ASC"}
INDEX_ORDERED_DESC = {"field": "index", "direction": "DESC"}
PAGINATE_OUTPUT = """
            items {{
                {0}
            }}
            page {{
                index
                size
            }}
            total
"""


def get_page_input(index: int = 1, size: int = 10) -> dict:
    return {"index": index, "size": size}
