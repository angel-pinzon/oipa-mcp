"""
Oracle Database connector for OIPA

Handles direct database connections to OIPA Oracle database.
Provides async query execution and connection pooling.

Based on OIPA table structure analysis from documentation.
Uses modern python-oracledb library (no Oracle Client required).
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
    
    Uses python-oracledb (modern replacement for cx_Oracle) which doesn't
    require Oracle Client installation and provides better async support.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self._pool: Optional[oracledb.AsyncConnectionPool] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the async database connection pool"""
        if self._initialized:
            return
            
        try:
            # Handle Cloud Wallet vs Traditional connection
            if self.config.database.is_cloud_wallet:
                await self._initialize_cloud_wallet()
            else:
                await self._initialize_traditional()
                
            self._initialized = True
            logger.info(f"Async database pool initialized: {self.config.database.dsn}")
            logger.info(f"Pool configuration: min={self.config.database.pool_min_size}, max={self.config.database.pool_max_size}")
            
        except oracledb.Error as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def _initialize_cloud_wallet(self) -> None:
        """Initialize connection using Oracle Cloud Wallet"""
        if not self.config.database.wallet_location:
            raise ValueError("OIPA_DB_WALLET_LOCATION is required for Cloud Wallet connection")
        
        logger.info("Initializing Oracle Cloud Wallet connection")
        
        # For Cloud Wallet, we must use thin mode (no Oracle Client)
        logger.info("Using thin mode for Cloud Wallet (no Oracle Client required)")
        
        # Setup environment for auto-login wallet
        self._setup_wallet_environment()
        
        # Create connection pool with Cloud Wallet configuration
        pool_params = {
            'user': self.config.database.username,
            'password': self.config.database.password,
            'dsn': self.config.database.dsn,
            'min': self.config.database.pool_min_size,
            'max': self.config.database.pool_max_size,
            'increment': 1,
            # Cloud Wallet specific configuration
            'config_dir': self.config.database.wallet_location,
            'wallet_location': self.config.database.wallet_location,
            # Enhanced pool configuration
            'ping_interval': 60,  # Test connections every 60 seconds
            'timeout': 30,        # Connection timeout
            'retry_count': 3,     # Retry on connection failures
            'retry_delay': 1      # Delay between retries
        }
        
        # Configure wallet usage
        if self.config.database.wallet_password:
            # Use encrypted wallet with password
            pool_params['wallet_password'] = self.config.database.wallet_password
            logger.info("Using encrypted wallet with password")
        else:
            # Force auto-login wallet usage (cwallet.sso)
            logger.info("Using auto-login wallet (cwallet.sso) without password")
        
        self._pool = oracledb.create_pool_async(**pool_params)
        
        logger.info(f"Cloud Wallet connection initialized from: {self.config.database.wallet_location}")
    
    def _setup_wallet_environment(self) -> None:
        """Setup environment variables for auto-login wallet"""
        import os
        
        wallet_location = self.config.database.wallet_location
        
        # Set TNS_ADMIN to wallet location
        os.environ['TNS_ADMIN'] = wallet_location
        
        # Set WALLET_LOCATION
        os.environ['WALLET_LOCATION'] = wallet_location
        
        # Force use of auto-login wallet by setting ORACLE_WALLET_TYPE
        os.environ['ORACLE_WALLET_TYPE'] = 'SSO'
        
        logger.info(f"Wallet environment configured for auto-login: {wallet_location}")
    
    async def _initialize_traditional(self) -> None:
        """Initialize traditional Oracle connection"""
        logger.info("Initializing traditional Oracle connection")
        
        # Try to initialize Oracle Client for thick mode (optional)
        try:
            oracledb.init_oracle_client()
            logger.info("Using Oracle Client (thick mode) for enhanced performance")
        except Exception:
            logger.info("Using thin mode (pure Python, no Oracle Client required)")
        
        # Create async connection pool
        self._pool = oracledb.create_pool_async(
            user=self.config.database.username,
            password=self.config.database.password,
            dsn=self.config.database.dsn,
            min=self.config.database.pool_min_size,
            max=self.config.database.pool_max_size,
            increment=1,
            # Enhanced pool configuration
            ping_interval=60,  # Test connections every 60 seconds
            timeout=30,        # Connection timeout
            retry_count=3,     # Retry on connection failures
            retry_delay=1      # Delay between retries
        )
    
    async def close(self) -> None:
        """Close the database connection pool"""
        if self._pool:
            await self._pool.close()
            self._pool = None
            self._initialized = False
            logger.info("Database pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get an async database connection from the pool"""
        if not self._initialized:
            await self.initialize()
            
        connection = None
        try:
            # Get async connection from pool
            connection = await self._pool.acquire()
            
            # Set default schema if configured
            if self.config.database.default_schema:
                cursor = connection.cursor()
                try:
                    alter_session_sql = f"ALTER SESSION SET CURRENT_SCHEMA = {self.config.database.default_schema}"
                    await cursor.execute(alter_session_sql)
                    logger.debug(f"Set default schema to: {self.config.database.default_schema}")
                except oracledb.Error as e:
                    logger.warning(f"Failed to set default schema: {e}")
                finally:
                    cursor.close()
            
            yield connection
        except oracledb.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection:
                await self._pool.release(connection)
    
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
            parameters: Query parameters (named parameters recommended)
            fetch_size: Maximum number of rows to fetch
            
        Returns:
            List of dictionaries representing query results
        """
        async with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Set fetch size for better performance
                if fetch_size:
                    cursor.arraysize = min(fetch_size, self.config.performance.max_query_results)
                else:
                    cursor.arraysize = 1000  # Default batch size
                
                # Execute query with parameters
                if parameters:
                    await cursor.execute(query, parameters)
                else:
                    await cursor.execute(query)
                
                # Fetch results
                columns = [col[0].lower() for col in cursor.description]
                rows = await cursor.fetchall()
                
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
    
    async def execute_many(
        self,
        query: str,
        parameters_list: List[Dict[str, Any]]
    ) -> None:
        """
        Execute a query multiple times with different parameters
        Useful for bulk operations
        """
        async with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                await cursor.executemany(query, parameters_list)
                await conn.commit()
                logger.debug(f"Executed batch query {len(parameters_list)} times")
                
            except oracledb.Error as e:
                await conn.rollback()
                logger.error(f"Batch query execution error: {e}")
                raise
            finally:
                cursor.close()
    
    async def test_connection(self) -> bool:
        """Test database connectivity with enhanced diagnostics"""
        try:
            start_time = asyncio.get_event_loop().time()
            result = await self.execute_scalar("SELECT 1 FROM DUAL")
            end_time = asyncio.get_event_loop().time()
            
            if result == 1:
                response_time = (end_time - start_time) * 1000  # Convert to ms
                logger.info(f"Database connection test successful (response time: {response_time:.2f}ms)")
                return True
            else:
                logger.error("Database connection test failed: unexpected result")
                return False
                
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    async def get_pool_status(self) -> Dict[str, Any]:
        """Get current connection pool status for monitoring"""
        if not self._pool:
            return {"status": "not_initialized"}
        
        try:
            return {
                "status": "active",
                "opened": self._pool.opened,
                "busy": self._pool.busy,
                "max_size": self._pool.max,
                "min_size": self._pool.min,
                "increment": self._pool.increment,
                "timeout": self._pool.timeout
            }
        except Exception as e:
            logger.error(f"Failed to get pool status: {e}")
            return {"status": "error", "error": str(e)}


class OipaQueryBuilder:
    """
    Query builder for common OIPA database queries
    
    Provides pre-built, optimized queries for common OIPA operations
    based on the documented table structure.
    """
    
    # Common table joins optimized for OIPA schema
    POLICY_TABLES = """
        AsPolicy p
        LEFT JOIN AsRole r ON p.PolicyGUID = r.PolicyGUID AND r.RoleCode = '01'
        LEFT JOIN AsClient c ON r.ClientGUID = c.ClientGUID
    """
    
    POLICY_PLAN_TABLES = """
        AsPolicy p
        LEFT JOIN AsPlan pl ON p.PlanGUID = pl.PlanGUID
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
        Build optimized query to search policies by various criteria
        
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
        
        # Add search term conditions with case-insensitive search
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
                "pending": "08",
                "suspended": "02"
            }
            if status_filter in status_map:
                conditions.append("p.StatusCode = :status_code")
                parameters['status_code'] = status_map[status_filter]
        
        # Build WHERE clause
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
        
        # Add ordering and limit with Oracle 12c+ syntax
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
        policy_number: Optional[str] = None,
        include_segments: bool = False
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
            FROM {OipaQueryBuilder.POLICY_PLAN_TABLES}
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
                p.UpdatedGmt as updated_date,
                r.RoleCode as role_code,
                r.RolePercent as role_percent,
                pl.PlanName as plan_name
            FROM AsRole r
            JOIN AsPolicy p ON r.PolicyGUID = p.PolicyGUID
            LEFT JOIN AsPlan pl ON p.PlanGUID = pl.PlanGUID
            WHERE r.ClientGUID = :client_guid
            ORDER BY p.UpdatedGmt DESC
        """
        
        parameters = {'client_guid': client_guid}
        return query, parameters
    
    @staticmethod
    def count_policies_by_status() -> tuple[str, Dict[str, Any]]:
        """
        Build optimized query to count policies by status
        """
        query = """
            SELECT 
                p.StatusCode as status_code,
                COUNT(*) as policy_count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
            FROM AsPolicy p
            GROUP BY p.StatusCode
            ORDER BY policy_count DESC
        """
        
        return query, {}
    
    @staticmethod
    def search_clients(
        search_term: Optional[str] = None,
        client_type: Optional[str] = None,
        limit: int = 50
    ) -> tuple[str, Dict[str, Any]]:
        """
        Build query to search clients
        """
        base_query = """
            SELECT 
                c.ClientGUID as client_guid,
                c.FirstName as first_name,
                c.LastName as last_name,
                c.CompanyName as company_name,
                c.TaxID as tax_id,
                c.TypeCode as type_code,
                c.DateOfBirth as date_of_birth,
                c.Email as email,
                c.StatusCode as status_code
            FROM AsClient c
        """
        
        conditions = []
        parameters = {}
        
        if search_term:
            search_conditions = [
                "UPPER(c.FirstName) LIKE UPPER(:search_term)",
                "UPPER(c.LastName) LIKE UPPER(:search_term)",
                "UPPER(c.CompanyName) LIKE UPPER(:search_term)",
                "UPPER(c.TaxID) LIKE UPPER(:search_term)",
                "UPPER(c.Email) LIKE UPPER(:search_term)"
            ]
            conditions.append(f"({' OR '.join(search_conditions)})")
            parameters['search_term'] = f"%{search_term}%"
        
        if client_type:
            conditions.append("c.TypeCode = :client_type")
            parameters['client_type'] = client_type
        
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
        
        query = f"""
            {base_query}
            {where_clause}
            ORDER BY c.LastName, c.FirstName, c.CompanyName
            FETCH FIRST {limit} ROWS ONLY
        """
        
        return query, parameters


# Global database instance
oipa_db = OipaDatabase(Config())
