"""
Quick test to verify the semantic analysis API endpoint is working
"""
import requests
import json

def test_semantic_api():
    url = "http://localhost:8000/analyzeSemantic"
    
    code = """
    piece of x, y, z;
    sip of temperature = 98.6;
    flag of isReady;
    
    start() {
        piece of count;
        bill(x);
    }
    """
    
    print("Testing Semantic Analysis API")
    print("=" * 80)
    print("\nCode:")
    print(code)
    print("\n" + "=" * 80)
    
    try:
        response = requests.post(
            url,
            json={"code": code},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse:")
            print(json.dumps(data, indent=2))
            
            if data.get("success"):
                print("\n✓ Semantic analysis succeeded!")
                print(f"\nIngredients: {len(data.get('ingredients', []))}")
                print(f"Recipes: {len(data.get('recipes', []))}")
            else:
                print("\n✗ Semantic analysis failed")
                print(f"Message: {data.get('message')}")
        else:
            print(f"\n✗ HTTP Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    test_semantic_api()
