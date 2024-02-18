from typing import Dict

from fetchfox.constants.specials import GHOST_BIBLE, STRABBLE_BIBLE


class AssetDTO:
    def __init__(self, collection_id: str, asset_id: str, metadata: dict):
        self.collection_id: str = collection_id
        self.asset_id: str = asset_id
        self.metadata: dict = metadata

    @property
    def name(self) -> str:
        return self.metadata["name"]

    @property
    def title(self) -> str:
        if "Book Title" in self.metadata:
            return self.metadata["Book Title"][0]

        return self.metadata["name"].split(" #")[0]

    @property
    def number(self) -> str:
        try:
            return int(self.metadata["name"].split(" #")[-1])
        except:
            return None

    @property
    def quantity(self) -> int:
        return int(self.metadata.get("quantity", "1"))

    @property
    def cover_theme(self) -> str:
        attributes = self.metadata.get("attributes") or self.metadata.get("properties") or {}

        if not attributes:
            return "none"

        if "Cover Theme" in attributes:
            return attributes["Cover Theme"].split(" / ")[-1]

        if "Edition" in attributes:
            return attributes["Edition"]

        trait_count = 0

        for attribute in attributes.values():
            if isinstance(attribute, str):
                trait_count += 1
            elif isinstance(attribute, list):
                trait_count += len(attribute)

        return f"Traits: {trait_count}"

    @property
    def cover_variation(self) -> str:
        attributes = self.metadata.get("attributes") or self.metadata.get("properties") or {}

        if not attributes:
            return None

        try:
            return int(attributes["Variation"].split(" / ")[-1])
        except:
            return None

    @property
    def files(self) -> Dict[str, str]:
        return {item["name"]: item["src"] for item in self.metadata.get("files", [])}

    def image_url(self, https: bool = False, highres: bool = False) -> str:
        url = None

        if highres:
            url = self.files.get("High-Res Cover Image")

        if not url:
            url = self.metadata.get("image") or self.metadata.get("media_url")

        if https and url:
            url = url.replace("ipfs://", "https://ipfs.io/ipfs/")

        return url

    @property
    def special(self) -> str:
        attributes = self.metadata.get("attributes") or self.metadata.get("properties") or {}

        if not attributes:
            return None

        if self.metadata["name"].startswith("Gutenberg Bible"):
            dots = attributes.get("Dots", [])
            black_knot = attributes.get("Black_Knot", [])

            specials = []

            if "Dots_Middle" in dots and "Dots_ADA" not in dots:
                specials.append(GHOST_BIBLE)

            if "Black_Knot_Outer_Ring_Stroke" in black_knot and "Black_Knot_Inner_Ring_Stroke" not in black_knot:
                specials.append(STRABBLE_BIBLE)

            if specials:
                return " - ".join(specials)

        return attributes.get("Special")

    @property
    def emoji(self) -> str:
        emojis = ""

        if GHOST_BIBLE in (self.special or ""):
            emojis += "👻"

        if STRABBLE_BIBLE in (self.special or ""):
            emojis += "🖌"

        if self.special in ["Bonus story in book", "Bonus chapter in book"]:
            emojis += "📖"

        return emojis if len(emojis) > 0 else None

    def __repr__(self) -> str:
        return f"{self.title} {self.number} [{self.cover_theme} / {self.cover_variation}]"
