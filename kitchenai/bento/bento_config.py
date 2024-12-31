from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from django.apps import AppConfig
from django.conf import settings
import sys

from .types import DependencyType
from .manager import DependencyManager

class BentoBaseConfig(AppConfig, ABC):
    """Abstract base class for Bento configurations.
    
    This class handles dependency injection and lifecycle management for Bento apps.
    Each Bento should subclass this and implement the abstract methods.
    """
    
    def __init__(self, app_name: str, app_module: str, dependency_manager: Optional[DependencyManager] = None):
        """Initialize the Bento config with its dependency manager.
        
        Args:
            app_name: The Django app name
            app_module: The Django app module
        """
        super().__init__(app_name, app_module)
        self.dependency_manager = dependency_manager

    @abstractmethod
    def get_settings_key(self) -> str:
        """Return the settings key for this bento's configuration.
        
        Returns:
            str: The key in Django settings where this bento's config is stored
        """
        pass

    @abstractmethod
    def create_dependencies(self, config: Dict) -> Dict[DependencyType, Any]:
        """Create and return all required dependencies.
        
        Args:
            config: Configuration dictionary from Django settings
            
        Returns:
            Dict[DependencyType, Any]: Mapping of dependency types to instances
        """
        pass

    def _initialize_dependencies(self) -> None:
        """Initialize or update dependencies based on current settings."""
        settings_key = self.get_settings_key()
        config = getattr(settings, settings_key, {})
        
        if not config:
            raise ValueError(f"No configuration found for {settings_key} in Django settings")
        
        # Create all dependencies at once
        dependencies = self.create_dependencies(config)
        
        # Register dependencies with the manager
        for dep_type, dependency in dependencies.items():
            self.dependency_manager.register_dependency(dep_type, dependency)

    def ready(self) -> None:
        """Initialize bento when Django starts.
        
        This method is called by Django when the app is ready.
        It ensures dependencies are initialized before any tasks run.
        """
        print(f"BentoBaseConfig.ready for {self.name}", file=sys.stdout)
        sys.stdout.flush()
        # Reset any existing dependencies
        self.dependency_manager.reset()
        
        # Initialize dependencies from settings
        self._initialize_dependencies()
        
        # Call any additional ready logic in subclasses
        self.on_ready()

    def on_ready(self) -> None:
        """Hook for subclasses to add additional ready logic.
        
        Override this method to perform any additional initialization
        after dependencies are set up.
        """
        pass

    def update_runtime_config(self, **new_settings) -> None:
        """Update configuration at runtime.
        
        Args:
            **new_settings: New configuration values to apply
        """
        settings_key = self.get_settings_key()
        current_config = getattr(settings, settings_key, {})
        current_config.update(new_settings)
        setattr(settings, settings_key, current_config)
        self._initialize_dependencies()

    def get_dependency(self, dep_type: DependencyType) -> Any:
        """Get a dependency by type.
        
        Args:
            dep_type: The type of dependency to retrieve
            
        Returns:
            The requested dependency instance
            
        Raises:
            ValueError: If the dependency isn't registered
        """
        return self.dependency_manager.get_dependency(dep_type) 