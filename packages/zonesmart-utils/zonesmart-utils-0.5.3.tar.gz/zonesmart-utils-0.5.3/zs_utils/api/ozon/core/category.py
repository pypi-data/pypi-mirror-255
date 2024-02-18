from zs_utils.api.ozon.base_api import OzonAPI


class OzonGetCategoriesTreeAPI(OzonAPI):
    """
    Docs: https://docs.ozon.ru/api/seller/#operation/CategoryAPI_GetCategoryTree
    """

    resource_method = "v2/category/tree"
    allowed_params = ["category_id", "language"]


class OzonGetCategoryAttributeAPIv3(OzonAPI):
    """
    Docs: https://docs.ozon.ru/api/seller/#operation/CategoryAPI_GetCategoryAttributesV3
    """

    resource_method = "v3/category/attribute"
    required_params = ["category_id"]
    allowed_params = ["language", "attribute_type"]


class OzonGetCategoryAttributeDictionaryAPI(OzonAPI):
    """
    Docs: https://docs.ozon.ru/api/seller/#operation/CategoryAPI_DictionaryValueBatch
    """

    resource_method = "v2/category/attribute/values"
    required_params = ["attribute_id", "category_id", "limit"]
    allowed_params = ["language", "last_value_id"]
