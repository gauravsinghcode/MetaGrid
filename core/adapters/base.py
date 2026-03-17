class BaseAdapter:

    def inspect_schema(self):
        raise NotImplementedError
    
    def get_columns(self, table_name):
        raise NotImplementedError
    
    def excute(self, query, params=None):
        raise NotImplementedError
    
