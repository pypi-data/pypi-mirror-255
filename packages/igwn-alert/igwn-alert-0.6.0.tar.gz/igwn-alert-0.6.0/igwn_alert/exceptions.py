from adc.errors import KafkaException


# a generic error object to interact with adc's KafkaException:
class generic_error():
    def __init__(self, code, reason, fatal):
        self.code = code
        self.reason = reason
        self.is_fatal = fatal
        self.is_retriable = not fatal

    def name(self):
        return self.code

    def str(self):
        return self.reason

    def retriable(self):
        return self.is_retriable

    def fatal(self):
        return self.is_fatal


FakeFatalKafkaException = KafkaException(generic_error(
    code=100,
    reason='fake fatal error',
    fatal=True))


FakeNonFatalKafkaException = KafkaException(generic_error(
    code=101,
    reason='fake nonfatal error',
    fatal=False))
