import os
from db.db_manager import execute_many, execute_query
from dotenv import load_dotenv

load_dotenv()

def seed_keywords():
    print("Seeding keywords...")
    
    # 1. Skin Types
    skin_types = [
        ("skin_type", "건성", "dry"),
        ("skin_type", "지성", "oily"),
        ("skin_type", "복합성", "combination"),
        ("skin_type", "중성", "normal"),
        ("skin_type", "민감성", "sensitive"),
    ]
    
    # 2. Skin Concerns (Based on UI image)
    skin_concerns = [
        ("skin_concern", "각질", "dead_skin"),
        ("skin_concern", "건조", "dryness"),
        ("skin_concern", "모공", "pore"),
        ("skin_concern", "미백", "brightening"),
        ("skin_concern", "민감", "sensitive_concern"),
        ("skin_concern", "블랙헤드", "blackhead"),
        ("skin_concern", "아토피", "atopy"),
        ("skin_concern", "유분", "oiliness"),
        ("skin_concern", "장벽", "barrier"),
        ("skin_concern", "주름", "wrinkle"),
        ("skin_concern", "트러블", "trouble"),
        ("skin_concern", "피지", "sebum"),
        ("skin_concern", "흉터", "scar"),
    ]

    # 3. Gender
    genders = [
        ("gender", "남성", "male"),
        ("gender", "여성", "female"),
    ]

    all_keywords = skin_types + skin_concerns + genders
    
    try:
        # Check if already seeded to avoid unique constraint error
        existing = execute_query("SELECT COUNT(*) as count FROM keywords")
        if existing and existing[0]['count'] > 0:
            print(f"Keywords table already has {existing[0]['count']} entries. Skipping seed.")
            return

        execute_many(
            "INSERT INTO keywords (type, label, keyword) VALUES (%s, %s, %s)",
            all_keywords
        )
        print(f"Successfully seeded {len(all_keywords)} keywords.")
    except Exception as e:
        print(f"Error seeding keywords: {e}")

if __name__ == "__main__":
    seed_keywords()
