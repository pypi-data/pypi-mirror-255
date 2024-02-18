from zs_utils.api.wildberries.base_api import WildberriesAPI


class GetWildberriesNomenclatureList(WildberriesAPI):
    """
    https://openapi.wb.ru/#tag/Kontent-Prosmotr/paths/~1content~1v1~1cards~1cursor~1list/post
    """

    http_method = "POST"
    resource_method = "content/v1/cards/cursor/list"
    required_params = ["sort"]


class GetWildberriesNomenclatureByVendorCode(WildberriesAPI):
    """
    https://openapi.wb.ru/#tag/Kontent-Prosmotr/paths/~1content~1v1~1cards~1filter/post
    """

    http_method = "POST"
    resource_method = "content/v1/cards/filter"
    required_params = ["vendorCodes"]


class GetWildberriesPrices(WildberriesAPI):
    """
    https://openapi.wb.ru/#tag/Ceny/paths/~1public~1api~1v1~1info/get
    """

    http_method = "GET"
    resource_method = "public/api/v1/info"
    allowed_params = ["quantity"]


class UpdateWildberriesPrices(WildberriesAPI):
    """
    https://openapi.wb.ru/#tag/Ceny/paths/~1public~1api~1v1~1prices/post
    """

    http_method = "POST"
    resource_method = "public/api/v1/prices"
    array_payload = True


class UpdateWildberriesDiscounts(WildberriesAPI):
    """
    https://openapi.wb.ru/#tag/Promokody-i-skidki/paths/~1public~1api~1v1~1updateDiscounts/post
    """

    http_method = "POST"
    resource_method = "public/api/v1/updateDiscounts"
    array_payload = True


class RevokeWildberriesDiscounts(WildberriesAPI):
    """
    https://openapi.wb.ru/#tag/Promokody-i-skidki/paths/~1public~1api~1v1~1revokeDiscounts/post
    """

    http_method = "POST"
    resource_method = "public/api/v1/revokeDiscounts"
    array_payload = True


class CreateWildberriesBarcodes(WildberriesAPI):
    """
    https://openapi.wb.ru/#tag/Kontent-Prosmotr/paths/~1content~1v1~1barcodes/post
    """

    http_method = "POST"
    resource_method = "content/v1/barcodes"
    required_params = ["count"]


class GetWildberriesFailedToUploadNomenclatureList(WildberriesAPI):
    """
    https://openapi.wb.ru/#tag/Kontent-Prosmotr/paths/~1content~1v1~1cards~1error~1list/get
    """

    http_method = "GET"
    resource_method = "content/v1/cards/error/list"


class CreateWildberriesNomenclature(WildberriesAPI):
    """
    https://openapi.wb.ru/#tag/Kontent-Zagruzka/paths/~1content~1v1~1cards~1upload/post
    """

    http_method = "POST"
    resource_method = "content/v1/cards/upload"
    array_payload = True


class UpdateWildberriesNomenclature(WildberriesAPI):
    """
    https://openapi.wb.ru/#tag/Kontent-Zagruzka/paths/~1content~1v1~1cards~1update/post
    """

    http_method = "POST"
    resource_method = "content/v1/cards/update"
    array_payload = True


class AddWildberriesNomenclaturesToCard(WildberriesAPI):
    """
    https://openapi.wb.ru/#tag/Kontent-Zagruzka/paths/~1content~1v1~1cards~1upload~1add/post
    """

    http_method = "POST"
    resource_method = "content/v1/cards/upload/add"
    required_params = [
        "vendorCode",
        "cards",
    ]


class UpdateWildberriesNomenclatureImages(WildberriesAPI):
    """
    https://openapi.wb.ru/#tag/Kontent-Mediafajly/paths/~1content~1v1~1media~1save/post
    """

    http_method = "POST"
    resource_method = "content/v1/media/save"
    required_params = [
        "vendorCode",
        "data",
    ]
