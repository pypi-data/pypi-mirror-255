from .execution import Execution, ExecutionStepLog


class ILogger:
    """
    logger interface
    """

    def write_log(self, message: str, level: int = 7):
        pass

    def notify_step(self, step_log: ExecutionStepLog):
        pass

    def notify_execution(self, execution: Execution):
        pass
