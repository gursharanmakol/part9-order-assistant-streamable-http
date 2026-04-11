import json
import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


def data_path() -> Path:
    base_dir = Path(__file__).resolve().parent
    raw = os.getenv("DATA_PATH", "./data/orders.json")
    p = Path(raw)
    if not p.is_absolute():
        p = base_dir / p
    return p.resolve()


def main() -> None:
    path = data_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    # Reset from scratch on every run for deterministic demos.
    data = {
        "orders": [
            {
                "id": "ORD-10042",
                "status": "shipped",
                "carrier": "FedEx",
                "delivery_estimate": "2026-03-28",
                "created_at": "2026-03-24T10:15:00Z",
                "cancelled": False,
                "items": [
                    {"name": "Wireless Headphones", "quantity": 1, "price": 79.99},
                    {"name": "Phone Case", "quantity": 2, "price": 12.99},
                ],
            },
            {
                "id": "ORD-10099",
                "status": "processing",
                "carrier": "UPS",
                "delivery_estimate": "2026-03-30",
                "created_at": "2026-03-25T14:40:00Z",
                "cancelled": False,
                "items": [
                    {"name": "Bluetooth Speaker", "quantity": 1, "price": 49.99},
                ],
            },
            {
                "id": "ORD-10110",
                "status": "delivered",
                "carrier": "USPS",
                "delivery_estimate": "2026-03-26",
                "created_at": "2026-03-22T09:05:00Z",
                "cancelled": False,
                "items": [
                    {"name": "Laptop Stand", "quantity": 1, "price": 34.99},
                ],
            },
        ]
    }

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")

    print(f"Seeded orders to: {path}")


if __name__ == "__main__":
    main()
