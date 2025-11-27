import warnings

# Suppress DeprecationWarning originating from dateutil (e.g., utcfromtimestamp deprecation)
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module=r".*dateutil.*"
)
# Also suppress any DeprecationWarning that mentions utcfromtimestamp specifically
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message=r".*utcfromtimestamp.*"
)
