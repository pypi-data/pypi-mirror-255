from enum import Enum


class WorkspaceGitSyncSettingsIncludeTypeItem(str, Enum):
    APP = "app"
    FLOW = "flow"
    FOLDER = "folder"
    SCRIPT = "script"

    def __str__(self) -> str:
        return str(self.value)
