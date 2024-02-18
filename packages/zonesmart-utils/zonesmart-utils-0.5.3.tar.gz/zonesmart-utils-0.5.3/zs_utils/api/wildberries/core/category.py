from zs_utils.api.wildberries.base_api import WildberriesAPI


class GetWildberriesCategoryList(WildberriesAPI):
    """
    Docs: https://openapi.wildberries.ru/#tag/Kontent-Konfigurator/paths/~1content~1v1~1object~1all/get
    """

    http_method = "GET"
    resource_method = "content/v1/object/all"
    allowed_params = ["name", "top"]


class GetWildberriesCategoryParentList(WildberriesAPI):
    """
    Docs: https://openapi.wildberries.ru/#tag/Kontent-Konfigurator/paths/~1content~1v1~1object~1parent~1all/get
    """

    http_method = "GET"
    resource_method = "content/v1/object/parent/all"


class GetWildberriesCategoryAttributes(WildberriesAPI):
    """
    Docs: https://openapi.wildberries.ru/#tag/Kontent-Konfigurator/paths/~1content~1v1~1object~1characteristics~1%7BobjectName%7D/get
    """

    http_method = "GET"
    resource_method = "content/v1/object/characteristics/{objectName}"
    required_params = ["objectName"]


class GetWildberriesAttributeValues(WildberriesAPI):
    """
    Docs: https://openapi.wildberries.ru/#tag/Kontent-Konfigurator/paths/~1content~1v1~1directory~1colors/get
    Значения dictionary_name:
    - colors (Цвет)
    - kinds (Пол)
    - countries (Страна производства)
    - collections (Коллекции)
    - seasons (Сезон)
    - contents (Комплектация)
    - consists (Состав)
    - brands (Бренд)
    - tnved (ТНВЭД)
    """

    http_method = "GET"
    resource_method = "content/v1/directory/{dictionary_name}"
    required_params = []
    allowed_params = [
        "top",  # кроме colors, kinds, countries, seasons
        "pattern",  # кроме colors, kinds, countries, seasons
        "objectName",  # только tnved
        "tnvedsLike",  # только tnved
    ]
