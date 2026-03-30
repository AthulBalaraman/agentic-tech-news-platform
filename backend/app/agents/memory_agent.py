from typing import List
from ..models.raw_data import RawData
from ..core.vector_store import vector_store

class MemoryAgent:
    def filter_duplicates(self, new_items: List[RawData], threshold: float = 0.15) -> List[RawData]:
        unique_items = []
        for item in new_items:
            # We use the title + description as the context for semantic check
            text_to_check = f"{item.title} {item.content[:1000]}"
            
            results = vector_store.search_similar(text=text_to_check, n_results=1)
            
            # If nothing in DB yet
            if not results.get("distances") or not results["distances"][0]:
                unique_items.append(item)
                continue
                
            distance = results["distances"][0][0]
            
            # Cosine distance: closer to 0 means more similar
            # If distance is greater than threshold, it's considered novel/unique
            if distance > threshold:
                unique_items.append(item)
            else:
                print(f"🧠 Memory Agent filtering duplicate insight: {item.title} (Distance: {distance:.3f})")
                
        return unique_items
