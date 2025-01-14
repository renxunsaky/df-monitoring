import os
import yaml

class QueryLoader:
    def __init__(self, config_path='/config/queries.yaml'):
        self.queries = {}
        self.load_queries(config_path)

    def load_queries(self, config_path):
        """Load queries from YAML configuration"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.queries = config.get('queries', {})
        except Exception as e:
            raise Exception(f"Failed to load queries config: {str(e)}")

    def get_query(self, query_name):
        """Get a query by its name"""
        query_config = self.queries.get(query_name)
        if query_config:
            return query_config.get('query')
        return None

    def get_query_names(self):
        """Get list of available queries"""
        return list(self.queries.keys())

    def get_query_description(self, query_name):
        """Get query description"""
        query_config = self.queries.get(query_name)
        if query_config:
            return query_config.get('description')
        return None 