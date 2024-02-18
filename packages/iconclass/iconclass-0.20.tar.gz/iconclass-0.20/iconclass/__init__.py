import os, re
from typing import Any
from pathlib import Path
from zipfile import ZipFile

__version__ = "0.20"

WITH_NAME_MATCH = re.compile(r"\((?!\.\.\.)[^+]+\)")
BRACKETS = re.compile(r"\([\w ]+?\)")


def split_on_colon(s):
    s = re.sub(r"\(([^)]*):([^)]*)\)", r"(\1__COLON__\2)", s)
    parts = s.split(":")
    parts = [part.replace("__COLON__", ":") for part in parts]
    return parts


class NotationNotFound(Exception):
    pass


class Iconclass:
    def __init__(self):
        data_path = current_dir = Path(__file__).parent / "data.zip"
        if not data_path.exists():
            raise Exception(f"{data_path} not found")
        data_file = ZipFile(data_path)

        self._D = {
            None: {"c": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], "n": None}
        }
        self.texts = {}
        self.keywords = {}
        keys = {}

        for o in data_file.read("keys.txt").decode("utf8").split("\n$"):
            obj = {}
            for line in o.split("\n"):
                tmp = line.split(" ")
                if len(tmp) < 2:
                    continue
                field = tmp[0]
                val = " ".join(tmp[1:])
                if field == "K":
                    obj["k"] = val
                elif field == "S":
                    obj["s"] = [val]
                elif field == ";":
                    obj["s"].append(val)
            suffixes = [s for s in obj.get("s", []) if s.find("q") < 0]
            if suffixes:
                obj["s"] = suffixes
                keys[obj["k"]] = obj

        for o in data_file.read("notations.txt").decode("utf8").split("\n$"):
            obj = {}
            for line in o.split("\n"):
                tmp = line.split(" ")
                if len(tmp) < 2:
                    continue
                field = tmp[0].lower()
                val = " ".join(tmp[1:])
                if field in ("r", "c", "p"):
                    obj[field] = [val]
                    last_field = field
                elif field == ";":
                    obj[last_field].append(val)
                else:
                    obj[field] = val
            if obj:
                k = obj.get("k")
                if k:
                    kk = keys.get(k)
                    if kk:
                        obj["k"] = kk
                    else:
                        del obj["k"]
                self._D[obj["n"]] = obj
        self.pad(self._D[None])

    def get(self, notation):
        raise Exception()  # not yet implemented

    def obj(self, notation):
        if notation == "ICONCLASS" or notation == "":
            return {
                "c": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                "n": "ICONCLASS",
            }

        tmp = notation.split("(+")
        if len(tmp) == 2:
            base, key = tmp
            if key.endswith(")"):
                key = key[:-1]
        else:
            base = tmp[0]
            key = ""

        obj = self._D.get(base)
        if not obj and WITH_NAME_MATCH.search(base):
            notation_with_name = WITH_NAME_MATCH.sub("(...)", base)
            obj = self._D.get(notation_with_name)
            if obj:
                obj = obj.copy()
                base = notation_with_name
                bracketed_text = WITH_NAME_MATCH.search(notation).group()
                obj["notation_with_name"] = notation_with_name
                obj["bracketed_text"] = bracketed_text
                if "c" in obj:
                    obj["c"] = [
                        child.replace("(...)", bracketed_text)
                        for child in obj.get("c", [])
                    ]
        if not obj:
            raise NotationNotFound(notation)

        obj = obj.copy()
        obj["b"] = base
        obj["n"] = notation  # in case there was a key, this sets it again

        obj_key = obj.get("k", {})
        if key and key not in obj_key["s"]:
            raise NotationNotFound(notation)
        if key:
            keys = [
                f'{obj_key["k"]}{k}'
                for k in obj_key.get("s", [])
                if k.startswith(key) and k != key and len(k) == (len(key) + 1)
            ]
            obj["l"] = keys
            obj["k"] = f'{obj_key["k"]}{key}'
            new_path = [f"{obj['p'][-1]}(+{key[: ki + 1]})" for ki in range(len(key))]
            obj["p"] = obj["p"] + new_path
        else:
            keys = [f'{obj_key["k"]}{k}' for k in obj_key.get("s", []) if len(k) == 1]
            obj["l"] = keys
            if "k" in obj:
                del obj["k"]

        return obj

    def text_(self, notation, language="en"):
        obj = self.obj(notation)
        if "b" not in obj:
            return ""
        base_t = self.texts[language].get(obj["b"], "")
        if "bracketed_text" in obj:
            base_t = BRACKETS.sub(obj["bracketed_text"], base_t)
        if "k" in obj:
            t2 = self.texts[language].get(obj["k"], "")
            if t2:
                base_t = f"{base_t} (+ {t2})"
        return base_t

    def txt(self, notation, language="en"):
        if language not in self.texts:
            self.load(language)
        parts = split_on_colon(notation)
        return " : ".join([self.text_(p, language) for p in parts])

    def kw(self, notation, language="en"):
        if language not in self.texts:
            self.load(language)
        obj = self.obj(notation)
        if "b" not in obj:
            return []
        base_kw = self.keywords[language].get(obj["b"], [])
        if "k" in obj:
            base_kw.extend(self.keywords[language].get(obj["k"], []))
        return base_kw

    def load(self, language):
        data_path = current_dir = Path(__file__).parent / f"data_{language}.zip"
        if not data_path.exists():
            raise Exception(f"{data_path} not found")
        data_file = ZipFile(data_path)

        self.texts[language] = {}
        lines = data_file.read(f"txt_{language}.txt").decode("utf8").split("\n")
        for line in lines:
            tmp = line.strip().split("|")
            if len(tmp) != 2:
                continue
            notation, txt = tmp
            self.texts[language][notation] = txt

        self.keywords[language] = {}
        lines = data_file.read(f"kw_{language}.txt").decode("utf8").split("\n")
        for line in lines:
            tmp = line.strip().split("|")
            if len(tmp) != 2:
                continue
            notation, kw = tmp
            self.keywords[language].setdefault(notation, []).append(kw)

    def pad(self, n):
        p = n.get("p", [])
        if n["n"]:
            p.append(n["n"])
        for c in n.get("c", []):
            if c not in self._D:
                print(f"Child {c} not found")
                continue
            kind = self._D[c]
            kind["p"] = p.copy()
            self.pad(kind)


if __name__ == "__main__":
    i = Iconclass()
    print(i.obj("11I62(...)"))
