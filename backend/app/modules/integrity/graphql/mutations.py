import strawberry
from strawberry.types import Info

from app.core.exceptions import AuthorizationError
from app.modules.integrity.graphql.types import (
    MonitoredDirectoryType,
    RegisterDirectoryInput,
    ScanRunType,
)
from app.modules.integrity.service import DirectoryValidationError, IntegrityService


@strawberry.type
class IntegrityMutationError:
    code: str
    message: str


@strawberry.type
class RegisterDirectoryPayload:
    directory: MonitoredDirectoryType | None = None
    error: IntegrityMutationError | None = None


@strawberry.type
class StartScanPayload:
    scan: ScanRunType | None = None
    error: IntegrityMutationError | None = None


@strawberry.type
class IntegrityMutations:
    @strawberry.mutation
    def register_directory(self, info: Info, input: RegisterDirectoryInput) -> RegisterDirectoryPayload:
        try:
            service = IntegrityService(info.context.db)
            directory = service.register_directory(
                name=input.name,
                path=input.path,
                description=input.description,
                recursive=input.recursive,
                scan_frequency=input.scan_frequency,
                included_extensions=input.included_extensions,
                excluded_extensions=input.excluded_extensions,
                excluded_subdirectories=input.excluded_subdirectories,
                max_file_size=input.max_file_size,
            )
        except DirectoryValidationError as error:
            return RegisterDirectoryPayload(error=IntegrityMutationError(code="VALIDATION", message=str(error)))
        except AuthorizationError as error:
            return RegisterDirectoryPayload(error=IntegrityMutationError(code="FORBIDDEN", message=str(error)))
        return RegisterDirectoryPayload(directory=MonitoredDirectoryType.from_model(directory))

    @strawberry.mutation
    def start_integrity_scan(self, info: Info, directory_id: strawberry.ID) -> StartScanPayload:
        try:
            service = IntegrityService(info.context.db)
            scan = service.start_scan(str(directory_id))
        except DirectoryValidationError as error:
            return StartScanPayload(error=IntegrityMutationError(code="VALIDATION", message=str(error)))
        return StartScanPayload(scan=ScanRunType.from_model(scan))
