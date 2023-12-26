import os

from domain.services.elena import get_elena_instance

if __name__ == "__main__":
    elena = get_elena_instance(
        config_manager_class_path="elena.adapters.config.local_config_manager.LocalConfigManager",
        config_manager_url=os.environ.get("ELENA_HOME", os.getcwd()),
    )
    elena.run()
