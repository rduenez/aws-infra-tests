"""
Sample data for testing.
"""
import random
import string
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from src.domain.entities import Item


# =============================================================================
# Static Sample Data
# =============================================================================

SAMPLE_ITEMS = [
    Item(
        id=1,
        name="Wireless Keyboard",
        description="Ergonomic wireless keyboard with backlit keys",
        price=Decimal("79.99"),
        quantity=150,
        created_at=datetime(2024, 1, 15, 10, 30, 0),
        updated_at=datetime(2024, 1, 15, 10, 30, 0),
    ),
    Item(
        id=2,
        name="USB-C Hub",
        description="7-in-1 USB-C hub with HDMI and ethernet",
        price=Decimal("49.99"),
        quantity=75,
        created_at=datetime(2024, 1, 16, 14, 20, 0),
        updated_at=datetime(2024, 1, 18, 9, 15, 0),
    ),
    Item(
        id=3,
        name="Mechanical Mouse",
        description="Gaming mouse with RGB lighting and 6 programmable buttons",
        price=Decimal("59.99"),
        quantity=200,
        created_at=datetime(2024, 1, 17, 8, 45, 0),
        updated_at=datetime(2024, 1, 17, 8, 45, 0),
    ),
    Item(
        id=4,
        name="Monitor Stand",
        description="Adjustable aluminum monitor stand with storage drawer",
        price=Decimal("89.99"),
        quantity=50,
        created_at=datetime(2024, 1, 18, 11, 0, 0),
        updated_at=datetime(2024, 1, 20, 16, 30, 0),
    ),
    Item(
        id=5,
        name="Webcam HD",
        description="1080p HD webcam with built-in microphone",
        price=Decimal("69.99"),
        quantity=120,
        created_at=datetime(2024, 1, 19, 9, 30, 0),
        updated_at=datetime(2024, 1, 19, 9, 30, 0),
    ),
]

SAMPLE_ITEM_DICTS = [
    {
        "name": "Wireless Keyboard",
        "description": "Ergonomic wireless keyboard with backlit keys",
        "price": 79.99,
        "quantity": 150,
    },
    {
        "name": "USB-C Hub",
        "description": "7-in-1 USB-C hub with HDMI and ethernet",
        "price": 49.99,
        "quantity": 75,
    },
    {
        "name": "Mechanical Mouse",
        "description": "Gaming mouse with RGB lighting and 6 programmable buttons",
        "price": 59.99,
        "quantity": 200,
    },
    {
        "name": "Monitor Stand",
        "description": "Adjustable aluminum monitor stand with storage drawer",
        "price": 89.99,
        "quantity": 50,
    },
    {
        "name": "Webcam HD",
        "description": "1080p HD webcam with built-in microphone",
        "price": 69.99,
        "quantity": 120,
    },
]


# =============================================================================
# Factory Functions
# =============================================================================

def create_sample_item(
    id: Optional[int] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    price: Optional[float] = None,
    quantity: Optional[int] = None,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
) -> Item:
    """
    Create a sample item with optional overrides.

    Args:
        id: Item ID (default: random)
        name: Item name (default: random)
        description: Item description (default: random)
        price: Item price (default: random between 10-500)
        quantity: Item quantity (default: random between 1-1000)
        created_at: Creation timestamp (default: now)
        updated_at: Update timestamp (default: now)

    Returns:
        A new Item instance.
    """
    now = datetime.now()

    return Item(
        id=id or random.randint(1, 10000),
        name=name or f"Test Item {_random_string(6)}",
        description=description or f"Description for test item {_random_string(10)}",
        price=Decimal(str(price)) if price else Decimal(str(round(random.uniform(10, 500), 2))),
        quantity=quantity if quantity is not None else random.randint(1, 1000),
        created_at=created_at or now,
        updated_at=updated_at or now,
    )


def create_sample_items(count: int = 5) -> list[Item]:
    """
    Create multiple sample items.

    Args:
        count: Number of items to create.

    Returns:
        List of Item instances.
    """
    items = []
    base_time = datetime.now()

    for i in range(count):
        created_at = base_time - timedelta(days=count - i)
        items.append(
            create_sample_item(
                id=i + 1,
                created_at=created_at,
                updated_at=created_at + timedelta(hours=random.randint(0, 48)),
            )
        )

    return items


def generate_random_item() -> dict:
    """
    Generate a random item dictionary for API requests.

    Returns:
        Dictionary suitable for POST/PUT requests.
    """
    categories = ["Electronics", "Office", "Gaming", "Accessories", "Storage"]
    adjectives = ["Premium", "Professional", "Ultra", "Essential", "Advanced"]
    nouns = ["Adapter", "Cable", "Dock", "Mount", "Charger", "Case", "Stand"]

    name = f"{random.choice(adjectives)} {random.choice(nouns)}"

    return {
        "name": name,
        "description": f"High-quality {name.lower()} for {random.choice(categories).lower()} use",
        "price": round(random.uniform(9.99, 299.99), 2),
        "quantity": random.randint(10, 500),
    }


# =============================================================================
# Helper Functions
# =============================================================================

def _random_string(length: int) -> str:
    """Generate a random alphanumeric string."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))
