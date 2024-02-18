from simba.mixins.timeseries_features_mixin import TimeseriesFeatureMixin
from simba.mixins.statistics_mixin import Statistics
import inspect, re, os
from docstring_parser import parse
import datetime


def parse_docstring(method: object, cls: object):
    try:
        docstring = inspect.getdoc(method)
        parsed_doc = parse(docstring)
        results = {}
        results['method_name'], results['class_name'] = method.__name__, cls.__name__
        results['file_path'] = inspect.getfile(cls)
        results['author'] = next((line.strip() for line in open(results['file_path']) if line.strip().startswith('__author__')), None).split('=')[-1].strip()
        results['unix_time'] = os.path.getmtime(results['file_path'])
        results['human_time'] = datetime.datetime.utcfromtimestamp(results['unix_time']).strftime('%Y-%m-%dT%H:%M:%SZ')
        note_matches = re.finditer(r'^\s*\.\.\s+note::\s*(.*?)$', docstring, re.MULTILINE | re.DOTALL)
        results['notes'] = [match.group(1).strip() for match in note_matches]
        image_matches = re.finditer(r'^\s*\.\.\s+image::\s*(.*?)$', docstring, re.MULTILINE | re.DOTALL)
        results['images'] = [match.group(1).strip() for match in image_matches]
        equation_matches = re.finditer(r'^\s*\.\.\s+math::\s*(.*?)$', docstring, re.MULTILINE | re.DOTALL)
        results['equations'] = [match.group(1).strip() for match in equation_matches]

        for section in parsed_doc.meta:
            if section.args:
                if section.args[0] == 'param' or section.args[0] == 'parameter':
                    results['parameters'] = {'name': section.arg_name, 'type': section.type_name, 'description': section.description, 'default': section.default}
                elif section.args[0] == 'return' or section.args[0] == 'returns':
                    results['return'] = {'name': section.return_name, 'type': section.type_name, 'description': section.description}
                elif section.args[0] == 'examples' or section.args[0] == 'example':
                    results['examples'] = section.description
                elif section.args[0] == 'reference' or section.args[0] == 'references':
                    results['references'] = section.description
        return results
    except:
        pass

instance = Statistics()
methods = [getattr(instance, method) for method in dir(instance) if callable(getattr(instance, method)) and not method.startswith("_")]
results = []
for method in methods:
    results.append(parse_docstring(method=method, cls=Statistics))