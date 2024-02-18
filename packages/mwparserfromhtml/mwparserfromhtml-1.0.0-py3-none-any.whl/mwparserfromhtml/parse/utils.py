from mwparserfromhtml.parse.const import NAMESPACES


def nested_value_extract(key, var):
    """
    function to extract the value of all occurances of a specific key from a nested dictionary
    """
    if hasattr(var, "items"):
        for k, v in var.items():
            if k == key:
                if v != "":
                    yield v
            if isinstance(v, dict):
                for result in nested_value_extract(key, v):
                    if result != "":
                        yield result
            elif isinstance(v, list):
                for d in v:
                    for result in nested_value_extract(key, d):
                        if result != "":
                            yield result


def _check_transclusion(tag_string) -> str:
    """
    Utility for checking if an element is transcluded on the web page.
    """
    if tag_string.has_attr("about") and tag_string["about"].startswith("#mwt"):
        return tag_string["about"]
    return ""


def is_transcluded(tag_string):
    if _check_transclusion(tag_string):
        return True
    for p in tag_string.parents:
        if _check_transclusion(p):
            return True
    return False


def title_normalization(link):
    try:
        # strip everything before the first ":" as a naive way
        # to strip namespace information i.e: "Category" in this case
        return link.split(":", 1)[1].replace("_", " ")
    except Exception:
        return link


def map_namespace(href, wiki_db) -> int:
    """
    returns the namespace id of a namespace type (i.e: article, talks etc.)
    """
    try:
        namespace_type = href.split(":")[0].strip("./").replace("_", " ")
        namespace_id = NAMESPACES[wiki_db][namespace_type]
        return namespace_id
    except Exception:
        return 0
