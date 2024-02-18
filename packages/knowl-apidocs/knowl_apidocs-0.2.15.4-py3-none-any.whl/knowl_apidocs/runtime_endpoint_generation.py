import argparse
import json
import os
import re
import sys
from importlib import import_module

from django.urls import URLPattern, URLResolver


def parse_url(url):
    pattern_path_non_regex = re.compile(r"(?<!\?P)<([^>]+)>")
    pattern_path_regex = re.compile(r"\((.*?)\)")
    pattern_path_curly = re.compile(r"(?<!\?P){([^}]+)}")
    result = {"url": None, "parameter": []}
    matches = re.findall(pattern_path_non_regex, url)
    for match in matches:
        name = match
        dtype = None
        if ":" in match:
            name = match[match.find(":") + 1 :]
            dtype = match[: match.find(":")]
        result["parameter"].append({"name": match.strip(), "pattern": None, "type": dtype})
        url = url.replace(f"<{match}>", "{" + name + "}")
    matches = re.findall(pattern_path_curly, url)
    for match in matches:
        name = match
        dtype = None
        if ":" in match:
            name = match[match.find(":") + 1 :]
            dtype = match[: match.find(":")]
        result["parameter"].append({"name": match.strip(), "pattern": None, "type": dtype})
    matches = re.findall(pattern_path_regex, url)
    for match in matches:
        start = match.find("<")
        end = match.find(">")
        name = match[start + 1 : end]
        pattern = match[end + 1 :]
        dtype = None
        if ":" in name:
            name = name[name.find(":") + 1 :]
            dtype = name[: name.find(":")]
        result["parameter"].append({"name": name.strip(), "pattern": pattern, "type": dtype})
        url = url.replace(f"({match})", "{" + name + "}")
    url = url.replace("^", "").replace("$", "").replace("?", "")
    result["url"] = url
    return result


def get_endpoints(manage_py_path, url_conf, setting_conf):
    try:
        django = import_module("django")
    except ImportError:
        raise ImportError("Django is not installed. Please install django before running this script")
    project_path = os.path.dirname(manage_py_path)
    sys.path.append(project_path)
    os.environ["DJANGO_SETTINGS_MODULE"] = setting_conf
    django.setup()

    try:
        from rest_framework.schemas.generators import EndpointEnumerator
    except ImportError:
        raise ImportError(
            "rest_framework.schemas.generators is not installed. Please install rest_framework.schemas.generators before running this script"
        )

    class EndpointEnumerator(EndpointEnumerator):
        def get_path_from_regex(self, path_regex):
            """
            Given a URL conf regex, return a URI template string.
            """
            # ???: Would it be feasible to adjust this such that we generate the
            # path, plus the kwargs, plus the type from the convertor, such that we
            # could feed that straight into the parameter schema object?
            path = parse_url(path_regex)
            _PATH_PARAMETER_COMPONENT_RE = re.compile(r"<(?:(?P<converter>[^>:]+):)?(?P<parameter>\w+)>")
            # Strip Django 2.0 convertors as they are incompatible with uritemplate format
            path["url"] = re.sub(_PATH_PARAMETER_COMPONENT_RE, r"{\g<parameter>}", path["url"])
            return path

        def endpoint_ordering(self, endpoint):
            path, method, callback = endpoint
            method_priority = {"GET": 0, "POST": 1, "PUT": 2, "PATCH": 3, "DELETE": 4}.get(method, 5)
            return (method_priority,)

        def get_api_endpoints(self, patterns=None, prefix=""):
            """
            Return a list of all available API endpoints by inspecting the URL conf.
            """
            if patterns is None:
                patterns = self.patterns

            api_endpoints = []

            for pattern in patterns:
                path_regex = prefix + str(pattern.pattern)
                if isinstance(pattern, URLPattern):
                    path = self.get_path_from_regex(path_regex)
                    callback = pattern.callback
                    if self.should_include_endpoint(path["url"], callback):
                        for method in self.get_allowed_methods(callback):
                            endpoint = (path, method, callback)
                            api_endpoints.append(endpoint)

                elif isinstance(pattern, URLResolver):
                    nested_endpoints = self.get_api_endpoints(patterns=pattern.url_patterns, prefix=path_regex)
                    api_endpoints.extend(nested_endpoints)

            return sorted(api_endpoints, key=self.endpoint_ordering)

    urlconf = import_module(url_conf)
    endpoint_enumerator = EndpointEnumerator(urlconf=urlconf)
    endpoints = endpoint_enumerator.get_api_endpoints()
    final = []
    for endpoint in endpoints:
        if "actions" in endpoint[2].__dir__():
            final.append(
                {
                    "url": endpoint[0],
                    "is_viewset": True,
                    "method": endpoint[1],
                    "view": endpoint[2].__name__,
                    "path": os.path.join(project_path, endpoint[2].__module__.replace(".", "/") + ".py"),
                    "function": getattr(endpoint[2], "actions")[endpoint[1].lower()],
                }
            )
        else:
            final.append(
                {
                    "url": endpoint[0],
                    "is_viewset": False,
                    "method": endpoint[1],
                    "view": endpoint[2].__name__,
                    "path": os.path.join(project_path, endpoint[2].__module__.replace(".", "/") + ".py"),
                }
            )
    return final


def main(input_dir, result_dir, url_conf, manage_py_path, setting_conf = None):
    if setting_conf is None:
        with open(manage_py_path) as f:
            code = f.read()
            pattern = re.compile(
                r"os\.environ\.setdefault\s*\(\s*[\"|\']DJANGO_SETTINGS_MODULE[\"|\']\s*\,\s*[\"|\'](.+)[\"|\']\s*\)"
            )
            matches = re.findall(pattern, code)
            if matches:
                setting_conf = matches[0]
            else:
                raise Exception("Settings file not found")
    input_path = os.path.abspath(input_dir)
    files_list = []
    for root, dir, files in os.walk(input_path):
        for file in files:
            if file.endswith(".py"):
                files_list.append(os.path.join(root, file))

    manage_py_path = None
    for file_path in files_list:
        if file_path.endswith("manage.py"):
            if manage_py_path is None or len(manage_py_path) > len(file_path):
                manage_py_path = file_path
    endpoints = get_endpoints(manage_py_path, url_conf, setting_conf)
    output = {"endpoints": endpoints}
    output_file_name = "django_endpoints.json"
    output_file_path = os.path.join(result_dir, output_file_name)
    with open(output_file_path, "w") as f:
        json.dump(output, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to bucket files based on the language")
    parser.add_argument("input_dir", type=str, help="Input directory path")
    parser.add_argument("result_dir", type=str, help="Result directory path")
    parser.add_argument("url_conf", type=str, help="URL conf", default=None)
    parser.add_argument("manage_py", type=str, help="manage py path", default=None)
    parser.add_argument("--settings_conf", type=str, help="manage py path", default=None)
    args = parser.parse_args()

    if not os.path.exists(args.input_dir):
        exit(1)

    if not os.path.exists(args.result_dir):
        exit(1)

    main(args.input_dir, args.result_dir, args.url_conf, args.manage_py, args.settings_conf)
