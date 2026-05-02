from engine import ACTX

if __name__ == "__main__":
    engine = ACTX()
    print("--- ACTX CLI MODE ---")
    while True:
        target = input("\nEnter actor name (or 'exit'): ").strip()
        if target.lower() == 'exit': break
        
        data = engine.search_actor(target)
        if data and "error" not in data:
            print(f"Result: {data['name']} | IMDb: {data['imdb_id']}")
        else:
            print("[!] Not found or Error occurred.")