from qwen_agent.tools.base import register_tool

from .tools.knowledge_base_tool import RAGTool
from .tools.sql_tool import SQLTool
from .tools.weather_tool import WeatherTool
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
    register_tool('get_weather')(WeatherTool)
    register_tool('execute_sql_query')(SQLTool)
    register_tool('search_knowledge_base')(RAGTool)

    # Run Q&A loop
    while True:
        try:
            query = input("Ask me anything (or press Enter to exit): ").strip()
            if not query:
                print("Goodbye!\n")
                break
            
            print("\nThinking... 🤔\n")
            result = router.route_query(query)

            print("--- Tool Used ---")
            print(result.get("tool", "Unknown Tool"), "\n")

            if result.get("success"):
                # 通用输出
                print("--- Assistant Answer ---\n")

                # 优先打印分析性回答
                if "answer" in result:
                    print(result["answer"], "\n")

                # 如果有数据（SQL结果等），展示前几行
                if "data" in result:
                    rows = result["data"]
                    print(f"Returned {len(rows)} rows\n")
                    for row in rows[:5]:  # 只显示前5行
                        print("  ", row)

                # 知识库结果
                elif "knowledge_base_results" in result:
                    for i, item in enumerate(result["knowledge_base_results"][:3]):
                        print(f"Result {i+1} from {item['source']}:")
                        print(item["content"][:200] + ("..." if len(item["content"]) > 200 else ""))
                        print()

                # 天气信息
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
