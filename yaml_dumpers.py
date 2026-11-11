# Windows の設定画面などからコピーした文字列には書式制御文字が混ざる。
# 例: Windows の「インストール日」の日付には U+200E (LEFT-TO-RIGHT MARK) が付く。
# 表示されないうえ差分やレビューの妨げになるため、公開データに残さない。
INVISIBLE_CHARS = "\u200b\u200c\u200d\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2060\ufeff"


def remove_invisible(value):
    """書式制御用の不可視文字を取り除く。"""
    if not isinstance(value, str):
        return value
    return value.translate({ord(ch): None for ch in INVISIBLE_CHARS})


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
