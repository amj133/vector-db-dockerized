import os
import anthropic
from dotenv import load_dotenv
from setup_vector_db import setup_vector_db

load_dotenv()

def get_user_input():
    """Get question, k value, and whether to use Claude from user"""
    print("\n" + "="*60)
    question = input("\033[33mEnter your question about the documents: \033[0m").strip()  # Softer yellow
    
    if not question:
        return None, None, False
    
    while True:
        try:
            k = input("How many similar results do you want? (default=3): ").strip()
            if not k:
                k = 3
            else:
                k = int(k)
            
            if k <= 0:
                print("Please enter a positive number.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")
    
    # Ask if user wants Claude response
    use_claude = input("Get Claude's answer? (y/N): ").strip().lower()
    use_claude = use_claude in ['y', 'yes']
    
    return question, k, use_claude

def get_claude_response(context_for_llm):
    """Send context to Claude API and get response with token usage and cost estimates"""
    try:
        # Get API key from environment
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return "❌ Error: ANTHROPIC_API_KEY not found in environment variables.", None
        
        # Initialize Claude client
        client = anthropic.Anthropic(api_key=api_key)
        
        print(f"\033[36m🤖 Asking Claude for analysis...\033[0m")
        
        # Send to Claude
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[
                {
                    "role": "user", 
                    "content": context_for_llm
                }
            ]
        )
        
        # Extract token usage
        usage = response.usage
        input_tokens = usage.input_tokens
        output_tokens = usage.output_tokens
        total_tokens = input_tokens + output_tokens
        
        # Claude 3.5 Sonnet pricing estimates (as of late 2024)
        # These are reasonable estimates - actual pricing may vary
        pricing_estimates = {
            "conservative": {"input": 0.000003, "output": 0.000015},  # $3/$15 per 1M tokens
            "moderate": {"input": 0.000004, "output": 0.000020},      # $4/$20 per 1M tokens  
            "premium": {"input": 0.000005, "output": 0.000025}        # $5/$25 per 1M tokens
        }
        
        # Calculate costs for different estimates
        cost_estimates = {}
        for scenario, prices in pricing_estimates.items():
            input_cost = input_tokens * prices["input"]
            output_cost = output_tokens * prices["output"]
            total_cost = input_cost + output_cost
            cost_estimates[scenario] = {
                "input": input_cost,
                "output": output_cost,
                "total": total_cost
            }
        
        # Format token usage info
        token_info = f"""
\033[36m📊 TOKEN USAGE & COST ESTIMATES:\033[0m
Input tokens:  {input_tokens:,}
Output tokens: {output_tokens:,}
Total tokens:  {total_tokens:,}

💰 Cost Estimates:
Conservative: ${cost_estimates['conservative']['total']:.6f} (${cost_estimates['conservative']['input']:.6f} + ${cost_estimates['conservative']['output']:.6f})
Moderate:     ${cost_estimates['moderate']['total']:.6f} (${cost_estimates['moderate']['input']:.6f} + ${cost_estimates['moderate']['output']:.6f})
Premium:      ${cost_estimates['premium']['total']:.6f} (${cost_estimates['premium']['input']:.6f} + ${cost_estimates['premium']['output']:.6f})
"""
        
        print(token_info)
        
        return response.content[0].text
        
    except Exception as e:
        return f"❌ Error calling Claude API: {e}", None

def load_system_context():
    """Load the system context from manifest file"""
    context_file = "context.md"
    try:
        with open(context_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"\033[36m⚠️  Warning: {context_file} not found. Using basic context.\033[0m")
        return "You are answering questions about a supply chain finance web application."
    except Exception as e:
        print(f"\033[36m⚠️  Warning: Could not load {context_file}: {e}\033[0m")
        return ""
    
def search_with_context(vectordb, question, k=3):
    """Search the vector database and combine with system context"""
    try:
        # Get relevant chunks from vector search
        results_with_scores = vectordb.similarity_search_with_score(question, k=k)
        
        # Load system context
        system_context = load_system_context()
        
        # Format the complete context for LLM
        if results_with_scores:
            relevant_docs = "\n\n".join([
                f"--- Document Chunk (Score: {score:.3f}) ---\n"
                f"Source: {chunk.metadata.get('source', 'Unknown')}\n"
                f"Content: {chunk.page_content}"
                for chunk, score in results_with_scores
            ])
            
            complete_context = f"""
{system_context}

## Relevant Documentation Found:
{relevant_docs}

## User Question:
{question}

## Instructions:
Answer the user's question using the relevant documentation above, keeping in mind the system context. If the documentation doesn't contain enough information to fully answer the question, say so clearly.
"""
        else:
            complete_context = f"""
{system_context}

## User Question:
{question}

## Instructions:
No relevant documentation was found for this question. Please let the user know that you couldn't find specific information about their question in the knowledge base.
"""
        
        return complete_context, results_with_scores
        
    except Exception as e:
        print(f"❌ Error searching with context: {e}")
        return None, []


def display_results_with_context(question, context_for_llm, results, claude_response=None, llm_used=False):
    """Display search results, LLM-ready context, and Claude's response"""
    print(f"\n{'='*60}")
    print(f"\033[93mQUESTION: {question}\033[0m")  # Yellow
    print(f"{'='*60}")
    
    # Show Claude's response first (most important)
    if claude_response:
        print(f"\n\033[95m--- CLAUDE'S ANSWER ---\033[0m")  # Magenta
        print(claude_response)
        print("-" * 60)
    
    if not results:
        print("No relevant documents found in vector database.")
    else:
        print(f"\n\033[92m--- VECTOR SEARCH RESULTS ---\033[0m")  # Green
        for i, (chunk, distance_score) in enumerate(results, 1):
            print(f"\n\033[92mRESULT {i}:\033[0m")  # Green
            print(f"Distance Score: {distance_score:.3f} (lower = more similar)")
            print(f"Content: {chunk.page_content}")
            source = chunk.metadata.get('source', 'Unknown')
            print(f"Source: {source}")
            print("-" * 40)

    if llm_used:
        # Show raw context at the bottom (for debugging)
        print(f"\n\033[94m--- RAW CONTEXT SENT TO CLAUDE ---\033[0m")  # Blue
        print("(For debugging - this was sent to the API)")
        print("-" * 60)
        print(context_for_llm)
        print("-" * 60)

def main():
    """Main application loop"""
    print("🔍 Document Search System (PostgreSQL + pgvector)")
    print("🐳 Running in Docker container")
    print("="*60)
    
    # Set up the vector database
    try:
        vectordb = setup_vector_db()
        if vectordb is None:
            print("\n💡 Setup help:")
            print("1. Make sure PostgreSQL container is running")
            print("2. Check that documents are in ./documents/ directory")
            print("3. Verify database connection string")
            return
    except Exception as e:
        print(f"❌ Error setting up the system: {e}")
        return
    
    print("✅ System ready! Your vector database persists in PostgreSQL.")
    print("💾 Database will only rebuild when documents change.")
    print("🔄 Add new documents to ./documents/ and restart to update.")
    print("Type 'quit', 'exit', or press Ctrl+C to stop.\n")
    
    # Main interaction loop
    while True:
        try:
            question, k, use_claude = get_user_input()
            
            if not question:
                print("Please enter a question.")
                continue
            
            # Check for exit commands
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            # Search and display results
            print(f"\n🔍 Searching PostgreSQL vector database for '{question}'...")
            context_for_llm, results = search_with_context(vectordb, question, k)
            
            claude_response = None
            if context_for_llm:
                if use_claude:
                    claude_response = get_claude_response(context_for_llm)

                display_results_with_context(question, context_for_llm, results, claude_response, use_claude)
            else:
                print("❌ Search failed. Please try again.")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()
