import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Pagination:
    """This is a wrapper around Sigma's pagination system"""

    def __init__(
        self,
        next_page: Optional[str],
        entries: Optional[list] = None,
        total: Optional[int] = 0,
    ):
        self.next_page = next_page
        self.entries = entries or []
        self.total = total

    def generate_url(self, endpoint_url: str) -> str:
        """Generates the paginated url based on the targeted endpoint"""
        pagination = f"?page={self.next_page}"
        paginated_url = f"{endpoint_url}{pagination}"
        return paginated_url
