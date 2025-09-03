from dotenv import load_dotenv
load_dotenv()

# loading documents from directory
from langchain_community.document_loaders import DirectoryLoader, TextLoader
import os

# chunking document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# embedding models to leverage
from langchain.embeddings import HuggingFaceEmbeddings

# import vector database - POSTGRESQL VERSION
from langchain_postgres import PGVector
import hashlib
import time

import anthropic

def get_connection_string():
    """Get PostgreSQL connection string from environment or default"""
    return os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/vectordb')

def get_documents_hash(documents_dir):
    """Create a hash of all document contents to detect changes"""
    hash_md5 = hashlib.md5()
    
    text_files = [f for f in os.listdir(documents_dir) if f.endswith(('.txt', '.md'))]
    text_files.sort()  # Ensure consistent ordering
    
    for filename in text_files:
        file_path = os.path.join(documents_dir, filename)
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
        except Exception as e:
            print(f"\033[36m  Warning: Could not hash {filename}: {e}\033[0m")
    
    return hash_md5.hexdigest()

def check_database_exists(connection_string, collection_name):
    """Check if the vector database collection already exists"""
    try:
        # Try to connect and check if collection exists
        temp_vectordb = PGVector(
            connection_string=connection_string,
            collection_name=collection_name,
            embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        )
        
        # Try a simple query to see if data exists
        test_results = temp_vectordb.similarity_search("test", k=1)
        return len(test_results) > 0
        
    except Exception:
        return False

def wait_for_database(connection_string, max_retries=30, delay=2):
    """Wait for PostgreSQL to be ready"""
    print(f"\033[36m⏳ Waiting for PostgreSQL to be ready...\033[0m")
    
    for i in range(max_retries):
        try:
            import psycopg
            # Convert psycopg3 connection string to basic format for testing
            test_conn_string = connection_string.replace('postgresql+psycopg://', 'postgresql://')
            conn = psycopg.connect(test_conn_string)
            conn.close()
            print(f"\033[36m✅ PostgreSQL is ready!\033[0m")
            return True
        except Exception as e:
            if i < max_retries - 1:
                print(f"\033[36m⏳ Waiting... ({i+1}/{max_retries})\033[0m")
                time.sleep(delay)
            else:
                print(f"❌ Could not connect to PostgreSQL after {max_retries} attempts: {e}")
                return False
    return False

def setup_vectordb():
    """Set up the vector database with all documents from the documents directory"""
    documents_dir = "documents"
    collection_name = "document_search"
    connection_string = get_connection_string()
    
    # Wait for database to be ready (important in Docker)
    if not wait_for_database(connection_string):
        return None
    
    # Check if documents directory exists
    if not os.path.exists(documents_dir):
        print(f"❌ Error: '{documents_dir}' directory not found!")
        print(f"Please create a '{documents_dir}' directory and add your text files there.")
        return None
    
    # Check if directory has any .txt or .md files
    text_files = [f for f in os.listdir(documents_dir) if f.endswith(('.txt', '.md'))]
    if not text_files:
        print(f"❌ Error: No .txt or .md files found in '{documents_dir}' directory!")
        print(f"Please add some .txt or .md files to the '{documents_dir}' directory.")
        return None
    
    print(f"\033[36mFound {len(text_files)} files: {', '.join(text_files)}\033[0m")
    
    # Get current document hash
    current_hash = get_documents_hash(documents_dir)
    hash_file = "data/document_hash.txt"  # Store in data directory for persistence
    os.makedirs("data", exist_ok=True)
    
    # Check if we need to rebuild the database
    rebuild_needed = True
    if os.path.exists(hash_file) and check_database_exists(connection_string, collection_name):
        try:
            with open(hash_file, 'r') as f:
                stored_hash = f.read().strip()
            
            if stored_hash == current_hash:
                print(f"\033[36m✓ Documents unchanged, using existing database\033[0m")
                rebuild_needed = False
            else:
                print(f"\033[36m📝 Documents changed, rebuilding database\033[0m")
        except:
            print(f"\033[36m🔄 Hash file issue, rebuilding database\033[0m")
    else:
        print(f"\033[36m🆕 Building new database\033[0m")
    
    # Create embedding function
    print(f"\033[36m🤖 Loading embedding model...\033[0m")
    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    if not rebuild_needed:
        # Use existing database
        try:
            vectordb = PGVector(
                connection_string=connection_string,
                collection_name=collection_name,
                embedding_function=embedding
            )
            print(f"\033[36m✅ Connected to existing database\033[0m")
            return vectordb
        except Exception as e:
            print(f"\033[36m⚠️  Could not connect to existing database: {e}\033[0m")
            print(f"\033[36m🔄 Rebuilding...\033[0m")
            rebuild_needed = True
    
    if rebuild_needed:
        print(f"\033[36mLoading and processing documents...\033[0m")
        
        # Load all .txt and .md files from the documents directory
        txt_loader = DirectoryLoader(documents_dir, glob="*.txt", loader_cls=TextLoader)
        md_loader = DirectoryLoader(documents_dir, glob="*.md", loader_cls=TextLoader)
        
        txt_data = txt_loader.load()
        md_data = md_loader.load()
        data = txt_data + md_data
        
        print(f"\033[36mLoaded {len(data)} documents\033[0m")
        
        if len(data) == 0:
            print("❌ Error: Could not load any documents!")
            return None
        
        # Debug: Show which files were actually loaded
        for i, doc in enumerate(data):
            source = doc.metadata.get('source', 'Unknown')
            content_preview = doc.page_content[:100].replace('\n', ' ')
            print(f"\033[36m  Document {i+1}: {source}\033[0m")
            print(f"\033[36m    Preview: {content_preview}...\033[0m")
            print()

        # Chunk documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=100,
            chunk_overlap=20,
            length_function=len,
        )

        chunks = text_splitter.split_documents(data)
        print(f"\033[36mDocuments split into {len(chunks)} chunks\033[0m")

        if len(chunks) == 0:
            print("❌ Error: No chunks created!")
            return None

        # Create vector database
        print("\033[36mCreating embeddings and storing in PostgreSQL... (this may take a moment)\033[0m")
        
        try:
            # Drop existing collection if it exists
            try:
                temp_vectordb = PGVector(
                    embeddings=embedding,
                    connection=connection_string,
                    collection_name=collection_name
                )
                temp_vectordb.delete_collection()
                print(f"\033[36m🗑️  Cleared existing collection\033[0m")
            except:
                pass  # Collection might not exist
            
            # Create new vector database
            vectordb = PGVector.from_documents(
                documents=chunks,
                embedding=embedding,
                connection=connection_string,
                collection_name=collection_name
            )
            
            # Save the current hash
            with open(hash_file, 'w') as f:
                f.write(current_hash)
            
            print(f"\033[36m✅ Vector database created successfully in PostgreSQL!\033[0m")
            return vectordb
            
        except Exception as e:
            print(f"❌ Error creating PostgreSQL vector database: {e}")
            print("Make sure PostgreSQL is running and pgvector extension is installed")
            return None

def search_policies(vectordb, question, k=3):
    """Search the vector database for chunks similar to the question"""
    try:
        results_with_scores = vectordb.similarity_search_with_score(question, k=k)
        return results_with_scores
    except Exception as e:
        print(f"❌ Error searching database: {e}")
        return []

def display_results(question, results):
    """Display search results in a nice format"""
    print(f"\n{'='*60}")
    print(f"\033[93mQUESTION: {question}\033[0m")  # Yellow
    print(f"{'='*60}")
    
    if not results:
        print("No results found.")
        return
    
    for i, (chunk, distance_score) in enumerate(results, 1):
        print(f"\n\033[92m--- RESULT {i} ---\033[0m")  # Green
        print(f"Distance Score: {distance_score:.3f} (lower = more similar)")
        print(f"Content: {chunk.page_content}")
        # Show source file
        source = chunk.metadata.get('source', 'Unknown')
        print(f"Source: {source}")
        print("-" * 40)

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
        vectordb = setup_vectordb()
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
