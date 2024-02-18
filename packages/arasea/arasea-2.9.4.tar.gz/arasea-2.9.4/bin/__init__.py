import warnings

warnings.warn(
    message= "Importing 'bin.arasea_cache' is deprecated. Import from "
    "'arasea.bin.arasea_cache' instead.",
    category=DeprecationWarning,
    stacklevel=2,  # Raise the warning on the import line
)
