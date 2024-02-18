def compare_version(_version: str, latest_version: str):
    version_ = _version.strip(".")
    latest_version_ = latest_version.strip(".")
    if len(version_) != len(latest_version_):
        return False
    for i in range(1, len(version_)):
        if version_[i] < latest_version_[i]:
            return False
    return True