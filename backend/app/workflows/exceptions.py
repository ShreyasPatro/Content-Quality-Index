"""Custom exceptions for workflow errors."""


class WorkflowError(Exception):
    """Base exception for workflow errors."""

    pass


class InvalidStateError(WorkflowError):
    """Raised when an operation is attempted on an invalid state."""

    pass


class BlogAlreadyApprovedError(InvalidStateError):
    """Raised when attempting to evaluate/rewrite an already approved blog."""

    def __init__(self, blog_id: str, approved_version_id: str):
        self.blog_id = blog_id
        self.approved_version_id = approved_version_id
        super().__init__(
            f"Blog {blog_id} is already approved (version {approved_version_id}). "
            "Cannot evaluate or rewrite approved content."
        )


class VersionNotFoundError(WorkflowError):
    """Raised when a version does not exist."""

    def __init__(self, version_id: str):
        self.version_id = version_id
        super().__init__(f"Version {version_id} not found")


class BlogNotFoundError(WorkflowError):
    """Raised when a blog does not exist."""

    def __init__(self, blog_id: str):
        self.blog_id = blog_id
        super().__init__(f"Blog {blog_id} not found")


class EvaluationAlreadyRunningError(InvalidStateError):
    """Raised when attempting to start evaluation while one is already running."""

    def __init__(self, version_id: str, run_id: str):
        self.version_id = version_id
        self.run_id = run_id
        super().__init__(
            f"Evaluation already running for version {version_id} (run_id={run_id})"
        )


class RewriteCapExceededError(InvalidStateError):
    """Raised when rewrite cap is exceeded."""

    def __init__(self, blog_id: str, current_count: int, max_count: int = 10):
        self.blog_id = blog_id
        self.current_count = current_count
        self.max_count = max_count
        super().__init__(
            f"Blog {blog_id} has exceeded rewrite cap ({current_count}/{max_count})"
        )


class EscalationAlreadyExistsError(InvalidStateError):
    """Raised when attempting to create duplicate escalation."""

    def __init__(self, blog_id: str, escalation_id: str):
        self.blog_id = blog_id
        self.escalation_id = escalation_id
        super().__init__(
            f"Escalation already exists for blog {blog_id} (escalation_id={escalation_id})"
        )
