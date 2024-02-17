def search_in_list(search_dict, items_list):
    return [
        item for item in items_list if all(
            item.get(key) == value for key, value in search_dict.items()
        )
    ] if items_list else []