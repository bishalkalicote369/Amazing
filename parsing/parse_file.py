def get_conf(file_name: str):
    config = {}

    try:
        with open(file_name, "r") as file:
            for line in file:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                try:
                    key, value = line.split("=", 1)
                except ValueError:
                    print(f"Invalid line: {line}")
                    return None

                key = key.strip()
                value = value.strip()

                if not key.isupper():
                    print(f"Key should be uppercase: {key}")
                    return None

                if key in ("ENTRY", "EXIT"):
                    try:
                        x, y = map(int, value.split(","))
                        value = (x, y)
                    except ValueError:
                        print(f"Invalid value for {key}: {value}")
                        return None

                elif key in ("WIDTH", "HEIGHT", "SEED"):
                    try:
                        value = int(value)
                    except ValueError:
                        print(f"Invalid value for {key}: {value}")
                        return None

                elif key == "PERFECT":
                    if value not in ("True", "False"):
                        print(f"Invalid value for {key}: {value}")
                        return None

                    value = value == "True"

                config[key] = value

    except FileNotFoundError as error:
        print(error)
        return None
    print(config)
    return config
