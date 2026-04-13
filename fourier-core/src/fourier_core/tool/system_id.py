def get_machine_id() -> str | None:
    try:
        with open("/etc/machine-id", "r") as f:
            return f.read().strip()
    except Exception:
        return None


if __name__ == "__main__":
    # Example usage
    machine_id = get_machine_id()
    print("Machine ID:", machine_id)
