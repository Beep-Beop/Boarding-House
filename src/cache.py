from src.logger import logger


class CacheService:
    def __init__(self):
        self.province_cache: list[str] = []

    def is_province_cached(self) -> bool:
        return bool(self.province_cache)

    def get_provinces(self) -> list[str]:
        return list(self.province_cache)

    def set_provinces(self, provinces: list[str]) -> None:
        self.province_cache = list(provinces)
        logger.info("Province cache updated with %d provinces", len(provinces))
