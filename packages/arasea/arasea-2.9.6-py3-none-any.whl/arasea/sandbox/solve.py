import warnings


from arasea.tensor.slinalg import solve  # noqa

message = (
    "The module arasea.sandbox.solve will soon be deprecated.\n"
    "Please use tensor.slinalg.solve instead."
)

warnings.warn(message)
