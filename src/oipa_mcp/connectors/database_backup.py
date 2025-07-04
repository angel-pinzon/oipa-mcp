"""
"""
Oracle Database connector for OIPA

Handles direct database connections to OIPA Oracle database.
Provides async query execution and connection pooling.

Based on OIPA table structure analysis from documentation.
"""

import asyncio
import oracledb
from typing import List, Dict, Any, Optional, Union
from contextlib import asynccontextmanager
from loguru import logger

from ..config import Config


class OipaDatabase:
    """
    Async Oracle database connector for OIPA
    
    Provides connection pooling, query execution, and transaction management
    for accessing OIPA data directly from Oracle database.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self._pool: Optional[oracledb.ConnectionPool] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the database connection pool"""
        if self._initialized:
            return
            
        try:
            # Configure oracledb for thick mode if Oracle Client is available
            # Otherwise it will use thin mode (pure Python)
            try:
                oracledb.init_oracle_client()
                logger.info("Using Oracle Client (thick mode)")
            except Exception:
                logger.info("Using thin mode (no Oracle Client required)")
            
            # Create connection pool
            self._pool = oracledb.create_pool(
                user=self.config.database.username,
                password=self.config.database.password,
                dsn=self.config.database.dsn,
                min=self.config.database.pool_min_size,
                max=self.config.database.pool_max_size,
                increment=1,
                encoding="UTF-8"
            )
            
            self._initialized = True
            logger.info(f"Database pool initialized: {self.config.database.dsn}")
            
        except oracledb.Error as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def close(self) -> None:
        """Close the database connection pool"""
        if self._pool:
            self._pool.close()
            self._pool = None
            self._initialized = False
            logger.info("Database pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection from the pool"""
        if not self._initialized:
            await self.initialize()
            
        connection = None
        try:
            # Get connection from pool
            connection = self._pool.acquire()
            yield connection
        except oracledb.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection:
                connection.close()
    
    async def execute_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None,
        fetch_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as list of dictionaries
        
        Args:
            query: SQL query string
            parameters: Query parameters
            fetch_size: Maximum number of rows to fetch
            
        Returns:
            List of dictionaries representing query results
        """
        async with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Set fetch size if specified
                if fetch_size:
                    cursor.arraysize = min(fetch_size, self.config.performance.max_query_results)
                
                # Execute query with parameters
                if parameters:
                    cursor.execute(query, parameters)
                else:
                    cursor.execute(query)
                
                # Fetch results
                columns = [col[0].lower() for col in cursor.description]
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                results = []
                for row in rows:
                    results.append(dict(zip(columns, row)))
                
                logger.debug(f"Query executed successfully, returned {len(results)} rows")
                return results
                
            except oracledb.Error as e:
                logger.error(f"Query execution error: {e}")
                logger.error(f"Query: {query}")
                logger.error(f"Parameters: {parameters}")
                raise
            finally:
                cursor.close()
    
    async def execute_single_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a query expecting a single result
        
        Returns:
            Single dictionary or None if no results
        """
        results = await self.execute_query(query, parameters, fetch_size=1)
        return results[0] if results else None
    
    async def execute_scalar(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute a query expecting a single scalar value
        
        Returns:
            Single value or None
        """
        result = await self.execute_single_query(query, parameters)
        if result:
            # Return first column value
            return next(iter(result.values()))
        return None
    
    async def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            result = await self.execute_scalar("SELECT 1 FROM DUAL")
            return result == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


class OipaQueryBuilder:
    """
    Query builder for common OIPA database queries
    
    Provides pre-built, tested queries for common OIPA operations
    based on the documented table structure.
    """
    
    # Common table aliases
    POLICY_TABLES = """
        AsPolicy p
        LEFT JOIN AsRole r ON p.PolicyGUID = r.PolicyGUID AND r.RoleCode = '01'
        LEFT JOIN AsClient c ON r.ClientGUID = c.ClientGUID
    """
    
    @staticmethod
    def search_policies(
        search_term: Optional[str] = None,
        status_filter: Optional[str] = None,
        limit: int = 50
    ) -> tuple[str, Dict[str, Any]]:
        """
        Build query to search policies by various criteria
        
        Returns:
            Tuple of (query_string, parameters)
        """
        base_query = f"""
            SELECT 
                p.PolicyGUID as policy_guid,
                p.PolicyNumber as policy_number,
                p.PolicyName as policy_name,
                p.StatusCode as status_code,
                p.PlanDate as plan_date,
                p.UpdatedGmt as updated_date,
                c.ClientGUID as client_guid,
                c.FirstName as client_first_name,
                c.LastName as client_last_name,
                c.CompanyName as company_name,
                c.TaxID as tax_id
            FROM {OipaQueryBuilder.POLICY_TABLES}
        """
        
        conditions = []
        parameters = {}
        
        # Add search term conditions
        if search_term:
            search_conditions = [
                "UPPER(p.PolicyNumber) LIKE UPPER(:search_term)",
                "UPPER(c.FirstName) LIKE UPPER(:search_term)",
                "UPPER(c.LastName) LIKE UPPER(:search_term)", 
                "UPPER(c.CompanyName) LIKE UPPER(:search_term)",
                "UPPER(c.TaxID) LIKE UPPER(:search_term)"
            ]
            conditions.append(f"({' OR '.join(search_conditions)})")
            parameters['search_term'] = f"%{search_term}%"
        
        # Add status filter
        if status_filter and status_filter != "all":
            status_map = {
                "active": "01",
                "cancelled": "99", 
                "pending": "08"
            }
            if status_filter in status_map:
                conditions.append("p.StatusCode = :status_code")
                parameters['status_code'] = status_map[status_filter]
        
        # Build WHERE clause
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
        
        # Add ordering and limit
        query = f"""
            {base_query}
            {where_clause}
            ORDER BY p.UpdatedGmt DESC
            FETCH FIRST {limit} ROWS ONLY
        """
        
        return query, parameters
    
    @staticmethod
    def get_policy_details(
        policy_guid: Optional[str] = None,
        policy_number: Optional[str] = None
    ) -> tuple[str, Dict[str, Any]]:
        """
        Build query to get detailed policy information
        """
        if not policy_guid and not policy_number:
            raise ValueError("Either policy_guid or policy_number must be provided")
        
        query = f"""
            SELECT 
                p.PolicyGUID as policy_guid,
                p.PolicyNumber as policy_number,
                p.PolicyName as policy_name,
                p.StatusCode as status_code,
                p.PlanDate as plan_date,
                p.IssueStateCode as issue_state,
                p.CreationDate as creation_date,
                p.UpdatedGmt as updated_date,
                -- Client information (primary insured)
                c.ClientGUID as client_guid,
                c.FirstName as client_first_name,
                c.LastName as client_last_name,
                c.CompanyName as company_name,
                c.TaxID as tax_id,
                c.DateOfBirth as date_of_birth,
                c.Sex as gender,
                -- Plan information
                pl.PlanGUID as plan_guid,
                pl.PlanName as plan_name
            FROM {OipaQueryBuilder.POLICY_TABLES}
            LEFT JOIN AsPlan pl ON p.PlanGUID = pl.PlanGUID
        """
        
        parameters = {}
        
        if policy_guid:
            query += " WHERE p.PolicyGUID = :policy_guid"
            parameters['policy_guid'] = policy_guid
        else:
            query += " WHERE p.PolicyNumber = :policy_number"
            parameters['policy_number'] = policy_number
        
        return query, parameters
    
    @staticmethod
    def get_client_portfolio(client_guid: str) -> tuple[str, Dict[str, Any]]:
        """
        Build query to get all policies for a client
        """
        query = f"""
            SELECT 
                p.PolicyGUID as policy_guid,
                p.PolicyNumber as policy_number,
                p.PolicyName as policy_name,
                p.StatusCode as status_code,
                p.PlanDate as plan_date,
                r.RoleCode as role_code,
                r.RolePercent as role_percent
            FROM AsRole r
            JOIN AsPolicy p ON r.PolicyGUID = p.PolicyGUID
            WHERE r.ClientGUID = :client_guid
            ORDER BY p.UpdatedGmt DESC
        """
        
        parameters = {'client_guid': client_guid}
        return query, parameters
    
    @staticmethod
    def count_policies_by_status() -> tuple[str, Dict[str, Any]]:
        """
        Build query to count policies by status
        """
        query = """
            SELECT 
                p.StatusCode as status_code,
                COUNT(*) as policy_count
            FROM AsPolicy p
            GROUP BY p.StatusCode
            ORDER BY policy_count DESC
        """
        
        return query, {}


# Global database instance
oipa_db = OipaDatabase(Config())
