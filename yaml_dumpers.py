def represent_odict(dumper, instance):
    return dumper.represent_mapping("tag:yaml.org,2002:map", instance.items())


def represent_str(dumper, instance):
    if "\n" in instance:
        return dumper.represent_scalar("tag:yaml.org,2002:str", instance, style="|")
    else:
        return dumper.represent_scalar("tag:yaml.org,2002:str", instance)


def represent_timestamp(dumper, instance):
    return dumper.represent_scalar("tag:yaml.org,2002:str", instance.to_pydatetime().isoformat().split("T")[0].replace("-", "/"))


def represent_none(self, _):
    return self.represent_scalar("tag:yaml.org,2002:null", "")
