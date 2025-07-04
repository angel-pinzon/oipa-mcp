"""
Base class for MCP tools

Provides common functionality and patterns for OIPA MCP tools.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ValidationError
from loguru import logger

from ..connectors import oipa_db
from ..config import config


class ToolError(Exception):
    """Base exception for tool errors"""
    pass


class ValidationToolError(ToolError):
    """Raised when tool input validation fails"""
    pass


class DatabaseToolError(ToolError):
    """Raised when database operations fail"""
    pass


class ConfigurationToolError(ToolError):
    """Raised when tool configuration is invalid"""
    pass


class BaseTool(ABC):
    """
    Base class for all OIPA MCP tools
    
    Provides common functionality like input validation, error handling,
    database access, and response formatting.
    """
    
    def __init__(self):
        self.db = oipa_db
        self.config = config
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name (used in MCP protocol)"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description (shown to user)"""
        pass
    
    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON schema for tool input validation"""
        pass
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with given arguments
        
        This method handles validation, execution, and error handling.
        """
        try:
            # Validate input
            validated_args = await self._validate_input(arguments)
            
            # Execute tool logic
            result = await self._execute_impl(validated_args)
            
            # Format response
            return await self._format_response(result)
            
        except ValidationError as e:
            logger.error(f"Validation error in {self.name}: {e}")
            raise ValidationToolError(f"Input validation failed: {e}")
        except DatabaseToolError as e:
            logger.error(f"Database error in {self.name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {self.name}: {e}")
            raise ToolError(f"Tool execution failed: {e}")
    
    async def _validate_input(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input arguments against schema
        
        Override this method for custom validation logic.
        """
        # Basic validation could be added here
        # For now, just return arguments as-is
        return arguments
    
    @abstractmethod
    async def _execute_impl(self, arguments: Dict[str, Any]) -> Any:
        """
        Implement the core tool logic
        
        This method must be implemented by each tool.
        """
        pass
    
    async def _format_response(self, result: Any) -> Dict[str, Any]:
        """
        Format the tool response
        
        Override this method for custom response formatting.
        """
        if isinstance(result, dict):
            return result
        elif isinstance(result, list):
            return {"data": result, "count": len(result)}
        else:
            return {"result": result}
    
    async def _ensure_db_connection(self) -> None:
        """Ensure database connection is available"""
        if not await self.db.test_connection():
            raise DatabaseToolError("Database connection not available")
    
    def _build_error_response(self, error: str, details: Optional[str] = None) -> Dict[str, Any]:
        """Build standardized error response"""
        response = {
            "success": False,
            "error": error
        }
        if details:
            response["details"] = details
        return response
    
    def _build_success_response(
        self, 
        data: Any, 
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build standardized success response"""
        response = {
            "success": True,
            "data": data
        }
        if message:
            response["message"] = message
        if metadata:
            response["metadata"] = metadata
        return response


class QueryTool(BaseTool):
    """
    Base class for tools that execute database queries
    
    Provides common patterns for query-based tools.
    """
    
    async def _execute_query_tool(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None,
        single_result: bool = False
    ) -> Union[List[Dict[str, Any]], Dict[str, Any], None]:
        """
        Execute a database query with error handling
        
        Args:
            query: SQL query string
            parameters: Query parameters
            single_result: If True, return single result instead of list
            
        Returns:
            Query results
        """
        await self._ensure_db_connection()
        
        try:
            if single_result:
                result = await self.db.execute_single_query(query, parameters)
            else:
                result = await self.db.execute_query(query, parameters)
            
            return result
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise DatabaseToolError(f"Database query failed: {e}")


class TransactionTool(BaseTool):
    """
    Base class for tools that execute OIPA transactions
    
    Provides common patterns for transaction-based tools.
    """
    
    async def _build_transaction_xml(
        self, 
        transaction_name: str,
        math_variables: Dict[str, Any],
        effective_date: Optional[str] = None
    ) -> str:
        """
        Build transaction XML for OIPA execution
        
        This is a placeholder - will be implemented when we add
        FileReceived web service support.
        """
        # TODO: Implement XML transaction building
        raise NotImplementedError("Transaction XML building not yet implemented")
    
    async def _execute_transaction(self, transaction_xml: str) -> Dict[str, Any]:
        """
        Execute transaction via FileReceived web service
        
        This is a placeholder - will be implemented when we add
        web service support.
        """
        # TODO: Implement transaction execution
        raise NotImplementedError("Transaction execution not yet implemented")


class AnalyticsTool(BaseTool):
    """
    Base class for analytical tools
    
    Provides common patterns for analytics and reporting tools.
    """
    
    def _calculate_percentage(self, part: int, total: int) -> float:
        """Calculate percentage with division by zero protection"""
        if total == 0:
            return 0.0
        return round((part / total) * 100, 2)
    
    def _format_currency(self, amount: float, currency: str = "USD") -> str:
        """Format currency amounts"""
        return f"{currency} {amount:,.2f}"
    
    def _format_date_range(self, start_date: str, end_date: str) -> str:
        """Format date range for display"""
        return f"{start_date} to {end_date}"
