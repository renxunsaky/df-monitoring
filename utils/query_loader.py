import os

class QueryLoader:
    def __init__(self, query_dir='queries'):
        self.queries = {}
        self.load_queries(query_dir)

    def load_queries(self, query_dir):
        """Load all SQL queries from .sql files"""
        for file_name in os.listdir(query_dir):
            if file_name.endswith('.sql'):
                file_path = os.path.join(query_dir, file_name)
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Split content by -- name: and process each query
                    query_blocks = content.split('-- name:')
                    for block in query_blocks[1:]:  # Skip first empty block
                        lines = block.strip().split('\n')
                        query_name = lines[0].strip()
                        query_content = '\n'.join(lines[1:]).strip()
                        self.queries[query_name] = query_content

    def get_query(self, query_name):
        """Get a query by its name"""
        return self.queries.get(query_name) 