from .core.knowledge_base import KnowledgeBaseManager
from .core.rag_engine import RAGEngine
from .core.query_router import QueryRouter
from .config import DOCS_DIR, IMG_DIR


def main():
    # Initialize knowledge base
    kb_manager = KnowledgeBaseManager()
    metadata_store, text_index, image_index = kb_manager.build_or_load_knowledge_base(DOCS_DIR, IMG_DIR)
    
    print("\n=============================================")
    print("Your Intelligent Q&A Assistant is Ready 🚀")
    print("=============================================\n")

    # Initialize RAG engine and query router
    rag_engine = RAGEngine()
    router = QueryRouter(rag_engine, metadata_store, text_index, image_index)

    # Run Q&A loop
    while True:
        try:
            query = input("Ask me anything (or press Enter to exit): ").strip()
            if not query:
                print("Goodbye!\n")
                break
            
            print("\nThinking... 🤔\n")
            result = router.route_query(query)
            print("\n--- Result ---\n")
            print(result)

            if result.get("success"):
                # General output
                print("--- Assistant Answer ---\n")

                # Prioritize analytical responses
                if "answer" in result:
                    print(result["answer"], "\n")

                # If there is data (SQL results, etc.), show the first few rows\n                if \"data\" in result:\n                    rows = result[\"data\"]\n                    print(f\"Returned {len(rows)} rows\\n\")\n                    for row in rows[:5]:  # Only show first 5 rows\n                        print(\"  \", row)

                # Knowledge base results
                elif "knowledge_base_results" in result:
                    for i, item in enumerate(result["knowledge_base_results"][:3]):
                        print(f"Result {i+1} from {item['source']}:")
                        print(item["content"][:200] + ("..." if len(item["content"]) > 200 else ""))
                        print()

                # Weather information
                elif "weather_data" in result:
                    w = result["weather_data"]
                    print(f"Weather in {w['location']}, {w['country']}: {w['description']}")
                    print(f"Temperature: {w['temperature']}°C (feels like {w['feels_like']}°C)")
                    print(f"Humidity: {w['humidity']}% | Pressure: {w['pressure']} hPa | Wind: {w['wind_speed']} m/s\n")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}\n")

            print("\n-----------------------------------------\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!\n")
            break
        except Exception as e:
            print(f"⚠️ Error: {str(e)}\n")


if __name__ == "__main__":
    main()
