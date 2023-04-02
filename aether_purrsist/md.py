import re

# Some of those regexps are from LLazyEmail/markdown-regex

regexp_H3 = re.compile(r'^### (.*)$', re.MULTILINE)
regexp_H2 = re.compile(r'^## (.*)$', re.MULTILINE)
regexp_H1 = re.compile(r'^# (.*$)', re.MULTILINE)
regexp_H = re.compile(r'^#{1,6} (.*)$', re.MULTILINE)

# Underline headings (matches both h1 and h2)
regexp_H_U = re.compile(r'^([\w\s]+)\n(=|\-)+$', re.MULTILINE)

regexp_IMAGE = re.compile(r'!\[([^\[]+)\]\(([^\)]+)\)', re.MULTILINE)
regexp_LINK = re.compile(r'\[([^\[]+)\]\(([^\)]+)\)', re.MULTILINE)
regexp_STRONG = re.compile(r'(\*\*|__)(.*?)(\*?)', re.MULTILINE)
regexp_CODE_B = re.compile(r'```(.*)```', re.MULTILINE)
regexp_CODE_S = re.compile(r'`(.*?)`', re.MULTILINE)


def is_markdown(text: str) -> bool:
    return any(reg.search(text) for reg in [regexp_H,
                                            regexp_H_U,
                                            regexp_IMAGE,
                                            regexp_STRONG,
                                            regexp_CODE_B,
                                            regexp_CODE_S,
                                            regexp_LINK])
